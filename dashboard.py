import streamlit as st
import json
import os


# ----------------------------
# Load all roadmap data
# ----------------------------
def load_data():
    if not os.path.exists("data.json"):
        return {}
    with open("data.json", "r") as f:
        return json.load(f)


def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------
# Dashboard Function
# ----------------------------
def show_dashboard():

    st.title("📊 Progress Dashboard")

    user_email = st.session_state.user_email

    data = load_data()

    user_roadmaps = data.get(user_email, [])

    if not user_roadmaps:
        st.info("No roadmaps found.")
        return

    # Roadmap dropdown
    roadmap_titles = [
        f"{r['field']} | {r['duration']} Weeks"
        for r in user_roadmaps
    ]

    selected_index = st.selectbox(
        "Select Roadmap",
        range(len(user_roadmaps)),
        format_func=lambda i: roadmap_titles[i]
    )

    selected_roadmap = user_roadmaps[selected_index]
    total_weeks = int(selected_roadmap["duration"])

    st.subheader("Track Your Weekly Progress")

    # Initialize progress if not exists
    if "progress" not in selected_roadmap:
        selected_roadmap["progress"] = []

    completed_weeks = selected_roadmap["progress"]
    updated_completed = []

    # Week checkboxes
    for week in range(1, total_weeks + 1):
        checked = week in completed_weeks
        if st.checkbox(
            f"Week {week}",
            value=checked,
            key=f"{selected_index}_week_{week}"
        ):
            updated_completed.append(week)

    # Save progress
    if st.button("Save Progress"):
        selected_roadmap["progress"] = updated_completed
        data[user_email] = user_roadmaps
        save_data(data)
        st.success("Progress saved!")


    # Progress Calculation
    progress_percent = (len(updated_completed) / total_weeks) * 100

# st.subheader("Progress")
# st.progress(progress_percent / 100)

# # 📊 Metrics Cards
# col1, col2, col3 = st.columns(3)

# with col1:
#     st.metric("Total Weeks", total_weeks)

# with col2:
#     st.metric("Completed Weeks", len(updated_completed))

# with col3:
#     st.metric("Progress %", f"{progress_percent:.1f}%")

    st.subheader("Progress")
    st.progress(progress_percent / 100)

    st.write(f"Completed: {len(updated_completed)} / {total_weeks} Weeks")
    st.write(f"Progress: {progress_percent:.1f}%")

    