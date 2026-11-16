# News Thingy: For a lack of a better name

A Django service that summarizes news articles from Philippine publishers using LLMs, providing key takeaways and direct links to original stories.

---

## Features

- **Classic Broadsheet Design**: Clean newspaper styling using Times New Roman for serif typography, cream paper (`#fbfbfa`) and obsidian dark mode (`#0d0e11`), with high-contrast borders and dividers.
- **Substantive Domain Models**: Concrete Django models for `Category`, `Outlet`, `Article`, `Summary`, and `UserSubscription`.
- **Direct Source Links**: Every summary links to the full original article (*Philippine Daily Inquirer, BusinessWorld, Rappler, GMA News Online, Philstar Global, ABS-CBN News*).
- **Source Filtering**: Follow or unfollow specific newsrooms to customize the stories displayed.

---

## Project Structure

```
news-thingy/
├── .venv/                         # Virtual environment (Django 6.1.1)
├── manage.py                      # Django CLI
├── requirements.txt               # Locked dependencies
├── news_thingy/                   # Project settings & root routing
├── accounts/                      # Authentication & CustomUser model
├── news/                          # News domain: Outlets, Articles, Summaries, Subscriptions
│   ├── management/commands/
│   │   └── seed_news.py           # Command to seed realistic Philippine news articles
│   ├── models.py
│   └── tests.py
├── core/                          # Home feed & subscription toggle views
└── templates/                     # Editorial publication templates
    ├── base.html                  # Masthead, navigation, theme toggle, and footer
    ├── core/home.html             # Main news feed & topic filters
    └── accounts/
        ├── auth_base.html         # Split layout for authentication pages
        ├── login.html             # User login page
        └── register.html          # New user registration page
```

## Vertical Slicing and Supabase

The active application screens are organized as feature slices under `apps/`:

```
apps/login/          # login behavior and URL configuration
apps/register/       # registration behavior and URL configuration
apps/home/           # authenticated briefing and source subscriptions
apps/profile/        # Profile model, form, screen, and migration
apps/user_settings/  # UserSettings model, form, screen, and migration
templates/<feature>/
static/css/<feature>/  static/js/<feature>/  static/images/<feature>/
```

The legacy `accounts`, `core`, and `news` modules remain for the custom user model, the existing news domain, and backward-compatible routes. The user-facing routes are `/login/`, `/register/`, `/`, `/profile/`, and `/settings/`.

### Connect Supabase

1. In Supabase, create/open your project and select **Connect**.
2. Copy the exact Session Pooler connection string (or Direct connection if your network supports it).
3. Copy `.env.example` to `.env`, then replace its placeholder with the copied value. Do not commit `.env`.
4. Install packages: `python -m pip install -r requirements.txt`.
5. Run `python manage.py check`, `python manage.py makemigrations`, and `python manage.py migrate`.
6. Register an account in the app, save a Profile and Settings change, then open **Supabase > Table Editor**. Confirm rows in `accounts_customuser`, `profile_profile`, and `user_settings_usersettings`.

Without a real `DATABASE_URL`, the project deliberately uses local SQLite so UI development and automated tests remain runnable. Once `DATABASE_URL` is in `.env`, Django uses Supabase PostgreSQL with SSL.

### Screenshot checklist

Run the server, use a browser at `http://127.0.0.1:8000`, and capture one screenshot per item below. Keep the browser address bar visible when it helps identify the screen, but hide passwords and database credentials.

1. **Login** - open `/login/`; show the heading, fields, and Create an account link.
2. **Register** - open `/register/`; show the username, email, password fields, and Log in link.
3. **Home** - register/log in, then open `/`; show the Today’s summaries heading, category filters, source controls, and at least one article card. Run `python manage.py seed_news` first if the feed is empty.
4. **Profile** - open `/profile/`; enter a non-sensitive full name and short bio, save, and show the success message.
5. **Settings** - open `/settings/`; change at least one preference, save, and show the success message.
6. **Supabase data** - open **Supabase Dashboard > Table Editor**, choose `profile_profile` or `user_settings_usersettings`, and show a saved row. Do not show the Connect dialog or any connection string.
7. **Folder structure** - in VS Code Explorer or File Explorer, expand `apps`, `templates`, and `static/css`, `static/js`, and `static/images` so the five feature names are visible in one frame.

---

## Quick Start Guide

### 1. Open Terminal in Project Directory
Make sure your terminal is in the project folder:
```powershell
cd C:\Users\gab\Documents\proj\news-thingy
```

### 2. Run Migrations & Seed Sample Stories
```powershell
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py seed_news
```

### 3. Start Development Server
```powershell
.\.venv\Scripts\python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your browser.

---

## Running the Automated Test Suite

```powershell
.\.venv\Scripts\python manage.py test
```
All 14 tests cover registration, auto-onboarding, login, logout, category filtering, summary calculations, and outlet subscription toggles.
