from flask import Flask, render_template, redirect, url_for
import pandas as pd
import random

app = Flask(__name__)



CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4Mia9DuUh7c3HFYjWxDorc59IcRKYcj-R5_4a7k7Koy6cc8AF83xFeWm2ifEOZp_K4HkSXBTHFccP/pub?gid=1243001482&single=true&output=csv"

def get_food_items():
    try:
        print("Fetching CSV from:", CSV_URL)
        df = pd.read_csv(CSV_URL)
        print("Sheet preview:\n", df.head())

        # Inspect available columns
        print("Columns found:", df.columns.tolist())

        # Use column name if available
        if 'Food Items' in df.columns:
            return df['Food Items'].dropna().tolist()
        else:
            # Fallback to second column if unnamed
            return df.iloc[:, 1].dropna().tolist()

    except Exception as e:
        print("Error fetching sheet:", e)
        return ["Paneer", "Chana", "Soya", "Rajma"]


def generate_weekly_menu():
    food_items = get_food_items()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Ensure we have at least 14 unique items
    unique_items = list(set(food_items))
    if len(unique_items) < 14:
        return {day: {'Lunch': 'N/A', 'Dinner': 'N/A'} for day in days}

    # Shuffle and pick 14 unique meals
    random.shuffle(unique_items)
    selected_items = unique_items[:14]

    # Split into lunch and dinner
    lunch_items = selected_items[:7]
    dinner_items = selected_items[7:]

    weekly_menu = {}
    for i, day in enumerate(days):
        weekly_menu[day] = {
            'Lunch': lunch_items[i],
            'Dinner': dinner_items[i]
        }

    return weekly_menu

@app.route('/')
def index():
    menu = generate_weekly_menu()
    return render_template("index.html", menu=menu)

@app.route('/refresh')
def refresh():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
