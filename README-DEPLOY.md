# RoofPro CRM — Deployment Guide

One-time setup for any roofing company. After this guide, you only need a company name to spin up a new instance.

---

## Step 1: Create a PythonAnywhere account

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com) and click **Start running** / **Create account**
2. Free plan works. Pick a username like `roofpro` or your company name
3. For custom domain (`crm.yourcompany.com`), upgrade to the $5/month Hacker plan later

## Step 2: Clone the repo

In PythonAnywhere's **Dashboard → Bash Console**:

```bash
git clone https://github.com/YOUR_USERNAME/roofing-crm.git
cd roofing-crm
```

## Step 3: Set up the environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 4: Configure the company

```bash
cp .env.example .env
nano .env
```

Change these values:
```
DJANGO_SECRET_KEY=generate-a-random-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=crm.yourcompany.com
COMPANY_NAME=ABC Roofing
COMPANY_SLUG=abc-roofing
```

Generate a secret key at: https://djecrety.ir/

## Step 5: Set up the database

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

## Step 6: Configure the web app

In PythonAnywhere **Web** tab:
- **Manual configuration** → Python 3.12
- **WSGI file**: edit to point at `roofing_crm.wsgi.application`
- **Static files**: URL `/static/` → directory `/home/YOUR_USERNAME/roofing-crm/staticfiles`
- **Virtualenv**: `/home/YOUR_USERNAME/roofing-crm/venv`

Click **Reload** — your CRM is live.

---

## Template Setup (for re-use)

Once this is working, you can deploy a new company in 5 minutes:

1. `git clone` the repo as a new project
2. Copy `.env.example` → `.env`, change company name
3. `python manage.py migrate && createsuperuser && collectstatic`
4. Add the subdomain in PythonAnywhere Web tab
5. Point DNS: CNAME `crm.companyname.com` → `yourusername.pythonanywhere.com`
