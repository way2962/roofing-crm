# RoofPro CRM — Project Instructions

## Overview
Django + HTMX CRM for roofing companies. Incoming call IVR chatbot, client management, appointment booking. Ready for QuickBooks Online + Twilio integration.

## Tech Stack
- **Django 5.x** — Python web framework
- **HTMX 2.x** — dynamic UI without JS framework
- **Bootstrap 5.3.3** — UI
- **SQLite** — database (upgradable to PostgreSQL)
- **WhiteNoise** — static file serving
- **PythonAnywhere** — hosting
- **Twilio** — IVR phone system (ready, not yet connected)

## Quick Reference

### Run Locally
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Deploy New Company
1. Clone repo: `git clone https://github.com/way2962/roofing-crm.git roofing-crm-{slug}`
2. Create PythonAnywhere web app (manual config, Python 3.12)
3. Set virtualenv, run migrate/createsuperuser/collectstatic
4. Set COMPANY_NAME in WSGI file
5. Reload

### Key URLs
- **Dashboard:** `/`
- **Call Simulator:** `/call-simulator/` (in-browser IVR test)
- **Appointments:** `/appointments/`
- **Clients:** `/clients/`
- **Log Call:** `/log-call/`
- **Admin:** `/admin/`
- **Twilio webhooks:** `/twilio/voice/`

### Models
- **Client** — name, phone, email, address, qbo_id, is_active
- **CallLog** — caller details, inquiry_type (general/emergency/estimate/service), from_ivr
- **Appointment** — caller info, is_emergency, reason, status (pending/confirmed/completed/cancelled), from_ivr

### IVR Call Flow (Twilio / Simulator)
1. Call comes in → `/twilio/voice/` looks up phone number
2. **Existing client:** name announced → menu (emergency / general / service / estimate)
3. **New caller:** gather name → address → need → appointment created
4. Emergency calls flagged prominently on dashboard

## GitHub
- **Repo:** `https://github.com/way2962/roofing-crm`
- **Token:** Revoked — use `gh auth login` or create a new repo-scoped token if needed

## Hosting
- **PythonAnywhere:** username `thoangai`
- **Live at:** `https://thoangai.pythonanywhere.com`
- **Deploy template:** See memory/roofpro-crm-template.md

## Next Steps / Roadmap
- [ ] Connect real Twilio phone number (buy number, point webhook to `/twilio/voice/`)
- [ ] Integrate QuickBooks Online API (pull clients, push invoices)
- [ ] Add email notifications for appointments
- [ ] Add appointment scheduling calendar
- [ ] Multi-user with permissions
- [ ] PostgreSQL upgrade when scaling
