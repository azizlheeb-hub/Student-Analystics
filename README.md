# Student Performance Analytics

A Python web app for tracking academic courses and analyzing GPA trends.

## Features
- Add course records with term, credits, and grade points
- Calculate credit-weighted overall GPA
- Visualize term GPA and grade distribution
- Edit or delete course records
- Persist data locally with SQLite
- Export records to CSV

## Tech stack
Python · Streamlit · SQLite · Pandas · Plotly

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser. The SQLite database is created automatically in the project folder.

## GPA formula
Weighted GPA = sum(grade points × credit hours) / sum(credit hours)

## Notes
This demo uses a 4.0 grade-point scale. Confirm your institution's grading scale before using it for official calculations.
