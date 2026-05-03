import os
import json
import re
from dotenv import load_dotenv
from google import genai
from database import create_users_table
from auth import register_user, login_user

# Create users table
create_users_table()

# Load environment variables
load_dotenv()

# AI PROVIDER
USE_AI = "gemini"  # change to "openai" if needed


# =============================
# AI FUNCTIONS
# =============================

def get_ai_response(prompt):
    if USE_AI == "gemini":
        return gemini_ai(prompt)
    elif USE_AI == "openai":
        return openai_ai(prompt)
    else:
        return "Invalid AI Provider"


def gemini_ai(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def openai_ai(prompt):
    import openai

    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# =============================
# DATA FUNCTIONS
# =============================

def load_data():
    if not os.path.exists("data.json"):
        return {}

    with open("data.json", "r") as file:
        return json.load(file)


def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)


# =============================
# LOGIN / SIGNUP MENU
# =============================

current_user = None

while True:
    print("\n=== AI Roadmap App ===")
    print("1. Signup")
    print("2. Login")
    print("3. Exit")

    choice = input("Choose option: ")

    # SIGNUP
    if choice == "1":
        username = input("Username: ")
        email = input("Email: ")
        password = input("Password: ")

        if register_user(username, email, password):
            print("✅ Account created successfully!")
        else:
            print("❌ Username or Email already exists.")

    # LOGIN
    elif choice == "2":
        email = input("Email: ")
        password = input("Password: ")

        if login_user(email, password):
            print("✅ Login successful!")
            current_user = email
            break
        else:
            print("❌ Invalid credentials.")

    elif choice == "3":
        exit()


# =============================
# DASHBOARD (AFTER LOGIN)
# =============================

while current_user:

    data = load_data()

    print(f"\nWelcome {current_user}")
    print("1. View Roadmap")
    print("2. Create New Roadmap")
    print("3. View Progress")
    print("4. Mark Week as Completed")
    print("5. Logout")

    choice = input("Enter choice (1-5): ")

    # VIEW ROADMAP
    if choice == "1":

        if current_user in data:
            print("\nYour Roadmap:\n")
            print(data[current_user]["roadmap"])
        else:
            print("No roadmap found. Create one first.")

    # CREATE ROADMAP
    elif choice == "2":

        field = input("Enter field: ")
        duration = input("Enter duration: ")
        level = input("Enter your level: ")

        prompt = f"""
Create a detailed learning roadmap.

Field: {field}
Duration: {duration}
Level: {level}

Include:
- Weekly plan
- Resources
- Practice tasks
"""

        print("\nGenerating roadmap...\n")
        roadmap = get_ai_response(prompt)

        data[current_user] = {
            "field": field,
            "duration": duration,
            "level": level,
            "roadmap": roadmap,
            "progress": []
        }

        save_data(data)

        print("✅ Roadmap saved successfully!")

    # VIEW PROGRESS
    elif choice == "3":

        if current_user not in data:
            print("No roadmap found.")
            continue

        roadmap_text = data[current_user]["roadmap"]
        completed = data[current_user]["progress"]

        weeks = re.findall(r"Week\s*\d+", roadmap_text, re.IGNORECASE)
        unique_weeks = sorted(set(weeks))
        total_weeks = len(unique_weeks)

        if total_weeks == 0:
            print("No weeks detected in roadmap.")
        else:
            percent = (len(completed) / total_weeks) * 100

            print("\nCompleted Weeks:")
            if completed:
                for w in completed:
                    print("-", w)
            else:
                print("No weeks completed yet.")

            print(f"\nProgress: {len(completed)} / {total_weeks}")
            print(f"Completion: {percent:.2f}%")

    # MARK WEEK COMPLETED
    elif choice == "4":

        if current_user not in data:
            print("No roadmap found.")
            continue

        roadmap_text = data[current_user]["roadmap"]
        weeks = re.findall(r"Week\s*\d+", roadmap_text, re.IGNORECASE)
        unique_weeks = sorted(set(weeks))

        if not unique_weeks:
            print("No weeks detected.")
            continue

        print("\nAvailable Weeks:")
        for w in unique_weeks:
            print("-", w)

        week = input("Enter week exactly as shown: ")

        if week in unique_weeks:

            if week not in data[current_user]["progress"]:
                data[current_user]["progress"].append(week)
                save_data(data)
                print("✔ Week marked as completed")
            else:
                print("Already completed.")

        else:
            print("Invalid week selection.")

    # LOGOUT
    elif choice == "5":
        current_user = None
        print("Logged out successfully.")