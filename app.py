from flask import Flask, render_template, redirect, url_for
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Setup Google Sheets connection
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Sheet setup
sheet = client.open_by_key('17AHo4_PR8mz2RolXrOD-vzw4geI13xH7dujGaAcIeoE')
read_ws = sheet.worksheet('MenuData')     # Sheet with food list
write_ws = sheet.worksheet('WeeklyMenu')  # Sheet with weekly menus

# Get current week number
def get_current_week():
    return str(datetime.now().isocalendar()[1])

# Read food items from MenuData
def get_food_items():
    rows = read_ws.get_all_values()
    return [row[1] for row in rows[1:] if len(row) > 1]  # Skip header and blank rows

# Fetch existing menu from WeeklyMenu
def get_menu():
    try:
        data = write_ws.get_all_records()
        if not data:
            return {}

        menu = {}
        for row in data:
            day = row.get('Day')
            lunch = row.get('Lunch')
            dinner = row.get('Dinner')
            if day:
                menu[day] = {'Lunch': lunch, 'Dinner': dinner}
        return menu
    except Exception as e:
        print(f"[ERROR] Failed to read menu: {e}")
        return {}

# Generate and store weekly menu with unique food items
def generate_menu():
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    food_items = get_food_items()
    current_week = get_current_week()

    if len(food_items) < 14:
        print("[ERROR] Not enough unique food items. At least 14 required.")
        return

    random.shuffle(food_items)
    selected_items = food_items[:14]  # Pick 14 unique items
    weekly_menu = []

    for i, day in enumerate(days):
        lunch = selected_items[i]
        dinner = selected_items[i + 7]
        weekly_menu.append([current_week, day, lunch, dinner])

    # Append only if this week's menu doesn't exist yet
    data = write_ws.get_all_records(expected_headers=["Week", "Day", "Lunch", "Dinner"])
    existing_weeks = {row['Week'] for row in data}

    if current_week not in existing_weeks:
        write_ws.append_rows(weekly_menu, value_input_option='USER_ENTERED')

@app.route('/')
def index():
    menu = get_menu()
    if not menu:
        generate_menu()
        menu = get_menu()
    return render_template('index.html', menu=menu)

@app.route('/refresh')
def refresh():
    generate_menu()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
