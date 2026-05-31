from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from datetime import datetime, timezone
import os, jwt, bcrypt, io, base64, requests
from apscheduler.schedulers.background import BackgroundScheduler
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.environ.get("MONGO_URI", "")
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")

client = MongoClient(MONGO_URI) if MONGO_URI else None
db = client["emergency_exit"] if client else None
users_col = db["users"] if db else None
vaults_col = db["vaults"] if db else None


# ─── TIMESTAMP HELPERS ────────────────────────────────────────────────────────

def ms_to_dt(ms):
    """Convert JS millisecond timestamp to Python datetime (UTC)."""
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)

def dt_to_ms(dt):
    """Convert Python datetime to JS millisecond timestamp."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

def now_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


# ─── VAULT SCHEMA HELPERS ─────────────────────────────────────────────────────

def extract_vault_fields(vault_blob: dict) -> dict:
    """Pull top-level scheduling fields out of the vault blob for MongoDB storage."""
    last_checkin_ms = vault_blob.get("lastCheckin")
    return {
        "lastCheckin": ms_to_dt(last_checkin_ms),
        "checkInFrequency": vault_blob.get("fc", 2),
        "checkInUnit": vault_blob.get("fu", "months"),
        "gracePeriodDays": vault_blob.get("gp", 7),
        "notifyProto": vault_blob.get("notifyProto", "ping_then_notify"),
    }

def reconstruct_vault_blob(doc: dict) -> dict:
    """Rebuild the frontend vault blob from a MongoDB vault document."""
    content = doc.get("content", {})
    # Always use explicit None check — empty list [] is falsy and would silently
    # fall through to the old schema if we used `or`.
    kin = content.get("kin")
    contacts = kin if kin is not None else doc.get("vault", {}).get("kin", [])

    assets = content.get("assets")
    assets = assets if assets is not None else doc.get("vault", {}).get("assets", [])

    wishes = content.get("wishes")
    wishes = wishes if wishes is not None else doc.get("vault", {}).get("wishes", [])

    will = content.get("will")
    if will is None:
        will = doc.get("vault", {}).get("will", None)

    supp_docs = content.get("suppDocs")
    supp_docs = supp_docs if supp_docs is not None else doc.get("vault", {}).get("suppDocs", [])

    return {
        "assets": assets,
        "wishes": wishes,
        "will": will,
        "suppDocs": supp_docs,
        "kin": contacts,
        "lastCheckin": dt_to_ms(doc.get("lastCheckin")),
        "fc": doc.get("checkInFrequency", 2),
        "fu": doc.get("checkInUnit", "months"),
        "gp": doc.get("gracePeriodDays", 7),
        "v": content.get("v", "face"),
        "notifyProto": doc.get("notifyProto", "ping_then_notify"),
        "notifySeq": content.get("notifySeq", "in_order"),
        "log": doc.get("log", []),
        "saveCount": content.get("saveCount", 0),
    }


# ─── AUTH HELPERS ─────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str) -> str:
    return jwt.encode({"sub": user_id}, JWT_SECRET, algorithm="HS256")

def clean_user(user: dict) -> dict:
    """Strip sensitive fields before returning user data to the client."""
    return {
        "id": str(user["_id"]),
        "username": user.get("username", ""),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "ageGroup": user.get("ageGroup", ""),
        "hasWill": user.get("hasWill", False),
        "isTester": user.get("isTester", False),
    }

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = users_col.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# ─── OVERDUE CALCULATION ──────────────────────────────────────────────────────

def is_overdue(vault_doc: dict) -> tuple[bool, int]:
    """
    Returns (is_overdue, days_overdue).
    Grace period starts after the check-in window expires.
    """
    last_checkin = vault_doc.get("lastCheckin")
    if not last_checkin:
        return False, 0

    freq = vault_doc.get("checkInFrequency", 2)
    unit = vault_doc.get("checkInUnit", "months")
    grace_days = vault_doc.get("gracePeriodDays", 7)

    interval_days = freq * 30 if unit == "months" else freq * 7
    now = datetime.now(timezone.utc)

    if last_checkin.tzinfo is None:
        last_checkin = last_checkin.replace(tzinfo=timezone.utc)

    due_date = last_checkin + __import__("datetime").timedelta(days=interval_days)
    grace_end = due_date + __import__("datetime").timedelta(days=grace_days)

    if now > grace_end:
        days_overdue = (now - grace_end).days
        return True, days_overdue
    return False, 0


# ─── F60: REMINDER THRESHOLD ─────────────────────────────────────────────────

def is_reminder_due(vault_doc: dict) -> bool:
    """
    Returns True when the vault holder should receive a check-in reminder.

    Logic mirrors the frontend F05 amber banner (25% rule):
    - Calculate the full check-in interval in days
    - A reminder fires when the time remaining until the due date is ≤ 25% of
      the interval (e.g. 2-month interval = ~60 days → reminder at ≤15 days left)
    - Only fires once per cycle — guarded by the `reminderSent` flag on the vault
    - Does NOT fire if the vault is already overdue (the overdue scanner handles that)
    """
    from datetime import timedelta

    last_checkin = vault_doc.get("lastCheckin")
    if not last_checkin:
        return False

    # Already sent this cycle — don't repeat
    if vault_doc.get("reminderSent", False):
        return False

    freq = vault_doc.get("checkInFrequency", 2)
    unit = vault_doc.get("checkInUnit", "months")
    interval_days = freq * 30 if unit == "months" else freq * 7
    threshold_days = max(7, round(interval_days * 0.25))

    now = datetime.now(timezone.utc)
    if last_checkin.tzinfo is None:
        last_checkin = last_checkin.replace(tzinfo=timezone.utc)

    due_date = last_checkin + timedelta(days=interval_days)
    days_remaining = (due_date - now).days

    # In window: reminder threshold reached but not yet overdue
    return 0 <= days_remaining <= threshold_days


# ─── EMAIL DELIVERY ───────────────────────────────────────────────────────────

def get_contacts_to_notify(vault_doc: dict, days_overdue: int) -> list:
    """
    Returns the list of contacts to notify based on the notification protocol
    and how many days overdue the vault is.
    """
    content = vault_doc.get("content", {})
    kin = content.get("kin")
    contacts = kin if kin is not None else []

    if not contacts:
        return []

    proto = vault_doc.get("notifyProto", "ping_then_notify")

    if proto == "ping_then_notify":
        if days_overdue < 3:
            return []  # Still in the "ping the owner" phase
        return contacts

    elif proto == "notify_immediately":
        return contacts

    elif proto == "escalate":
        # One new contact per day overdue
        count = min(days_overdue + 1, len(contacts))
        return contacts[:count]

    return contacts


def send_reminder_email(user: dict, vault_doc: dict):
    """
    F60: Send a warm check-in reminder email to the vault holder themselves.
    Called by the pulse scanner when is_reminder_due() returns True.
    """
    from datetime import timedelta

    freq = vault_doc.get("checkInFrequency", 2)
    unit = vault_doc.get("checkInUnit", "months")
    interval_days = freq * 30 if unit == "months" else freq * 7

    last_checkin = vault_doc.get("lastCheckin")
    if last_checkin and last_checkin.tzinfo is None:
        last_checkin = last_checkin.replace(tzinfo=timezone.utc)

    due_date = last_checkin + timedelta(days=interval_days) if last_checkin else None
    days_remaining = (due_date - datetime.now(timezone.utc)).days if due_date else 0
    days_remaining = max(0, days_remaining)

    recipient_name = user.get("name", "").split()[0] or "there"
    recipient_email = user.get("email", "buat.nonton8282@gmail.com")

    freq_label = f"{freq} {'month' if unit == 'months' else 'week'}{'s' if freq != 1 else ''}"
    due_label = due_date.strftime("%-d %B %Y") if due_date else "soon"
    days_label = f"{days_remaining} day{'s' if days_remaining != 1 else ''}"

    subject = f"Your Emergency Exit check-in is due in {days_label}"

    body = f"""Hi {recipient_name},

Just a gentle reminder that your Emergency Exit check-in is coming up.

Your next check-in is due on {due_label} — that's {days_label} from now.

A quick tap in the app is all it takes to confirm you're okay and reset your timer.

Why this matters: if your check-in is missed and your grace period expires, your nominated contacts will automatically receive your vault — assets, wishes, and personal letters included. This reminder is here so that never happens by accident.

Open Emergency Exit and tap the heart to check in:
https://ramenfanclub.github.io/emergency-exit/

If everything looks different than expected, or you've already checked in, you can safely ignore this email.

Take care,
The Emergency Exit team

---
You're receiving this because you set up a check-in schedule of every {freq_label}.
To change your frequency, open Settings in the app.
"""

    payload = {
        "from": "Emergency Exit <onboarding@resend.dev>",
        "to": [recipient_email],
        "subject": subject,
        "text": body,
    }

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        print(f"F60: Reminder email sent to {recipient_email} ({days_remaining} days remaining)")
        return True
    except Exception as e:
        print(f"F60: Reminder email failed for {recipient_email}: {e}")
        return False


def generate_pdf_for_contact(contact: dict, vault_doc: dict) -> bytes:
    """Generate a PDF package for a single contact. Returns raw bytes."""
    content = vault_doc.get("content", {})

    kin = content.get("kin")
    all_contacts = kin if kin is not None else []

    assets = content.get("assets")
    assets = assets if assets is not None else []

    wishes = content.get("wishes")
    wishes = wishes if wishes is not None else []

    will = content.get("will")
    supp_docs = content.get("suppDocs")
    supp_docs = supp_docs if supp_docs is not None else []

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    story = []

    heading_style = ParagraphStyle("Heading", parent=styles["Heading1"],
                                   fontSize=18, spaceAfter=6, textColor=colors.HexColor("#002147"))
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"],
                               fontSize=10, textColor=colors.HexColor("#54657d"), spaceAfter=12)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
                                fontSize=10, leading=15, spaceAfter=8)
    label_style = ParagraphStyle("Label", parent=styles["Normal"],
                                 fontSize=8, textColor=colors.HexColor("#54657d"),
                                 spaceAfter=2, fontName="Helvetica-Bold")
    section_style = ParagraphStyle("Section", parent=styles["Heading2"],
                                   fontSize=12, spaceAfter=6,
                                   textColor=colors.HexColor("#002147"))

    first = contact.get("first", "")
    last = contact.get("last", "")

    story.append(Paragraph("Emergency Exit", heading_style))
    story.append(Paragraph(f"Prepared for {first} {last}", sub_style))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%-d %B %Y')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Personal Letter", section_style))
    letter = contact.get("letter", "").strip()
    if letter:
        for line in letter.split("\n"):
            story.append(Paragraph(line or "&nbsp;", body_style))
    else:
        story.append(Paragraph("[No personal letter recorded for this contact.]", body_style))
    story.append(Spacer(1, 12))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e0e0e0")))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Will & Legal Documents", section_style))
    if will:
        status_map = {"signed": "Signed & witnessed", "draft": "Draft — not signed", "none": "No Will yet"}
        story.append(Paragraph("Status", label_style))
        story.append(Paragraph(status_map.get(will.get("status", ""), will.get("status", "")), body_style))
        if will.get("solicitor"):
            story.append(Paragraph("Solicitor / Law Firm", label_style))
            story.append(Paragraph(will["solicitor"], body_style))
        if will.get("loc1"):
            story.append(Paragraph("Primary Location", label_style))
            story.append(Paragraph(will["loc1"], body_style))
        if will.get("loc2"):
            story.append(Paragraph("Secondary Location", label_style))
            story.append(Paragraph(will["loc2"], body_style))
        if will.get("notes"):
            story.append(Paragraph("Notes", label_style))
            story.append(Paragraph(will["notes"], body_style))
    else:
        story.append(Paragraph("[No Will details recorded.]", body_style))

    if supp_docs:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Supporting Documents", section_style))
        for supp_doc in supp_docs:
            story.append(Paragraph(supp_doc.get("name", ""), label_style))
            loc = supp_doc.get("loc", "")
            if loc:
                story.append(Paragraph(f"Location: {loc}", body_style))

    if assets:
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e0e0e0")))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Asset Register", section_style))
        for asset in assets:
            story.append(Paragraph(asset.get("name", ""), label_style))
            detail_parts = []
            if asset.get("category"):
                detail_parts.append(asset["category"])
            if asset.get("value"):
                detail_parts.append(f"${round(asset['value']):,}")
            if asset.get("details"):
                detail_parts.append(asset["details"])
            if asset.get("beneficiary"):
                detail_parts.append(f"Beneficiary: {asset['beneficiary']}")
            story.append(Paragraph(" · ".join(detail_parts), body_style))

    if wishes:
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e0e0e0")))
        story.append(Spacer(1, 8))
        story.append(Paragraph("My Wishes", section_style))
        for wish in wishes:
            story.append(Paragraph(wish.get("title", ""), label_style))
            if wish.get("details"):
                story.append(Paragraph(wish["details"], body_style))

    if all_contacts:
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e0e0e0")))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Key Contacts", section_style))
        for c in all_contacts:
            name = f"{c.get('first', '')} {c.get('last', '')}".strip()
            rel = c.get("rel", "")
            email = c.get("email", "")
            phone = c.get("phone", "")
            parts = [x for x in [name, rel, email, phone] if x]
            story.append(Paragraph(" · ".join(parts), body_style))

    doc.build(story)
    return buf.getvalue()


def send_notification_email(contact: dict, vault_doc: dict):
    """Send overdue notification email with PDF attachment to a contact."""
    first = contact.get("first", "")
    last = contact.get("last", "")
    recipient_email = contact.get("email", "buat.nonton8282@gmail.com")

    pdf_bytes = generate_pdf_for_contact(contact, vault_doc)
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

    subject = f"Important: Emergency Exit package for {first} {last}"
    body = f"""Dear {first},

You are receiving this because you have been nominated as a trusted contact in Emergency Exit.

The vault holder has not confirmed their check-in within the required period. Attached is their emergency package — please review it carefully.

This package includes their recorded assets, wishes, Will details, and any personal letters they have written for you.

If you believe this has been sent in error, please disregard this message.

The Emergency Exit team
"""

    payload = {
        "from": "Emergency Exit <onboarding@resend.dev>",
        "to": [recipient_email],
        "subject": subject,
        "text": body,
        "attachments": [
            {
                "filename": f"Emergency-Exit-{first}-{last}.pdf",
                "content": pdf_b64,
            }
        ],
    }

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        print(f"Notification email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Notification email failed for {recipient_email}: {e}")
        return False


def send_allclear_email(contact: dict):
    """Send a warm recovery email to a contact when vault holder checks in after being overdue."""
    first = contact.get("first", "")
    recipient_email = contact.get("email", "buat.nonton8282@gmail.com")

    subject = "All clear — Emergency Exit update"
    body = f"""Dear {first},

Good news — the vault holder has checked in and confirmed they are okay.

Any previous notifications about their Emergency Exit vault can be disregarded. No action is required from you at this time.

Thank you for being a trusted contact.

The Emergency Exit team
"""

    payload = {
        "from": "Emergency Exit <onboarding@resend.dev>",
        "to": [recipient_email],
        "subject": subject,
        "text": body,
    }

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        print(f"All-clear email sent to {first} at {recipient_email}")
        return True
    except Exception as e:
        print(f"All-clear email failed for {first} at {recipient_email}: {e}")
        return False


# ─── PULSE SCANNER ────────────────────────────────────────────────────────────

def run_pulse_scan():
    """
    Hourly scanner. Two responsibilities:
    1. Overdue detection — notifies contacts when grace period has expired
    2. F60: Reminder detection — emails vault holder when check-in is approaching
    """
    print("Pulse scan running...")
    now = datetime.now(timezone.utc)

    for vault_doc in vaults_col.find({}):
        user_id = vault_doc.get("userId")
        if not user_id:
            continue

        user = users_col.find_one({"_id": user_id})
        if not user:
            continue

        overdue, days_overdue = is_overdue(vault_doc)

        # ── Overdue path ─────────────────────────────────────────────────────
        if overdue:
            already_notified = vault_doc.get("overdueNotificationSent", False)
            proto = vault_doc.get("notifyProto", "ping_then_notify")

            if not already_notified or proto == "escalate":
                contacts = get_contacts_to_notify(vault_doc, days_overdue)
                if contacts:
                    for contact in contacts:
                        send_notification_email(contact, vault_doc)
                    if proto != "escalate":
                        vaults_col.update_one(
                            {"_id": vault_doc["_id"]},
                            {"$set": {"overdueNotificationSent": True,
                                      "updatedAt": now}}
                        )
            continue  # Skip reminder check if already overdue

        # ── F60: Reminder path ────────────────────────────────────────────────
        # Only runs when vault is NOT overdue
        if is_reminder_due(vault_doc):
            sent = send_reminder_email(user, vault_doc)
            if sent:
                vaults_col.update_one(
                    {"_id": vault_doc["_id"]},
                    {"$set": {"reminderSent": True, "updatedAt": now}}
                )
                print(f"F60: reminderSent flag set for user {user.get('username', user_id)}")

    print("Pulse scan complete.")


scheduler = BackgroundScheduler()
scheduler.add_job(run_pulse_scan, "interval", hours=1)
scheduler.start()


# ─── API ROUTES ───────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    """Create MongoDB indexes on boot. Safe to run every time — skipped if already exists."""
    vaults_col.create_index([("userId", ASCENDING)], unique=True)
    vaults_col.create_index([("lastCheckin", ASCENDING)])
    vaults_col.create_index([("overdueNotificationSent", ASCENDING),
                             ("lastCheckin", ASCENDING)])
    # F60: index reminderSent so the scanner can efficiently skip already-reminded vaults
    vaults_col.create_index([("reminderSent", ASCENDING), ("lastCheckin", ASCENDING)])
    print("Startup complete — indexes ensured.")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/auth/login")
def login(body: dict):
    username = body.get("username", "").strip().lower()
    password = body.get("password", "")

    user = users_col.find_one({"username": username})
    if not user or not check_password(password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    users_col.update_one({"_id": user["_id"]},
                         {"$set": {"lastLogin": datetime.now(timezone.utc)}})

    token = create_token(str(user["_id"]))
    return {"ok": True, "token": token, "user": clean_user(user)}


@app.get("/auth/me")
def me(current_user: dict = Depends(get_current_user)):
    return {"ok": True, "user": clean_user(current_user)}


@app.get("/admin/testers")
def list_testers(current_user: dict = Depends(get_current_user)):
    testers = list(users_col.find({"isTester": True}))
    return {"ok": True, "testers": [clean_user(t) for t in testers]}


@app.post("/vault/sync")
def vault_sync(body: dict, current_user: dict = Depends(get_current_user)):
    vault_blob = body.get("vault", {})
    fields = extract_vault_fields(vault_blob)

    content = {
        "assets": vault_blob.get("assets", []),
        "wishes": vault_blob.get("wishes", []),
        "will": vault_blob.get("will"),
        "suppDocs": vault_blob.get("suppDocs", []),
        "kin": vault_blob.get("kin", []),
        "v": vault_blob.get("v", "face"),
        "notifySeq": vault_blob.get("notifySeq", "in_order"),
        "saveCount": vault_blob.get("saveCount", 0),
    }

    now = datetime.now(timezone.utc)
    vaults_col.update_one(
        {"userId": current_user["_id"]},
        {"$set": {
            **fields,
            "content": content,
            "log": vault_blob.get("log", [])[-20:],
            "syncedAt": now,
            "updatedAt": now,
        },
         "$setOnInsert": {"createdAt": now, "overdueNotificationSent": False,
                          "reminderSent": False}},
        upsert=True,
    )
    return {"ok": True}


@app.get("/vault")
def vault_get(current_user: dict = Depends(get_current_user)):
    doc = vaults_col.find_one({"userId": current_user["_id"]})
    if not doc:
        return {"ok": True, "vault": None}
    return {"ok": True, "vault": reconstruct_vault_blob(doc)}


@app.post("/checkin")
def checkin(current_user: dict = Depends(get_current_user)):
    """
    Record a check-in. Resets both overdueNotificationSent and reminderSent
    so the next cycle starts fresh.
    """
    now = datetime.now(timezone.utc)

    existing = vaults_col.find_one({"userId": current_user["_id"]})
    was_overdue = existing.get("overdueNotificationSent", False) if existing else False

    vaults_col.update_one(
        {"userId": current_user["_id"]},
        {"$set": {
            "lastCheckin": now,
            "overdueNotificationSent": False,
            "reminderSent": False,   # F60: reset so reminder fires again next cycle
            "updatedAt": now,
        }},
        upsert=True,
    )

    allclear_sent = False
    allclear_count = 0

    if was_overdue and existing:
        content = existing.get("content", {})
        kin = content.get("kin")
        contacts = kin if kin is not None else []
        for contact in contacts:
            if send_allclear_email(contact):
                allclear_count += 1
        allclear_sent = allclear_count > 0

    return {
        "ok": True,
        "checkedIn": True,
        "allclear_sent": allclear_sent,
        "allclear_count": allclear_count,
    }


@app.post("/admin/trigger-pulse")
def trigger_pulse(current_user: dict = Depends(get_current_user)):
    """Manually trigger the pulse scan immediately. For testing."""
    run_pulse_scan()
    return {"ok": True, "message": "Pulse scan triggered"}


@app.post("/admin/force-overdue")
def force_overdue(current_user: dict = Depends(get_current_user)):
    """Set vault lastCheckin to 2020 to simulate an overdue state. For testing."""
    vaults_col.update_one(
        {"userId": current_user["_id"]},
        {"$set": {
            "lastCheckin": datetime(2020, 1, 1, tzinfo=timezone.utc),
            "overdueNotificationSent": False,
            "reminderSent": False,
            "updatedAt": datetime.now(timezone.utc),
        }},
        upsert=True,
    )
    return {"ok": True, "message": "Vault set to overdue state"}


@app.post("/admin/force-reminder")
def force_reminder(current_user: dict = Depends(get_current_user)):
    """
    F60: Set vault lastCheckin so the reminder threshold is triggered next scan.
    Sets lastCheckin to (interval - threshold + 1) days ago, putting the vault
    just inside the reminder window without being overdue.
    For testing only.
    """
    from datetime import timedelta

    vault_doc = vaults_col.find_one({"userId": current_user["_id"]})
    freq = vault_doc.get("checkInFrequency", 2) if vault_doc else 2
    unit = vault_doc.get("checkInUnit", "months") if vault_doc else "months"
    interval_days = freq * 30 if unit == "months" else freq * 7
    threshold_days = max(7, round(interval_days * 0.25))

    # Put lastCheckin so that exactly (threshold_days - 1) days remain until due
    fake_checkin = datetime.now(timezone.utc) - timedelta(days=interval_days - threshold_days + 1)

    vaults_col.update_one(
        {"userId": current_user["_id"]},
        {"$set": {
            "lastCheckin": fake_checkin,
            "reminderSent": False,
            "overdueNotificationSent": False,
            "updatedAt": datetime.now(timezone.utc),
        }},
        upsert=True,
    )
    return {"ok": True, "message": f"Vault set to reminder-due state ({threshold_days - 1} days remaining)"}
