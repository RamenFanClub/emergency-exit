# Emergency Exit — Project Context for Claude

## How to start a new chat

Always begin a new chat with:
1. Upload the current `index.html` from GitHub
2. Say: "We are continuing work on Emergency Exit. Here is the current index.html."
3. Then describe what you want to change

This gives Claude the current state of the app without needing to re-read this entire file.

---

## What is this project?

**Emergency Exit** is a personal digital legacy vault app that helps users prepare for sudden death by recording assets, documenting final wishes, storing Will and legal document details, monitoring liveness via periodic check-ins, and automatically notifying nominated contacts if the user stops responding.

Target market: everyday Australians (non-technical users).

Planned platforms:
- **iOS** (Apple App Store)
- **Android** (Google Play Store)
- **Web** (mobile-optimised browser, currently deployed via GitHub Pages)

---

## Repository & Deployment

- **GitHub:** `https://github.com/RamenFanClub/emergency-exit`
- **Live site:** `https://ramenfanclub.github.io/emergency-exit`
- **Deployment:** Push to `main` branch → GitHub Pages serves from `/ (root)` → live in ~60 seconds
- **Key files:**
  - `index.html` — the entire frontend app (root, served by GitHub Pages)
  - `frontend/index.html` — duplicate kept in sync with root
  - `CLAUDE.md` — this file
  - `docs/` — Technical Blueprint and Feature Register
  - `*-service/` — 7 backend microservice skeletons (not yet implemented)

---

## App Name & Branding

- **App name:** Emergency Exit
- **Design system:** "The Eternal Archive / Aeterna Solid"
- **Tone:** Calm, trustworthy, premium — a "Digital Sanctuary"
- **Primary colour:** `#002147` (deep navy)
- **Accent colour:** `#2d8a7a` (teal)
- **Gradient:** `linear-gradient(135deg, #002147, #003366)`
- **Fonts:** Manrope (headlines, 800 weight) + Public Sans (body)
- **Design rules:**
  - No 1px borders for sectioning — use background colour shifts
  - Minimum tap target: 48×48dp
  - Rounded cards (`border-radius: 16px`)
  - Ambient shadows only
  - No pure black — use `#002147` for dark tones

---

## Tech Stack

### Current (prototype)
- Single-file HTML/CSS/JavaScript (`index.html`)
- localStorage for data persistence (key: `ee_v3`)
- Hosted on GitHub Pages

### Planned (production)
- **Frontend:** React Native (iOS + Android) + React (web)
- **Backend:** Python FastAPI microservices
- **Database:** MongoDB (one DB per service)
- **Message broker:** RabbitMQ (domain events between services)
- **Notifications:** Email (SendGrid), SMS (Twilio), WhatsApp, push
- **Auth:** Biometric (Face ID / Touch ID), PIN, JWT + MFA

---

## App Structure — 5 Screens

### 1. Vault (Dashboard)
- Hero headline: "Your legacy is securely anchored"
- Asset + wish count summary with Active status badge
- **Vitality Pulse** — animated pulsing heart, tap to confirm "Alive & well"
- Next check-in date + days remaining countdown (combined with Vitality Pulse in one card)
- Last confirmed timestamp shown below pulse
- Asset Ledger CTA (full-width gradient button)
- Compact pill buttons: **Add Asset** (navy) + **My Wishes** (grey-blue)
- Vault completeness % with progress bar + actionable tips (8 checks)
- Recent activity log

### 2. Ledger (Asset Register)
- Record New Asset CTA (gradient button)
- Assets grouped by category with icons
- Categories (11): Bank account, Property, Investment, Superannuation, Life insurance, Vehicle, Cryptocurrency, Business, Personal item, Digital account, Other
- Per asset: name, category, estimated value, details (free-text), beneficiary, notes
- Delete button per asset
- Legacy completeness % shown in info box

### 3. My Wishes
- New Instruction CTA (dark gradient card with START NOW button)
- **Will & Legal Documents** section (always at top):
  - Will status badge: Not recorded / Draft / Signed & witnessed
  - Will details: status, date signed, solicitor, primary location, secondary location, notes
  - Supplementary Documents list with delete per item
  - Attach document button
- **Statement of Wishes prompt** (orange accent card — prominent nudge):
  - Shows when Statement of Wishes has NOT been recorded
  - Transforms to green confirmation card when recorded, showing storage location
  - Tapping opens Attach Document modal with "Statement of Wishes" pre-selected
- **Wishes grouped by category** (like Ledger):
  - Shows only categories that have at least one wish
  - Each wish: title, details preview, priority badge (high/medium/low), edit + delete
  - Edit opens modal pre-filled with existing data
- Wish categories (9): Funeral & Service, Medical / end of life care, Guardian for children, Pet care, Business succession, Digital accounts, Personal message, Charitable giving, Other
- Wish form fields: Category, Wish, Details, Priority

### 4. Contact
- Title: "Contacts", subtitle: "People to notify and how to reach them"
- Section: "My Contacts" with Add Contact button
- Contact cards showing:
  - Initials avatar (navy gradient)
  - Full name + relationship
  - Access level badge (Executor / Full / Wishes)
  - Notify via icon + label (Email / SMS / WhatsApp / Email+SMS)
  - Sequence number (#1, #2...) with up/down arrows to reorder
  - Remove button
- Add Contact modal fields: First name, Last name, Relationship, Email, Phone, Notify via, Access level

### 5. Settings
- **Check-in Frequency** — stepper (1–24 Weeks or Months)
- **Grace Period** — stepper in days (1–30 days, default 3)
- **Notification Protocol** — 3 radio options:
  - "Ping me first, then notify contacts" (default)
  - "Notify contacts immediately"
  - "Escalate gradually" (notify first contact, wait 24h, then next)
- **Verification** — FaceID/Biometrics or Secure Passcode
- Info box: "Missed check-ins after X days will grant access to N contacts"
- Confirm Settings button

---

## Navigation

Bottom tab bar (5 tabs, rounded top corners):

| Tab | Icon | Screen |
|-----|------|--------|
| Vault | `shield` | Dashboard |
| Ledger | `account_balance` | Asset Register |
| Wishes | `auto_stories` | My Wishes |
| Contact | `family_history` | Contacts |
| Settings | `settings_suggest` | Settings |

Active tab: white icon/label on navy pill. Inactive: navy at 35% opacity.

---

## Key UI Patterns

- **Modals:** Bottom-sheet, drag handle at top, tap outside to dismiss
- **Gradient buttons:** Full-width, 18px padding, 3px border-bottom for depth, active scale(0.97)
- **Compact action buttons:** Pill-shaped, side by side, 10px vertical padding
- **Cards:** `border-radius: 16px`, `#f2f4f6` or white with ambient shadow
- **Tags/badges:** Uppercase, 10px, pill-shaped
- **Toast notifications:** Fixed, centred, navy pill, auto-dismiss 2.4s
- **Stepper controls:** − value + (used for frequency and grace period)
- **Icons:** Google Material Symbols Outlined

---

## Data Model

```javascript
// localStorage key: 'ee_v3'
{
  assets: [{
    id: timestamp, name: string, category: string,
    value: number, details: string, beneficiary: string, notes: string
  }],
  wishes: [{
    id: timestamp, category: string, title: string,
    details: string, priority: 'high' | 'medium' | 'low'
  }],
  will: {
    status: 'signed' | 'draft' | 'none',
    date: string, solicitor: string,
    loc1: string, loc2: string, notes: string
  } | null,
  suppDocs: [{
    id: timestamp,
    type: 'Statement of Wishes' | 'Enduring Power of Attorney' |
          'Advance Health Directive' | 'Guardianship Nomination' |
          'Funeral Pre-arrangement' | 'Business Succession Plan' | 'Other',
    name: string, loc: string, notes: string
  }],
  kin: [{
    id: timestamp, first: string, last: string, rel: string,
    email: string, phone: string,
    notifyVia: 'email' | 'sms' | 'whatsapp' | 'email_and_sms',
    access: 'executor' | 'full' | 'wishes',
    order: number
  }],
  lastCheckin: timestamp | null,
  fc: number,               // frequency count (1–24)
  fu: 'weeks' | 'months',
  gp: number,               // grace period in DAYS (1–30, default 3)
  v: 'face' | 'pin',
  notifyProto: 'ping_then_notify' | 'notify_immediately' | 'escalate',
  log: [{ msg: string, time: string }]
}
```

---

## Completeness Score — 8 Checks (~12.5% each)

1. At least one asset recorded
2. At least one asset has a beneficiary assigned
3. At least one wish recorded
4. Will details recorded
5. Statement of Wishes recorded (suppDocs includes type === 'Statement of Wishes')
6. At least one contact added
7. At least one contact has access level "executor"
8. First check-in completed

---

## Contact Notification — Emergency Exit Package

When the grace period expires, contacts receive a self-contained package. No app, no login required.

**What they receive:**

1. **Notification message** (via email/SMS/WhatsApp) — warm tone, explains the situation
2. **Personal letter** — written by the user for this specific contact, embedded in email body
3. **Emergency Exit PDF** — attached to the email, works offline, can be printed

**PDF sections** (filtered by contact's access level):
- Personal message from the user
- Action checklist (auto-generated from vault data)
- Will & legal documents (solicitor, locations, supplementary docs)
- Asset register (Executor sees account details; Full sees names/values; Wishes-only skips this)
- Wishes grouped by category with priority flags
- Key people to contact (other contacts + solicitor)

**Statement of Wishes** is referenced prominently — contacts are told where to find the user's detailed step-by-step instructions.

**Design principle:** PDF works offline. Watermarked with contact name + date. Does not depend on Emergency Exit servers staying online.

---

## Terminology — Always Use These Words

| Use | Never use |
|-----|-----------|
| Contact | Guardian, Kin, Trusted Kin |
| My Contacts | Circle of Trust |
| Settings | Config, Configuration |
| My Wishes | Legacy Wishes |
| Wish (field label) | Title |
| Alive & well (check-in label) | I'm Alive |
| Contact (nav tab) | Kin |
| Settings (nav tab) | Config |

---

## Microservices Architecture (Skeleton — Phase 2+)

| Service | Port | Database |
|---------|------|----------|
| api-gateway | 8000 | — |
| identity-service | 8001 | ee_identity |
| vault-service | 8002 | ee_vault |
| wishes-service | 8003 | ee_wishes |
| guardian-service | 8004 | ee_guardian |
| pulse-service | 8005 | ee_pulse |
| notification-service | 8006 | — |

CI is running but tests fail (expected — services are skeleton only, not yet implemented).

---

## Coding Conventions

- CSS variables for all colours (`--p`, `--ac`, `--sec`, etc.)
- Short class names (`.scr`, `.ni`, `.mo`, `.fi`) to keep file size small
- Mobile-first — max-width 430px, touch targets min 48px
- State loading: `S={...S,...parsed}` to safely merge new default fields
- Monetary values: always `Math.round().toLocaleString()` — never raw floats
- localStorage key is `ee_v3` (not ee_v2)
- When editing index.html, always update BOTH `./index.html` AND `./frontend/index.html`

---

## What NOT to Do

- Do not use Inter, Roboto, or Arial — always Manrope + Public Sans
- Do not use pure black — use `#002147`
- Do not use the old terminology (Guardian, Kin, Config, Legacy Wishes, Circle of Trust)
- Do not use "Title" as the wish field label — use "Wish"
- Do not use separate location/ref fields for assets — single "Details" textarea
- Do not render monetary values as raw floats
- Do not forget to update BOTH index.html files (root and `frontend/`)
- Do not use grace period in hours — it is in days
- Do not use `ee_v2` as localStorage key — it is `ee_v3`
- Do not remove the Statement of Wishes prompt — it is a key UX nudge

---

## End-of-Chat Checklist

- [ ] Download the new `index.html`
- [ ] Did anything structural change? Update `CLAUDE.md`
- [ ] Replace files in VS Code (`./index.html` AND `./frontend/index.html`)
- [ ] `git add -A`
- [ ] `git commit -m "describe what changed"`
- [ ] `git push`
