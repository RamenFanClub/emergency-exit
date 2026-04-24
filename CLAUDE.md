# Emergency Exit — Project Context for Claude

## How to start a new chat

This project is connected to the `RamenFanClub/emergency-exit` GitHub repo. `CLAUDE.md` and `index.html` are synced at the project level, so Claude can read them automatically at the start of every chat — no need to upload files manually.

To start a new chat:
1. Open a new chat inside this Claude Project
2. Simply describe what you want to change or build
3. Claude will read the latest `CLAUDE.md` and `index.html` from the GitHub sync

**Important:** Always push your changes to `main` after each session. The GitHub sync reflects whatever is on `main` — if you don't push, the next chat will be working from outdated files.

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
- jsPDF (via CDN) for client-side PDF generation
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

### 1. Home (Dashboard)
- Hero headline: "Your legacy is securely anchored"
- Asset + wish count summary with Active status badge
- **Vitality Pulse** — animated pulsing heart, tap to confirm "Alive & well"
- Next check-in date + days remaining countdown (combined with Vitality Pulse in one card)
- Last confirmed timestamp shown below pulse
- Asset Ledger CTA (full-width gradient button)
- Compact pill buttons: **Add Asset** (navy) + **My Wishes** (grey-blue)
- Home completeness % with progress bar + actionable tips (7 checks)
- Recent activity log
- Screen ID: `s-home` | Nav ID: `n-home`

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
  - Attach document button (`.ob` style in section header)
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
- Section: "My Contacts" with Add Contact button (`.ob` style in section header)
- Contact cards showing:
  - Initials avatar (navy gradient)
  - Full name + relationship
  - **Letter status pill** — teal "Letter written" badge or orange "No letter yet" badge
  - Notify via icon + label (Email / SMS / WhatsApp / Email+SMS)
  - Sequence number (#1, #2...) with up/down arrows to reorder
  - Remove button
  - **"Write personal letter" / "Edit personal letter" button** — teal-tinted, opens letter modal
  - **"Preview what [Name] will receive" button** — generates and downloads a per-contact PDF package
- Add Contact modal fields: First name, Last name, Relationship, Email, Phone, Notify via
- **All contacts receive the full package — there are no access level tiers**

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

| Tab | Icon | Screen ID | Nav ID |
|-----|------|-----------|--------|
| Home | `shield` | `s-home` | `n-home` |
| Ledger | `account_balance` | `s-ledger` | `n-ledger` |
| Wishes | `auto_stories` | `s-wishes` | `n-wishes` |
| Contact | `family_history` | `s-kin` | `n-kin` |
| Settings | `settings_suggest` | `s-config` | `n-config` |

Active tab: white icon/label on navy pill. Inactive: navy at 35% opacity.

---

## Key UI Patterns

- **Modals:** Bottom-sheet, drag handle at top, tap outside to dismiss
- **Gradient buttons:** Full-width, 18px padding, 3px border-bottom for depth, active scale(0.97)
- **Compact action buttons:** Pill-shaped, side by side, 10px vertical padding
- **Cards:** `border-radius: 16px`, `#f2f4f6` or white with ambient shadow
- **Card background rule (F27):** `.cardw` (white + shadow) = interactive or primary sections. `.card` (grey) = informational or contextual grouping containers. Never mix these up.
- **Secondary add-action buttons (F26):** All "add" actions in section headers use `.ob` style (navy outlined pill). The only exceptions are the Home screen quick-action pills (`.qb`) which are primary actions, not section header adds.
- **Tags/badges:** Uppercase, 10px, pill-shaped
- **Toast notifications:** Fixed, centred, navy pill, auto-dismiss 2.4s
- **Stepper controls:** − value + (used for frequency and grace period)
- **Icons:** Google Material Symbols Outlined
- **Letter button:** Teal-tinted outlined style (`.letter-btn`), changes label to "Edit" once a letter exists
- **Letter status pill:** Teal "Letter written" or orange "No letter yet" — rendered inside the contact card header row
- **Preview button:** Outlined style (navy border, near-transparent background) at the bottom of each contact card

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
    order: number,
    letter: string   // F03: personal letter written by vault owner for this contact (may be empty string)
    // Note: no access field — all contacts receive the full package
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

## Completeness Score — 7 Checks (~14.3% each)

1. At least one asset recorded
2. At least one asset has a beneficiary assigned
3. At least one wish recorded
4. Will details recorded
5. Statement of Wishes recorded (suppDocs includes type === 'Statement of Wishes')
6. At least one contact added
7. First check-in completed

---

## Contact Notification — Emergency Exit Package

When the grace period expires, contacts receive a self-contained package. No app, no login required.

**What they receive:**

1. **Notification message** (via email/SMS/WhatsApp) — warm tone, explains the situation
2. **Personal letter** — written by the user for this specific contact, embedded in email body
3. **Emergency Exit PDF** — attached to the email, works offline, can be printed

**PDF structure (6 pages, generated client-side via jsPDF):**
- **Page 1 — Cover:** Contact's name, generation date, intro note, personal letter (rendered in italic with teal accent if written; placeholder text if not yet written)
- **Page 2 — Action Checklist:** Auto-generated steps from vault data (solicitor, Will location, Statement of Wishes location)
- **Page 3 — Will & Legal Documents:** Will details + all supplementary documents
- **Page 4 — Asset Register:** All assets grouped by category, full detail (name, value, details, beneficiary)
- **Page 5 — My Wishes:** All wishes grouped by category with priority badges
- **Page 6 — Key Contacts:** All contacts with name, relationship, email, phone
- **Footer on every page:** Contact name + page numbers

**All contacts receive the full package — there are no access level tiers.**

**Statement of Wishes** is referenced prominently — contacts are told where to find the user's detailed step-by-step instructions.

**Design principle:** PDF works offline. Does not depend on Emergency Exit servers staying online.

**Preview feature (F17):** The vault owner can tap "Preview what [Name] will receive" on any contact card to generate and download the PDF immediately.

**Personal letter feature (F03):** Each contact can have a unique personal letter written by the vault owner. The letter appears on Page 1 of their PDF package, rendered in italic with a teal left-accent bar. If no letter is written, the placeholder copy remains. Contact cards show a status pill: teal "Letter written" or orange "No letter yet". The write/edit button is teal-tinted to signal emotional significance.

---

## Modals

| ID | Purpose |
|----|---------|
| `am` | Add Asset |
| `wm` | Add / Edit Wish |
| `wlm` | Will Details |
| `sdm` | Attach Supplementary Document |
| `km` | Add Contact |
| `lm` | Write / Edit Personal Letter (F03) — fields: `#lm-kin-id` (hidden, stores contact id), `#lt` (textarea) |

---

## Terminology — Always Use These Words

| Use | Never use |
|-----|-----------|
| Home | Vault |
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
- Home screen uses `id="s-home"` and nav uses `id="n-home"`
- When editing index.html, always update BOTH `./index.html` AND `./frontend/index.html`
- jsPDF loaded via CDN in `<head>` — access via `window.jspdf.jsPDF`
- New contacts are initialised with `letter: ''` so the field is always present

---

## What NOT to Do

- Do not use Inter, Roboto, or Arial — always Manrope + Public Sans
- Do not use pure black — use `#002147`
- Do not use the old terminology (Vault, Guardian, Kin, Config, Legacy Wishes, Circle of Trust)
- Do not use "Title" as the wish field label — use "Wish"
- Do not use separate location/ref fields for assets — single "Details" textarea
- Do not render monetary values as raw floats
- Do not forget to update BOTH index.html files (root and `frontend/`)
- Do not use grace period in hours — it is in days
- Do not use `ee_v2` as localStorage key — it is `ee_v3`
- Do not remove the Statement of Wishes prompt — it is a key UX nudge
- Do not use `s-vault` or `n-vault` as element IDs — they are now `s-home` and `n-home`
- **Do not reintroduce contact access levels (Executor / Full / Wishes only) — deliberately removed. All contacts receive the full package.**
- Do not remove the personal letter prompt from the letter modal — it sets the right emotional tone for users
- Do not use `.cardw` for informational/contextual containers — use `.card` (grey). `.cardw` is reserved for interactive or primary content only (F27).
- Do not use non-`.ob` styles for secondary add-action buttons in section headers (F26). The only exception is the Home screen quick-action pills (`.qb`).

---

## Feature Backlog — User Stories

Features are prioritised using MoSCoW: **Must** (ship or the product doesn't work), **Should** (high value, planned soon), **Could** (nice-to-have, future), **Won't** (out of scope for now).

Status key: `idea` → `specified` → `in-progress` → `done`

### Must Have — Core Product Loop

These features complete the vault → heartbeat → delivery loop. Without them, Emergency Exit is just another document vault.

| ID | User Story | Priority | Status | Notes |
|----|-----------|----------|--------|-------|
| F01 | As a user, I want the app to automatically notify my contacts if I miss a check-in and the grace period expires, so that my loved ones are alerted without relying on someone else to act. | Must | idea | This is the #1 differentiator. Requires backend (notification-service). |
| F02 | As a contact, I want to receive a self-contained PDF with the user's assets, wishes, and legal document locations, so I can act immediately without needing an app or login. | Must | done | All contacts receive the full package — no access level tiers. 6-page A4 PDF generated client-side via jsPDF. Preview button on each contact card ("Preview what [Name] will receive"). Also delivers F17. |
| F03 | As a user, I want to write a personal letter for each contact that is included in their notification, so they receive a human message alongside the practical information. | Must | done | Letter stored as `k.letter` (string) on each contact object. Letter modal (`#lm`) with warm UX prompt. Status pill on contact card (teal "Letter written" / orange "No letter yet"). Letter button changes label to "Edit" once written. PDF Page 1 renders actual letter text in italic with teal accent bar; placeholder copy shown if not yet written. |
| F04 | As a user, I want my data encrypted at rest and in transit, so that sensitive financial and legal information is protected from unauthorised access. | Must | idea | Current prototype uses plain localStorage. Production needs AES-256 or equivalent. |
| F05 | As a user, I want to receive reminders (push notification, email, or SMS) when my check-in is due, so I don't accidentally miss one and trigger a false alarm. | Must | idea | Critical for preventing false positives. Configurable reminder frequency. |

### Should Have — High Value, Near-Term

| ID | User Story | Priority | Status | Notes |
|----|-----------|----------|--------|-------|
| F06 | As a user, I want to test the notification flow with a "dry run" that sends a sample email to myself or a chosen contact, so I can verify everything works before it's needed for real. | Should | idea | Builds user trust. Reduces anxiety about "will this actually work?" |
| F07 | As a user, I want a guided onboarding flow that walks me through the most important setup steps on first use, so I don't feel overwhelmed by the number of sections. | Should | idea | Completeness score already nudges — but first-time UX needs more hand-holding. |
| F08 | As a user, I want to export or back up my vault data to a file I control, so I'm not entirely dependent on Emergency Exit's servers or storage. | Should | idea | JSON or encrypted export. Aligns with "your data, your control" philosophy. |
| F09 | As a user, I want an auto-generated action checklist in the PDF delivery package that tells my contacts what to do first, second, third, so they aren't overwhelmed by raw data. | Should | done | Implemented as part of F02. Page 2 of the PDF is an auto-generated checklist built from vault data. |
| F10 | As a user, I want to record my digital accounts (email, social media, subscriptions) and what should happen to each one, so my contacts can close or transfer them. | Should | idea | Separate from financial assets. Inspired by GoodTrust's account closure feature. |
| F11 | As a contact receiving a notification, I want to see a clear explanation of what Emergency Exit is and why I'm receiving this message, so I understand the context without confusion or alarm. | Should | idea | Warm, human-toned message. Not robotic. First impression matters enormously. |
| F19 | As a user, I want the app to passively detect that I'm alive based on phone activity (unlocks, movement, app usage), so I don't have to manually check in every time. | Should | idea | Reduces check-in fatigue — the #1 engagement risk. Manual check-in becomes fallback. Requires native mobile APIs (iOS/Android), not possible in browser-only prototype. |
| F20 | As a user, I want the app to capture only the minimum information my contacts need to locate an asset (e.g. "ANZ Savings Account" not full BSB/account numbers), so I feel safe using the app without exposing sensitive financial details. | Should | idea | Design philosophy: Emergency Exit is a *map*, not a *copy*. Reduces security liability, lowers encryption burden, increases user trust. Revisit asset form fields and placeholder text. |
| F21 | As a user, I want to record where my documents are stored (e.g. "solicitor's office", "Google Drive") rather than uploading them, so the app uses minimal storage and I don't duplicate sensitive files. | Should | idea | App already does this partially via suppDocs location field. Formalise as primary approach. Position as "your documents stay where they are — we just tell people where to look." |

### Could Have — Future Value

| ID | User Story | Priority | Status | Notes |
|----|-----------|----------|--------|-------|
| F12 | As a user, I want to generate a physical Emergency Access Card (QR code) that I can store in my wallet or safe, so my contacts have a backup way to access my vault if digital notifications fail. | Could | idea | Inspired by Evaheld's QR card. Good offline redundancy. |
| F13 | As a user, I want to record an Advance Care Directive within the app, so my medical wishes are stored alongside my other legacy documents. | Could | idea | Relevant for Australian market. Evaheld already does this well — consider whether to compete or integrate. |
| F14 | As a user, I want the app to remind me periodically (e.g. every 6 months) to review and update my vault data, so my information stays current as my life changes. | Could | idea | Separate from check-in reminders. "Life audit" nudge — new baby, moved house, etc. |
| F15 | As a user, I want to nominate a backup check-in method (e.g. if I don't respond to push notifications, try SMS, then email), so the system has multiple ways to reach me before alerting contacts. | Could | idea | Reduces false alarms. Escalation ladder for the user, not just contacts. |
| F16 | As a user, I want to record video or audio messages for my contacts, so they receive something more personal than text. | Could | idea | Emotional value is high. Storage and delivery complexity is also high. Consider post-MVP. |
| F17 | As a user, I want to see a "What my contacts will receive" preview screen, so I can verify the output before it's ever needed. | Could | done | Delivered as part of F02. "Preview what [Name] will receive" button on each contact card. |
| F18 | As a user, I want to grant a trusted person "vault editor" access so they can help me fill in details (e.g. elderly parent's adult child helping set up), so the app works for people who aren't comfortable doing it alone. | Could | idea | Delegate setup use case. Common in aged care context. |

### UX Improvements — Consistency, Tone & Journey

These features address UX audit findings: visual consistency, tone of voice, empty states, and user journey friction.

| ID | User Story | Priority | Status | Notes |
|----|-----------|----------|--------|-------|
| F22 | As a user, I want the primary CTA on every screen to use the same visual pattern (gradient button), so the app feels consistent and I always know where to tap first. | Must | done | New Instruction on Wishes now uses `.gbtn` with `edit_note` icon, matching Asset Ledger pattern. Subtitle updated to "Record something you'd like carried out". |
| F23 | As a first-time user, I want encouraging empty states with a clear next step and warm copy, so I feel guided rather than confronted by blank screens. | Must | done | Warm empty states with icon, headline, encouraging sub-text, and CTA button added to Ledger, Wishes, and Contacts. Uses `.empty-state` CSS class. |
| F24 | As a user, I want all screen subtitles and headlines to use calm, grounded language instead of marketing-speak, so the app feels like a trusted guide rather than a sales pitch. | Must | done | Rewrites applied: Home hero → "Everything is in order." / Ledger → "A record of what you have, so the right people know where to find it." / Wishes → "What matters to you, written down so it's not forgotten." / Settings → "Set how often you check in and what happens if you don't." / Check-in label → "TAP TO CHECK IN". / Record New Asset subtitle → "Add anything your people should know about". / `.ps` bumped to 15px/500wt. |
| F25 | As a user, I want to edit my assets and contacts (not just delete and re-add), so I can fix mistakes without losing data. | Must | done | `editA()` and `editK()` functions added. Asset and contact modals now support both Add and Edit modes (hidden `*-edit-id` field, dynamic title/button text). Edit icons added to asset rows and contact cards. Existing data preserved on edit (contact order and letter kept). |
| F26 | As a user, I want the "add" action on every screen to follow the same visual pattern, so I don't have to re-learn the interface on each tab. | Should | done | All secondary add-actions in section headers now use `.ob` style (navy outlined pill button). Supp docs "Attach" button moved into section header as `.ob`. Home quick-action pills (`.qb`) deliberately preserved — they are primary Home actions, not section header adds. |
| F27 | As a user, I want card backgrounds (grey vs white) to follow a clear visual rule, so the screen hierarchy makes sense at a glance. | Should | done | Rule enforced across all screens: `.cardw` (white + shadow) = interactive or primary sections; `.card` (grey) = informational or contextual grouping containers. Rule also documented in Key UI Patterns and What NOT to Do sections of this file. |
| F28 | As a user, I want section headers to follow a consistent layout pattern across all screens, so the app feels cohesive. | Should | done | Home activity header changed from text-link to `.ob` button. All section headers now use `.sh` row with consistent left/right elements. |
| F29 | As a user, I want to see my contacts' email and phone number on their card, so I can verify the details are correct without opening anything. | Should | done | Compact email and phone lines added below notification method on contact cards, with mail/phone icons and text overflow handling. |
| F30 | As a user, I want the Vitality Pulse to be less prominent until I've set up my vault, so I'm guided toward adding content first rather than checking in to an empty vault. | Should | specified | De-emphasise pulse when completeness < 40%. Promote completeness card + top tip as the primary Home element for new users. |
| F31 | As a user, I want a brief privacy note on the Home screen or Settings, so I feel confident about where my sensitive data is stored. | Should | specified | Add: "Your information is stored on this device only. It never leaves your phone unless you choose to share it." Update when backend launches. |
| F32 | As a user, I want the Statement of Wishes nudge to include a brief plain-language explanation of what it is (and how it differs from a Will), so I understand why it matters. | Should | specified | Add clarifying sentence: "A Statement of Wishes is a plain-language document — separate from your Will — that tells your people exactly what to do and where to find everything." |
| F33 | As a user, I want the check-in label to say "Tap to check in" instead of "TAP TO CONFIRM", so it feels like a gentle habit rather than a transactional confirmation. | Should | done | Micro-label on Vitality Pulse changed to "TAP TO CHECK IN". |
| F34 | As a user, I want all delete actions across the app to look and behave the same way, so destructive actions are predictable. | Could | specified | Currently: assets use icon only, contacts use text + icon ("Remove"), docs use icon only. Standardise to icon-only, same size and colour everywhere. |
| F35 | As a user, I want Settings to auto-save all changes consistently (not a mix of auto-save and manual confirm), so I don't wonder whether my changes were saved. | Could | specified | Currently: notification protocol auto-saves on tap; frequency/grace period require "Confirm Settings" button. Switch everything to auto-save with toast feedback. |
| F36 | As a user, I want toast messages to feel consistent and occasionally warm, so small moments of feedback reinforce trust. | Could | specified | Standardise: all toasts include ✓. First few saves can use warmer copy like "Saved. One more thing taken care of." |
| F37 | As a user, I want screen subtitles to be visually distinct from in-card body text, so the hierarchy is clear. | Could | done | `.ps` bumped to 15px and `font-weight: 500` to separate from in-card descriptions. |

### Bug Fix

| ID | User Story | Priority | Status | Notes |
|----|-----------|----------|--------|-------|
| F38 | As a user, I do not want to see an "Access Level" dropdown when adding a contact, because all contacts receive the full package and this field was deliberately removed. | Must | done | Verified — Access Level field is not present on the live site. Live HTML and repo `index.html` are in sync. |

### Won't Have (for now)

| ID | Feature | Why not |
|----|---------|---------|
| W01 | Legal Will creation (drafting a legally binding Will inside the app) | Emergency Exit records *where* your Will is — it doesn't replace a solicitor. Liability risk is too high. |
| W02 | Account closure automation (automatically closing social media, bank accounts) | Requires API integrations with every platform. GoodTrust does this and it's their core business. Not our lane. |
| W03 | AI-generated legacy stories or memory capture | Evaheld's territory. Emergency Exit is practical and action-oriented, not sentimental. Stay in lane. |
| W04 | Cryptocurrency wallet management or key storage | Extremely high security risk. Users should use purpose-built crypto custody solutions. We just record that the asset exists. |

---

### How to use this backlog

- **Adding a new feature:** Add a row with the next ID number (F39, F40...), write the user story, set priority and status to `idea`.
- **When building:** Move status to `specified` once requirements are clear, `in-progress` when coding, `done` when shipped.
- **Re-prioritising:** Change the MoSCoW priority and move the row to the correct section. Add a note explaining why.
- **Removing a feature:** Move it to "Won't Have" with an explanation. Never delete — context matters.

---

## End-of-Chat Checklist

- [ ] Download the new `index.html`
- [ ] Download the new `CLAUDE.md`
- [ ] Did anything structural change? Update `CLAUDE.md`
- [ ] Replace files in VS Code (`./index.html` AND `./frontend/index.html`)
- [ ] `git add -A`
- [ ] `git commit -m "describe what changed"`
- [ ] `git push`
