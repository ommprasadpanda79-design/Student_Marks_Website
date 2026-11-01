# Student Marks Management System - Website

## Requirements
- Python 3.10 or newer
- VS Code (recommended)

## Setup
1. Open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Install Flask:
   `python -m pip install -r requirements.txt`
4. Start the website:
   `python app.py`
5. Open `http://127.0.0.1:5000` in your browser.

## Features
- Add, display, search, update and delete student records
- Calculate total, percentage and grade
- SQLite database for persistent storage
- Linear Search implemented in Python
- Bubble Sort implemented in Python for ranking

## Existing console project
Keep your original `main.py` and `students.json`. This website is a separate interface and stores its records in `students.db`. It does not overwrite the console project or its JSON data.

## Notes
This is a local academic demonstration app. Before public deployment, change the Flask secret key, add authentication, and use production deployment settings.
