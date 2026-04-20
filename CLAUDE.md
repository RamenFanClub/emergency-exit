# Emergency Exit — Project Context for Claude

## What is this project?

**Emergency Exit** is a personal digital legacy vault app that helps users prepare for sudden death by recording assets, documenting final wishes, storing Will and legal document details, monitoring liveness via periodic check-ins, and automatically notifying nominated family members if the user stops responding.

The app targets everyday Australians (non-technical users) and is being built for:
- **iOS** (Apple App Store)
- **Android** (Google Play Store)
- **Web** (mobile-optimised browser, deployed via GitHub Pages)

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
  - No 1px borders for sectioning — use background colour shifts instead
  - Minimum tap target: 48×48dp
  - Rounded cards (`border-radius: 16px`)
  - Ambient shadows only (blur 24–48px, opacity 4–6%)
  - No pure black — use `#002147` for dark tones

---

## Tech Stack

### Current (prototype)
- Single-file HTML/CSS/JavaScript (`index.html`)
- localStorage for data persistence (key: `ee_v2`)
- Hosted on GitHub Pages

### Planned (production)
- **Frontend:** React Native (shared codebase for iOS + Android)
- **Web:** React (same component logic)
- **Backend:** Python (FastAPI) for check-in scheduling, email/SMS alerts
- **Database:** Encrypted cloud storage (AES-256, zero-knowledge)
- **Notifications:** Email (SendGrid), SMS, native push notifications
- **Auth:** Biometric (Face ID / Touch ID), PIN, 2FA

---

## App Structure — 5 Screens

### 1. Vault (Dashboard)
- Hero headline: "Your legacy is securely anchored"
- Asset + wish count summary
- Status badge (Active / Overdue / Alert Sent)
- Next security check date
- Asset Ledger CTA (full-width gradient button)
- Compact pill buttons: **Add Asset** (navy) + **My Wishes** (grey-blue)
- Vault completeness percentage + progress bar + actionable tips
- Recent activity log

### 2. Ledger (Asset Register)
- Record New Asset CTA (gradient button)
- Assets grouped by category with icons
- Categories: Bank account, Property, Investment, Superannuation, Life insurance, Vehicle, Cryptocurrency, Business, Personal item, Digital account, Other
- Per asset: name, category, estimated value, details (free-text), beneficiary, notes
- Legacy completeness % shown in info box

### 3. My Wishes (formerly "Legacy Wishes")
- New Instruction CTA (dark gradient card with START NOW button)
- **Will & Legal Documents** section:
  - Will status badge (Not recorded / Draft / Signed & witnessed)
  - Will details: status, date signed, solicitor/law firm, primary storage location, secondary location, notes
  - Supplementary Documents: attach records with type, name, storage location, notes
  - Document types: Statement of Wishes, Enduring Power of Attorney, Advance Health Directive, Guardianship Nomination, Funeral Pre-arrangement, Business Succession Plan, Other
- **Funeral & Service** section — wish items with teal checkmarks
- **Digital Handover** section — Social Media Accounts, Photo Archives Access
- **Scheduled Messages** section — personal messages with active count badge
- Wish form fields: Category, Wish (generic label), Details (generic placeholder), Priority
- Status strip: "Status: Safe & Sound"

### 4. Kin (Circle of Trust)
- Guardian cards with initials avatar, name, role badge, access level
- Access levels: Executor (full + account details), Full (all assets & wishes), Wishes only
- Notification Protocol card (dark gradient): "3 Daily Pings → Kin Contacted"
- Next check-in countdown (days remaining) with confirm button

### 5. Config (Check-in Settings)
- **Vitality Pulse** — large pulsing animated circle, tap to confirm alive
- Pulse Frequency — stepper (1–24 Weeks or Months)
- Grace Period — slider (12H → 72H, recommended 48H)
- Verification — FaceID/Biometrics or Secure Passcode (radio toggle)
- Info box: "Missed check-ins after Xh will grant access to N Kin members"
- Confirm Configuration button

---

## Navigation

Bottom tab bar (5 tabs, fixed, rounded top corners):
| Tab | Icon | Screen |
|-----|------|--------|
| Vault | `shield` (filled when active) | Dashboard |
| Ledger | `account_balance` | Asset Register |
| Wishes | `auto_stories` | My Wishes |
| Kin | `family_history` | Circle of Trust |
| Config | `settings_suggest` | Check-in Settings |

Active tab: white icon/label on navy background pill.
Inactive tabs: navy at 35% opacity.

---

## Key UI Patterns

- **Modals:** Bottom-sheet style, slide up from bottom, drag handle at top, tap outside to dismiss
- **Gradient buttons:** Full-width, 18px padding, border-bottom 3px rgba(0,0,0,0.22) for depth, active scale(0.97)
- **Compact action buttons:** Pill-shaped (`border-radius: 9999px`), side by side in a row, 10px vertical padding
- **Cards:** `border-radius: 16px`, surface-low background (`#f2f4f6`) or white with ambient shadow
- **Tags/badges:** Uppercase, 10px, pill-shaped — Active (teal), Secure (blue-grey), Dark (navy), Will (teal border)
- **Toast notifications:** Fixed, centred, navy pill, auto-dismiss after 2.4s
- **Upload buttons:** Dashed border, teal hover state, used for Will details and supplementary documents
- **Icons:** Google Material Symbols Outlined font

---

## Data Model

```javascript
// Stored in localStorage key: 'ee_v2'
{
  assets: [{
    id: timestamp,
    name: string,
    category: string,       // one of 11 categories
    value: number,          // AUD
    details: string,        // free-text (replaces old location + ref fields)
    beneficiary: string,
    notes: string
  }],
  wishes: [{
    id: timestamp,
    category: string,       // one of 9 categories
    title: string,          // labelled "Wish" in the UI
    details: string,
    priority: 'high' | 'medium' | 'low'
  }],
  will: {                   // null if not recorded
    status: 'signed' | 'draft' | 'none',
    date: string,           // date signed (ISO format)
    solicitor: string,      // solicitor or law firm name
    loc1: string,           // primary storage location
    loc2: string,           // secondary storage location
    notes: string
  },
  suppDocs: [{              // supplementary legal documents
    id: timestamp,
    type: string,           // one of 7 document types
    name: string,
    loc: string,            // where the document is stored
    notes: string
  }],
  kin: [{
    id: timestamp,
    first: string,
    last: string,
    rel: string,            // relationship
    email: string,
    phone: string,
    access: 'executor' | 'full' | 'wishes'
  }],
  lastCheckin: timestamp | null,
  fc: number,               // frequency count (e.g. 2)
  fu: 'weeks' | 'months',   // frequency unit
  gp: number,               // grace period in hours (12–72)
  v: 'face' | 'pin',        // verification method
  log: [{ msg: string, time: string }]
}
```

---

## Completeness Score Logic

7 checks, each worth ~14.3%:
1. At least one asset recorded
2. At least one asset has a beneficiary assigned
3. At least one wish recorded
4. Will details recorded
5. At least one guardian added
6. At least one guardian has access level "executor"
7. First check-in completed

---

## Feature Register

A separate Word document (`Emergency_Exit_Feature_Register.docx`) tracks all features across 8 categories with Live / In Progress / Planned status:

1. Asset Register
2. My Wishes (renamed from "Legacy Wishes")
3. Check-in & Liveness Detection
4. Circle of Trust (Family Contacts)
5. Dashboard & Overview
6. Mobile App & Platform
7. Security & Data Privacy
8. Export & Legal Integration

**When adding a new feature:** Update both the app AND regenerate the feature register document so they stay in sync.

---

## Deployment

- **Hosting:** GitHub Pages (free, public repo)
- **URL pattern:** `https://USERNAME.github.io/emergency-exit`
- **Deployment flow:** Edit index.html → commit in VS Code → push to GitHub → live within 60 seconds
- **Repository files:** `index.html`, `CLAUDE.md`, `README.md`

---

## Coding Conventions

- **CSS variables** for all colours (short aliases like `--p`, `--ac`, `--sec`)
- **Short CSS class names** to keep file size small (e.g. `.scr`, `.ni`, `.mo`, `.fi`)
- **No hardcoded hex values** in component styles — always reference variables
- **Mobile-first** — max-width 430px, touch targets min 48px
- **No zoom** — `user-scalable=no` on viewport
- **Smooth scroll** with `-webkit-overflow-scrolling: touch`
- **Transitions:** `transform 0.1s` on buttons (active scale), `all 0.18s` on nav items
- **Animation:** CSS keyframes only for the Vitality Pulse ring (`pr`)
- All monetary values displayed with `Math.round().toLocaleString()` — never raw floats
- **State loading:** Use spread operator `S={...S,...parsed}` to safely merge saved state with new default fields

---

## Planned Backend (FastAPI / Python)

```
/api/checkin          POST  — record a check-in, reset timer
/api/checkin/status   GET   — return current status + days remaining
/api/assets           GET / POST / DELETE
/api/wishes           GET / POST / DELETE
/api/will             GET / PUT — will details
/api/documents        GET / POST / DELETE — supplementary documents
/api/kin              GET / POST / DELETE
/api/notify           POST  — trigger manual notification to kin
/api/config           GET / PUT — frequency, grace period, verif method
```

Scheduled jobs (APScheduler or Celery):
- Daily: check if any user has missed check-in + grace period → send email/SMS
- On overdue: send 3 daily pings to user → then notify kin

---

## Australian Context

- Currency: AUD (`$`)
- Date format: `dd/mm/yyyy` (en-AU locale)
- Superannuation is a key asset category (mandatory in AU)
- Legal references: Enduring Power of Attorney, Advance Health Directive, Guardianship Nomination, Will, Death Benefit Nomination, Funeral Pre-arrangement
- Phone format: `+61 4xx xxx xxx`
- Jurisdiction: Australian law (state-based estate law)

---

## What NOT to do

- Do not use Inter, Roboto, or Arial — always Manrope + Public Sans
- Do not use pure black (`#000000`) — use `#002147` for dark text
- Do not add 1px borders between sections — use background colour shifts
- Do not use `position: fixed` inside iframe-rendered widgets
- Do not use `localStorage` in Claude.ai artifact widgets (use in-memory state) — only in the standalone `index.html`
- Do not make tap targets smaller than 48×48dp
- Do not render monetary values as raw floats — always round and format
- Do not use "Legacy Wishes" — the screen is now called "My Wishes"
- Do not use "Title" as the wish field label — use "Wish" with generic placeholders
- Do not use separate location/ref fields for assets — use a single "Details" textarea instead
