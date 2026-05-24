# Anik Tech School Website

A Flask-based university website for Anik Tech School.

## Project Structure

```
anik_tech_school/
├── app.py                  ← Main Flask app
├── requirements.txt        ← Python dependencies
├── templates/
│   ├── base.html           ← Shared layout (navbar + footer)
│   ├── index.html          ← Home page
│   ├── programs.html       ← Programs page
│   ├── admissions.html     ← Admissions page
│   ├── about.html          ← About page
│   └── contact.html        ← Contact page
└── static/
    └── css/
        └── style.css       ← All styles
```

## How to Run in PyCharm

### Step 1 — Open the project
Open the `anik_tech_school` folder in PyCharm.

### Step 2 — Install Flask
Open the Terminal in PyCharm (View > Tool Windows > Terminal) and run:
```
pip install flask
```

### Step 3 — Run the app
In the Terminal, run:
```
python app.py
```

### Step 4 — Open in browser
Go to: http://127.0.0.1:5000

## Pages
- `/`           → Home
- `/programs`   → Programs
- `/admissions` → Admissions
- `/about`      → About
- `/contact`    → Contact
