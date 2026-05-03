import streamlit as st
from database import create_tables
from roadmap_engine import generate_roadmap, create_pdf
from auth import register_user, login_user
from dashboard import show_dashboard
import json
import os

# ---------------------------
# PAGE CONFIG (must be first)
# ---------------------------
st.set_page_config(
    page_title="Roadmap.AI",
    layout="wide",
    page_icon="🛸"
)

# ---------------------------
# CUSTOM CSS — Startup-Grade Dark Theme
# ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

:root {
    --void:        #06090f;
    --surface:     #0c1220;
    --panel:       #101828;
    --card:        #131d2e;
    --line:        #1e2d42;
    --line-hi:     #2a4060;
    --cyan:        #38bdf8;
    --cyan-dim:    #0ea5e9;
    --cyan-ghost:  rgba(56,189,248,0.10);
    --blue:        #818cf8;
    --blue-ghost:  rgba(129,140,248,0.10);
    --green:       #34d399;
    --green-ghost: rgba(52,211,153,0.08);
    --amber:       #fbbf24;
    --red:         #f87171;
    --t1: #f0f8ff;
    --t2: #94afc8;
    --t3: #4a6785;
    --mono:    'DM Mono', monospace;
    --display: 'Syne', sans-serif;
    --body:    'DM Sans', sans-serif;
    --r-sm: 4px;
    --r-md: 6px;
    --r-lg: 8px;
}

html, body, [class*="css"] {
    font-family: var(--body) !important;
    background-color: var(--void) !important;
    color: var(--t1) !important;
}

.stApp {
    background:
        radial-gradient(ellipse 70% 40% at 15% 0%, rgba(14,165,233,0.06) 0%, transparent 100%),
        radial-gradient(ellipse 50% 50% at 85% 100%, rgba(129,140,248,0.06) 0%, transparent 100%),
        var(--void) !important;
}

.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(30,45,66,0.5) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,45,66,0.5) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: radial-gradient(ellipse 100% 60% at 50% 0%, black 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio label {
    font-family: var(--body) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: var(--t2) !important;
    padding: 9px 14px !important;
    border-radius: var(--r-md) !important;
    border-left: 2px solid transparent !important;
    transition: all 0.15s ease !important;
    background: transparent !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: var(--t1) !important;
    background: var(--panel) !important;
    border-left-color: var(--line-hi) !important;
}

/* ── Typography ── */
h1 {
    font-family: var(--display) !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--t1) !important;
    letter-spacing: -0.01em !important;
    text-shadow: none !important;
}
h2 {
    font-family: var(--display) !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: var(--t1) !important;
    letter-spacing: -0.01em !important;
    text-shadow: none !important;
}
h3 {
    font-family: var(--display) !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: var(--t1) !important;
    text-shadow: none !important;
}
p { color: var(--t2) !important; font-size: 0.9rem; line-height: 1.6; }

.stCaption, small {
    font-family: var(--mono) !important;
    color: var(--t3) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.04em !important;
}

hr { border-color: var(--line) !important; opacity: 1 !important; margin: 1rem 0 !important; }

/* ── Form Labels — THE KEY FIX: visible uppercase labels ── */
.stTextInput > label,
.stNumberInput > label,
.stSelectbox > label,
.stRadio > label {
    font-family: var(--display) !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--t2) !important;
    margin-bottom: 5px !important;
    display: block !important;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
    color: var(--t1) !important;
    font-family: var(--body) !important;
    font-size: 0.9rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
}
.stTextInput input::placeholder { color: var(--t3) !important; }

[data-testid="stSelectbox"] > div > div {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
    color: var(--t1) !important;
    font-family: var(--body) !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
}
[data-testid="stSelectbox"] ul {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
}
[data-testid="stSelectbox"] li { color: var(--t1) !important; font-family: var(--body) !important; }
[data-testid="stSelectbox"] li:hover { background: var(--cyan-ghost) !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: var(--display) !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    border-radius: var(--r-md) !important;
    transition: all 0.15s ease !important;
    text-transform: uppercase !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(14,165,233,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 28px rgba(14,165,233,0.4) !important;
    transform: translateY(-1px) !important;
    opacity: 0.95 !important;
}
.stButton > button:not([kind="primary"]) {
    background: var(--panel) !important;
    color: var(--t2) !important;
    border: 1px solid var(--line) !important;
}
.stButton > button:not([kind="primary"]):hover {
    color: var(--t1) !important;
    border-color: var(--line-hi) !important;
    background: var(--card) !important;
}

[data-testid="stDownloadButton"] button {
    font-family: var(--display) !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    background: rgba(52,211,153,0.08) !important;
    color: var(--green) !important;
    border: 1px solid rgba(52,211,153,0.3) !important;
    border-radius: var(--r-md) !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: rgba(52,211,153,0.14) !important;
    border-color: var(--green) !important;
    transform: translateY(-1px) !important;
}

/* ── Progress Bar ── */
[data-testid="stProgressBar"] > div {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: 3px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--cyan-dim), var(--blue)) !important;
    border-radius: 3px !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1px solid var(--line) !important;
    border-radius: var(--r-lg) !important;
    background: var(--card) !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    background: var(--card) !important;
    color: var(--t2) !important;
    font-family: var(--body) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 12px 16px !important;
}
[data-testid="stExpander"] summary:hover {
    color: var(--t1) !important;
    background: var(--panel) !important;
}
[data-testid="stExpander"] > div > div {
    background: var(--surface) !important;
    padding: 12px 16px !important;
}

/* ── Checkbox ── */
.stCheckbox label {
    color: var(--t2) !important;
    font-family: var(--body) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
    color: var(--t1) !important;
    font-family: var(--body) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb { background: var(--line-hi); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan); }

/* ══ COMPONENTS ══ */

.sb-brand {
    padding: 20px 16px 16px;
    border-bottom: 1px solid var(--line);
    margin-bottom: 8px;
}
.sb-brand-name {
    font-family: var(--display);
    font-size: 1rem;
    font-weight: 800;
    color: var(--t1);
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 3px;
}
.sb-brand-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 8px var(--cyan);
    display: inline-block;
    animation: dotpulse 2.5s ease-in-out infinite;
}
@keyframes dotpulse {
    0%,100% { box-shadow: 0 0 6px var(--cyan); }
    50% { box-shadow: 0 0 14px var(--cyan), 0 0 28px rgba(56,189,248,0.4); }
}
.sb-user {
    font-family: var(--mono);
    font-size: 0.68rem;
    color: var(--t3);
    letter-spacing: 0.05em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.page-header { margin-bottom: 20px; }
.page-eyebrow {
    font-family: var(--mono);
    font-size: 0.68rem;
    color: var(--cyan);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 7px;
}
.page-title {
    font-family: var(--display);
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--t1);
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 5px;
}
.page-desc {
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--t3);
    letter-spacing: 0.04em;
}

.auth-wrap {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
    max-width: 480px;
    margin: 0 auto;
}
.auth-hero {
    background:
        radial-gradient(ellipse 80% 80% at 50% -20%, rgba(56,189,248,0.12) 0%, transparent 70%),
        var(--panel);
    border-bottom: 1px solid var(--line);
    padding: 36px 28px 28px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.auth-grid-bg {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(30,45,66,0.7) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,45,66,0.7) 1px, transparent 1px);
    background-size: 32px 32px;
    opacity: 0.5;
    pointer-events: none;
}
.auth-logo-text {
    font-family: var(--display);
    font-size: 2rem;
    font-weight: 800;
    color: var(--t1);
    letter-spacing: -0.02em;
    position: relative;
    z-index: 1;
    margin-bottom: 6px;
}
.auth-logo-text span {
    background: linear-gradient(135deg, var(--cyan) 0%, var(--blue) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.auth-tagline {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--t3);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    position: relative;
    z-index: 1;
}
.auth-form-body { padding: 24px 28px 28px; }

.outcome-box {
    background: var(--panel);
    border: 1px solid var(--line);
    border-left: 3px solid var(--cyan-dim);
    border-radius: var(--r-lg);
    padding: 14px 18px;
    margin-bottom: 16px;
    font-size: 0.9rem;
    color: var(--t2);
    line-height: 1.65;
    font-family: var(--body);
}
.outcome-label {
    font-family: var(--display);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.outcome-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 6px var(--cyan);
    display: inline-block;
}

.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--r-md);
    padding: 7px 14px;
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--t2);
    letter-spacing: 0.06em;
    white-space: nowrap;
    width: 100%;
    box-sizing: border-box;
}
.stat-pill strong { color: var(--t1) !important; font-weight: 500; }
.stat-pill.cyan strong { color: var(--cyan) !important; }
.stat-pill.green strong { color: var(--green) !important; }

.week-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: var(--r-lg);
    padding: 14px 18px;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
}
.week-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--cyan-dim), var(--blue));
}
.week-card-eyebrow {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--cyan);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.week-card-title {
    font-family: var(--display);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--t1);
    letter-spacing: -0.01em;
    margin-bottom: 10px;
}
.week-pbar-track {
    height: 3px;
    background: var(--line);
    border-radius: 2px;
    overflow: hidden;
}
.week-pbar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--cyan-dim), var(--blue));
    border-radius: 2px;
}
.week-card-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--t3);
    letter-spacing: 0.05em;
    margin-top: 6px;
}

.day-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-left: 2px solid var(--cyan-dim);
    border-radius: var(--r-md);
    padding: 10px 14px;
    margin: 6px 0;
}
.day-card.done {
    border-left-color: var(--green);
    background: rgba(52,211,153,0.04);
}
.day-card-top {
    display: flex;
    align-items: center;
    gap: 10px;
}
.day-badge {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--t3);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    min-width: 44px;
    flex-shrink: 0;
}
.day-badge.done { color: var(--green); }
.day-title-text {
    font-family: var(--body);
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--t1);
    flex: 1;
}
.day-hours {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--t3);
    flex-shrink: 0;
}

.topic-chips { display: flex; flex-wrap: wrap; gap: 5px; margin: 8px 0 10px; }
.topic-chip {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--cyan);
    background: var(--cyan-ghost);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 3px;
    padding: 2px 8px;
}

.section-label {
    font-family: var(--display);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--t3);
    margin: 10px 0 5px;
}

.task-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--r-sm);
    padding: 7px 10px;
    margin: 4px 0;
    font-size: 0.85rem;
    color: var(--t2);
    font-family: var(--body);
    line-height: 1.45;
}
.task-bullet { color: var(--cyan); flex-shrink: 0; }

.resource-chips { display: flex; flex-wrap: wrap; gap: 5px; margin: 6px 0 12px; }
.resource-chip {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.06em;
    border-radius: var(--r-sm);
    padding: 4px 10px;
    text-decoration: none;
    border: 1px solid;
    transition: filter 0.15s;
    display: inline-block;
}
.resource-chip:hover { filter: brightness(1.25); }
.resource-chip.video   { color: #f87171; background: rgba(248,113,113,0.08); border-color: rgba(248,113,113,0.25); }
.resource-chip.article { color: var(--green); background: var(--green-ghost); border-color: rgba(52,211,153,0.25); }
.resource-chip.course  { color: var(--cyan); background: var(--cyan-ghost); border-color: rgba(56,189,248,0.25); }
.resource-chip.doc     { color: var(--blue); background: var(--blue-ghost); border-color: rgba(129,140,248,0.25); }
.resource-chip.link    { color: var(--t2); background: var(--panel); border-color: var(--line); }

.project-box {
    background: rgba(52,211,153,0.04);
    border: 1px dashed rgba(52,211,153,0.3);
    border-radius: var(--r-lg);
    padding: 14px 18px;
    margin: 12px 0 20px;
}
.project-eyebrow {
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 5px;
}
.project-title {
    font-family: var(--display);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--t1);
    margin-bottom: 5px;
}
.project-desc { font-size: 0.85rem; color: var(--t2); line-height: 1.5; margin-bottom: 6px; }
.project-deliverable {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--t3);
}

.divider-line { height: 1px; background: var(--line); margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

FILE_PATH = "data.json"

def load_data():
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

create_tables()

# ---------------------------
# SAVE DAY PROGRESS
# ---------------------------
def _save_day_progress(user_email, roadmap_index, progress_set):
    file_data = load_data()
    if user_email in file_data and roadmap_index < len(file_data[user_email]):
        file_data[user_email][roadmap_index]["day_progress"] = list(progress_set)
        save_data(file_data)

# ---------------------------
# RENDER ROADMAP
# ---------------------------
def render_roadmap(roadmap_json: str, user_email: str = None, roadmap_index: int = None):
    try:
        data_raw = json.loads(roadmap_json)
    except Exception:
        st.markdown(roadmap_json)
        return

    progress_key = f"progress_{roadmap_index}" if roadmap_index is not None else "progress_preview"

    saved_progress = set()
    if user_email and roadmap_index is not None:
        file_data = load_data()
        roadmaps = file_data.get(user_email, [])
        if roadmap_index < len(roadmaps):
            saved_progress = set(roadmaps[roadmap_index].get("day_progress", []))

    if progress_key not in st.session_state:
        st.session_state[progress_key] = saved_progress

    outcome = data_raw.get("final_outcome", "")
    if outcome:
        st.markdown(
            f'<div class="outcome-box">'
            f'<div class="outcome-label"><span class="outcome-dot"></span>Mission Objective</div>'
            f'{outcome}'
            f'</div>',
            unsafe_allow_html=True
        )

    total_days = sum(len(w.get("days", [])) for w in data_raw.get("weeks", []))
    total_hours = sum(
        d.get("estimated_hours", 0)
        for w in data_raw.get("weeks", [])
        for d in w.get("days", [])
    )
    completed_days = len(st.session_state[progress_key])
    progress_pct = (completed_days / total_days * 100) if total_days > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-pill cyan"><strong>{data_raw.get("duration_weeks","?")}W</strong>&nbsp;duration</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-pill"><strong>{total_days}</strong>&nbsp;days</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-pill"><strong>~{total_hours}h</strong>&nbsp;total</div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-pill green"><strong>{completed_days}/{total_days}</strong>&nbsp;done</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(progress_pct / 100, text=f"Overall Progress — {progress_pct:.0f}%")
    st.divider()

    for week in data_raw.get("weeks", []):
        wn = week.get("week_number", "?")
        theme = week.get("theme", "")
        overview = week.get("overview", "")
        week_days = week.get("days", [])

        week_done = sum(1 for d in week_days if f"w{wn}d{d['day']}" in st.session_state[progress_key])
        week_pct = int(week_done / len(week_days) * 100) if week_days else 0

        st.markdown(
            f'<div class="week-card">'
            f'<div class="week-card-eyebrow">Phase {str(wn).zfill(2)}</div>'
            f'<div class="week-card-title">{theme}</div>'
            f'<div class="week-pbar-track"><div class="week-pbar-fill" style="width:{week_pct}%"></div></div>'
            f'<div class="week-card-meta"><span>{week_done}/{len(week_days)} days complete</span><span>{week_pct}%</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )
        if overview:
            st.caption(f"// {overview}")

        with st.expander(f"View Phase {wn} — {len(week_days)} days", expanded=(wn == 1)):
            for day in week_days:
                dn = day.get("day", "?")
                dtitle = day.get("title", "")
                topics = day.get("topics", [])
                tasks = day.get("tasks", [])
                resources = day.get("resources", [])
                hours = day.get("estimated_hours", "?")
                day_key = f"w{wn}d{dn}"
                is_done = day_key in st.session_state[progress_key]

                badge_class = "day-badge done" if is_done else "day-badge"
                badge_text = "✓ done" if is_done else f"day {str(dn).zfill(2)}"
                card_class = "day-card done" if is_done else "day-card"

                st.markdown(
                    f'<div class="{card_class}">'
                    f'<div class="day-card-top">'
                    f'<span class="{badge_class}">{badge_text}</span>'
                    f'<span class="day-title-text">{dtitle}</span>'
                    f'<span class="day-hours">~{hours}h</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if topics:
                    chips = "".join(f'<span class="topic-chip">{t}</span>' for t in topics)
                    st.markdown(f'<div class="topic-chips">{chips}</div>', unsafe_allow_html=True)

                if tasks:
                    st.markdown('<div class="section-label">Objectives</div>', unsafe_allow_html=True)
                    for task in tasks:
                        st.markdown(
                            f'<div class="task-item"><span class="task-bullet">▸</span>{task}</div>',
                            unsafe_allow_html=True
                        )

                if resources:
                    st.markdown('<div class="section-label">Resources</div>', unsafe_allow_html=True)
                    chips_html = ""
                    for r in resources:
                        rtype = r.get("type", "link").lower()
                        rtitle = r.get("title", "Resource")
                        rurl = r.get("url", "#")
                        chips_html += f'<a href="{rurl}" target="_blank" class="resource-chip {rtype}">{rtitle}</a>'
                    st.markdown(f'<div class="resource-chips">{chips_html}</div>', unsafe_allow_html=True)

                col_cb, _ = st.columns([1, 4])
                with col_cb:
                    checked = st.checkbox(
                        "Mark complete" if not is_done else "Completed ✓",
                        value=is_done,
                        key=f"cb_{progress_key}_{day_key}"
                    )
                    if checked and day_key not in st.session_state[progress_key]:
                        st.session_state[progress_key].add(day_key)
                        if user_email and roadmap_index is not None:
                            _save_day_progress(user_email, roadmap_index, st.session_state[progress_key])
                        st.rerun()
                    elif not checked and day_key in st.session_state[progress_key]:
                        st.session_state[progress_key].discard(day_key)
                        if user_email and roadmap_index is not None:
                            _save_day_progress(user_email, roadmap_index, st.session_state[progress_key])
                        st.rerun()

                st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

        mp = week.get("mini_project", {})
        if mp:
            st.markdown(
                f'<div class="project-box">'
                f'<div class="project-eyebrow">⬡ Mission Module</div>'
                f'<div class="project-title">{mp.get("title","")}</div>'
                f'<div class="project-desc">{mp.get("description","")}</div>'
                f'<div class="project-deliverable">// Deliverable: {mp.get("deliverable","")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------
# AUTH PAGE
# ---------------------------
def show_auth():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown(
            '<div class="auth-wrap">'
            '<div class="auth-hero">'
            '<div class="auth-grid-bg"></div>'
            '<div class="auth-logo-text">Roadmap<span>.AI</span></div>'
            '<div class="auth-tagline">Personalized AI-powered learning paths</div>'
            '</div>'
            '<div class="auth-form-body">',
            unsafe_allow_html=True
        )
        choice = st.radio("", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        email = st.text_input("Email Address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Min. 6 characters")

        if choice == "Sign Up":
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success = register_user(email, password)
                    if success:
                        st.success("Account created! Please log in.")
                    else:
                        st.error("That email is already registered.")
        else:
            if st.button("Log In", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    user = login_user(email, password)
                    if user:
                        st.session_state["user"] = dict(user)
                        st.session_state["user_email"] = email
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")

        st.markdown('</div></div>', unsafe_allow_html=True)


# ---------------------------
# GENERATE ROADMAP PAGE
# ---------------------------
def show_generate_page():
    st.markdown(
        '<div class="page-header">'
        '<div class="page-eyebrow">● Generate</div>'
        '<div class="page-title">Build Your Roadmap</div>'
        '<div class="page-desc">// Configure your learning parameters and let AI do the rest</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.divider()

    field = st.text_input("Target Field", placeholder="e.g., Machine Learning, Web Development, Data Science")

    col1, col2 = st.columns(2)
    with col1:
        level = st.selectbox("Skill Tier", ["Beginner", "Intermediate", "Advanced"])
    with col2:
        duration = st.number_input("Mission Duration (Weeks)", min_value=1, max_value=52, step=1, value=4)

    st.caption(f"// Will generate a {duration * 7}-day plan with daily objectives, curated resources, and mission modules.")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⬡ Generate Roadmap", use_container_width=True, type="primary"):
        if not field.strip():
            st.error("Please enter a target field.")
            return

        with st.spinner("AI is crafting your roadmap — this takes 20–30 seconds..."):
            try:
                roadmap = generate_roadmap(field, level, duration)
            except Exception as e:
                st.error(f"Generation failed: {e}")
                return

        file_data = load_data()
        user_email = st.session_state["user_email"]
        if user_email not in file_data:
            file_data[user_email] = []

        file_data[user_email].append({
            "field": field,
            "level": level,
            "duration": duration,
            "content": roadmap,
            "day_progress": []
        })
        save_data(file_data)

        st.session_state["generated_roadmap"] = roadmap
        st.session_state["field_name"] = field
        st.session_state["generated_roadmap_index"] = len(file_data[user_email]) - 1

        st.toast("Roadmap generated successfully 🎉")
        st.balloons()

    if "generated_roadmap" in st.session_state:
        st.divider()
        field_name = st.session_state.get("field_name", "")
        st.markdown(
            f'<div class="page-header" style="margin-bottom:12px">'
            f'<div class="page-eyebrow">● Result</div>'
            f'<div class="page-title" style="font-size:1.2rem">{field_name} Roadmap</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        render_roadmap(
            st.session_state["generated_roadmap"],
            user_email=st.session_state["user_email"],
            roadmap_index=st.session_state.get("generated_roadmap_index")
        )

        pdf_bytes = create_pdf(st.session_state["generated_roadmap"])
        st.download_button(
            label="⬡ Download Roadmap PDF",
            data=pdf_bytes,
            file_name=f"{st.session_state['field_name']}_roadmap.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ---------------------------
# PREVIOUS ROADMAPS
# ---------------------------
def show_previous_roadmaps():
    st.markdown(
        '<div class="page-header">'
        '<div class="page-eyebrow">● Archives</div>'
        '<div class="page-title">Mission Archives</div>'
        '<div class="page-desc">// All your saved learning roadmaps in one place</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.divider()

    file_data = load_data()
    user_email = st.session_state["user_email"]
    user_roadmaps = file_data.get(user_email, [])

    if not user_roadmaps:
        st.info("No roadmaps found. Generate your first one from the Generate page.")
        return

    st.caption(f"// {len(user_roadmaps)} saved roadmap(s) on record")
    st.markdown("<br>", unsafe_allow_html=True)

    for index, roadmap in enumerate(user_roadmaps):
        day_progress = roadmap.get("day_progress", [])
        total_days = roadmap.get("duration", 1) * 7
        pct = int(len(day_progress) / total_days * 100) if total_days > 0 else 0

        with st.expander(
            f"{roadmap['field']}  ·  {roadmap['level']}  ·  {roadmap['duration']}w  —  {pct}% complete"
        ):
            render_roadmap(roadmap["content"], user_email=user_email, roadmap_index=index)
            st.divider()

            col1, col2, col3 = st.columns(3)
            with col1:
                pdf_bytes = create_pdf(roadmap["content"])
                st.download_button(
                    "⬡ Export PDF",
                    data=pdf_bytes,
                    file_name=f"{roadmap['field']}_roadmap.pdf",
                    mime="application/pdf",
                    key=f"pdf_{index}",
                    use_container_width=True
                )
            with col2:
                if st.button("↻ Regenerate", key=f"regen_{index}", use_container_width=True):
                    with st.spinner("Regenerating roadmap..."):
                        new_content = generate_roadmap(
                            roadmap["field"], roadmap["level"], roadmap["duration"]
                        )
                    file_data[user_email][index]["content"] = new_content
                    file_data[user_email][index]["day_progress"] = []
                    save_data(file_data)
                    st.success("Roadmap regenerated.")
                    st.rerun()
            with col3:
                if st.button("✕ Delete", key=f"delete_{index}", use_container_width=True):
                    file_data[user_email].pop(index)
                    save_data(file_data)
                    st.success("Roadmap deleted.")
                    st.rerun()


# ---------------------------
# MAIN APP
# ---------------------------
def show_main_app():
    with st.sidebar:
        user_email = st.session_state.get("user_email", "")
        st.markdown(
            f'<div class="sb-brand">'
            f'<div class="sb-brand-name"><span class="sb-brand-dot"></span>Roadmap.AI</div>'
            f'<div class="sb-user">{user_email}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        menu = st.radio(
            "Navigation",
            ["🛸  Generate Roadmap", "📊  Dashboard", "📡  Mission Archives", "⏻  Logout"],
            label_visibility="collapsed"
        )

    if "Generate" in menu:
        show_generate_page()
    elif "Dashboard" in menu:
        show_dashboard()
    elif "Archives" in menu:
        show_previous_roadmaps()
    elif "Logout" in menu:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ---------------------------
# ROUTING
# ---------------------------
if st.session_state["user"] is None:
    show_auth()
else:
    show_main_app()

# import streamlit as st
# from database import create_tables
# from roadmap_engine import generate_roadmap, create_pdf
# from auth import register_user, login_user
# from dashboard import show_dashboard
# import json
# import os

# # ---------------------------
# # PAGE CONFIG (must be first)
# # ---------------------------
# st.set_page_config(
#     page_title="AI Roadmap Generator",
#     layout="wide",
#     page_icon="🛸"
# )

# # ---------------------------
# # CUSTOM CSS — Dark & Futuristic Space/Tech Theme
# # ---------------------------
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600&family=Share+Tech+Mono&display=swap');

# /* ── CSS Variables ── */
# :root {
#     --bg-void:       #020408;
#     --bg-deep:       #050c14;
#     --bg-panel:      #080f1a;
#     --bg-card:       #0a1628;
#     --border-glow:   #0ff;
#     --border-dim:    #1a3a5c;
#     --accent-cyan:   #00f5ff;
#     --accent-blue:   #0096ff;
#     --accent-purple: #7b2fff;
#     --accent-green:  #00ff88;
#     --accent-orange: #ff6b35;
#     --text-primary:  #e0f4ff;
#     --text-secondary:#7ab3d4;
#     --text-dim:      #3a6080;
#     --glow-cyan:     0 0 8px #00f5ff, 0 0 20px #00f5ff33;
#     --glow-blue:     0 0 8px #0096ff, 0 0 20px #0096ff33;
#     --glow-green:    0 0 8px #00ff88, 0 0 20px #00ff8833;
# }

# /* ── Global Reset ── */
# html, body, [class*="css"] {
#     font-family: 'Rajdhani', sans-serif !important;
#     background-color: var(--bg-void) !important;
#     color: var(--text-primary) !important;
# }

# /* ── Headings ── */
# h1, h2, h3, h4 {
#     font-family: 'Orbitron', monospace !important;
#     letter-spacing: 0.08em;
#     color: var(--accent-cyan) !important;
#     text-shadow: var(--glow-cyan);
# }

# /* ── Streamlit App Background ── */
# .stApp {
#     background: 
#         radial-gradient(ellipse at 20% 0%, #001428 0%, transparent 60%),
#         radial-gradient(ellipse at 80% 100%, #05002e 0%, transparent 60%),
#         var(--bg-void) !important;
# }

# /* Starfield simulation via pseudo-elements on body */
# .stApp::before {
#     content: '';
#     position: fixed;
#     inset: 0;
#     background-image:
#         radial-gradient(1px 1px at 10% 15%, #ffffff55 0%, transparent 100%),
#         radial-gradient(1px 1px at 25% 40%, #ffffff33 0%, transparent 100%),
#         radial-gradient(1px 1px at 40% 8%,  #ffffff44 0%, transparent 100%),
#         radial-gradient(1px 1px at 60% 30%, #ffffff22 0%, transparent 100%),
#         radial-gradient(1px 1px at 75% 60%, #ffffff44 0%, transparent 100%),
#         radial-gradient(1px 1px at 88% 20%, #ffffff33 0%, transparent 100%),
#         radial-gradient(1px 1px at 5%  70%, #ffffff22 0%, transparent 100%),
#         radial-gradient(1px 1px at 50% 85%, #ffffff33 0%, transparent 100%),
#         radial-gradient(1px 1px at 93% 75%, #ffffff44 0%, transparent 100%),
#         radial-gradient(2px 2px at 35% 55%, #00f5ff22 0%, transparent 100%),
#         radial-gradient(2px 2px at 70% 10%, #0096ff22 0%, transparent 100%);
#     pointer-events: none;
#     z-index: 0;
# }

# /* ── Sidebar ── */
# [data-testid="stSidebar"] {
#     background: linear-gradient(180deg, #050c14 0%, #020408 100%) !important;
#     border-right: 1px solid var(--border-dim) !important;
#     box-shadow: 4px 0 30px #00f5ff0a !important;
# }

# [data-testid="stSidebar"]::before {
#     content: '';
#     position: absolute;
#     top: 0; left: 0; right: 0;
#     height: 2px;
#     background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
#     animation: scanline 3s ease-in-out infinite;
# }

# @keyframes scanline {
#     0%, 100% { opacity: 0.3; }
#     50% { opacity: 1; }
# }

# /* ── Radio Buttons (Navigation) ── */
# [data-testid="stSidebar"] .stRadio > div {
#     gap: 4px;
# }
# [data-testid="stSidebar"] .stRadio label {
#     font-family: 'Rajdhani', sans-serif !important;
#     font-size: 0.95rem;
#     font-weight: 600;
#     letter-spacing: 0.05em;
#     color: var(--text-secondary) !important;
#     padding: 8px 12px;
#     border-radius: 4px;
#     border: 1px solid transparent;
#     transition: all 0.2s ease;
#     cursor: pointer;
# }
# [data-testid="stSidebar"] .stRadio label:hover {
#     color: var(--accent-cyan) !important;
#     border-color: var(--border-dim);
#     background: #0a1628;
#     text-shadow: var(--glow-cyan);
# }

# /* ── Buttons ── */
# .stButton > button {
#     font-family: 'Orbitron', monospace !important;
#     font-size: 0.75rem;
#     font-weight: 600;
#     letter-spacing: 0.12em;
#     background: linear-gradient(135deg, #001f3f 0%, #003366 100%) !important;
#     color: var(--accent-cyan) !important;
#     border: 1px solid var(--accent-cyan) !important;
#     border-radius: 4px !important;
#     text-transform: uppercase;
#     transition: all 0.25s ease !important;
#     box-shadow: 0 0 12px #00f5ff22 !important;
# }
# .stButton > button:hover {
#     background: linear-gradient(135deg, #003366 0%, #0066aa 100%) !important;
#     box-shadow: var(--glow-cyan) !important;
#     transform: translateY(-1px);
# }
# .stButton > button[kind="primary"] {
#     background: linear-gradient(135deg, #003a6e 0%, #0055a5 100%) !important;
#     box-shadow: 0 0 20px #0096ff44 !important;
# }
# .stButton > button[kind="primary"]:hover {
#     box-shadow: var(--glow-blue) !important;
# }

# /* ── Inputs ── */
# .stTextInput input, .stNumberInput input {
#     background: #080f1a !important;
#     border: 1px solid var(--border-dim) !important;
#     border-radius: 4px !important;
#     color: var(--text-primary) !important;
#     font-family: 'Rajdhani', sans-serif !important;
#     font-size: 1rem;
#     transition: border-color 0.2s, box-shadow 0.2s;
# }
# .stTextInput input:focus, .stNumberInput input:focus {
#     border-color: var(--accent-cyan) !important;
#     box-shadow: 0 0 10px #00f5ff33 !important;
# }

# /* ── Selectbox ── */
# .stSelectbox select,
# [data-testid="stSelectbox"] > div {
#     background: #080f1a !important;
#     border: 1px solid var(--border-dim) !important;
#     color: var(--text-primary) !important;
#     font-family: 'Rajdhani', sans-serif !important;
#     border-radius: 4px !important;
# }

# /* ── Progress Bar ── */
# .stProgress > div > div > div {
#     background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)) !important;
#     box-shadow: 0 0 10px var(--accent-cyan) !important;
#     border-radius: 2px !important;
# }
# .stProgress > div > div {
#     background: #0a1628 !important;
#     border: 1px solid var(--border-dim) !important;
#     border-radius: 2px !important;
# }

# /* ── Expander ── */
# .streamlit-expanderHeader {
#     background: #080f1a !important;
#     border: 1px solid var(--border-dim) !important;
#     border-radius: 4px !important;
#     color: var(--accent-blue) !important;
#     font-family: 'Rajdhani', sans-serif !important;
#     font-weight: 600;
#     letter-spacing: 0.05em;
#     transition: all 0.2s;
# }
# .streamlit-expanderHeader:hover {
#     border-color: var(--accent-cyan) !important;
#     color: var(--accent-cyan) !important;
#     box-shadow: 0 0 12px #00f5ff1a !important;
# }
# .streamlit-expanderContent {
#     background: #050c14 !important;
#     border: 1px solid var(--border-dim) !important;
#     border-top: none !important;
#     border-radius: 0 0 4px 4px !important;
# }

# /* ── Divider ── */
# hr {
#     border-color: var(--border-dim) !important;
#     opacity: 0.5;
# }

# /* ── Caption / Small text ── */
# .stCaption, small, caption {
#     color: var(--text-dim) !important;
#     font-family: 'Share Tech Mono', monospace !important;
#     font-size: 0.75rem !important;
# }

# /* ── Spinner ── */
# .stSpinner > div {
#     border-top-color: var(--accent-cyan) !important;
# }

# /* ── Toast / Alert ── */
# .stAlert {
#     background: #080f1a !important;
#     border: 1px solid var(--border-dim) !important;
#     border-radius: 4px !important;
#     color: var(--text-primary) !important;
# }

# /* ── Checkbox ── */
# .stCheckbox label {
#     color: var(--text-secondary) !important;
#     font-family: 'Rajdhani', sans-serif !important;
#     font-weight: 500;
# }

# /* ═══════════════════════════════════
#    COMPONENT CARDS
# ═══════════════════════════════════ */

# /* Week Header Card */
# .week-card {
#     background: linear-gradient(135deg, #040d1a 0%, #071425 50%, #040d1a 100%);
#     border: 1px solid var(--accent-cyan);
#     border-left: 3px solid var(--accent-cyan);
#     color: var(--accent-cyan);
#     padding: 0.9rem 1.5rem;
#     border-radius: 6px;
#     margin-bottom: 0.6rem;
#     font-family: 'Orbitron', monospace;
#     font-weight: 700;
#     font-size: 0.9rem;
#     letter-spacing: 0.1em;
#     text-transform: uppercase;
#     box-shadow: 0 0 20px #00f5ff0f, inset 0 0 20px #00f5ff05;
#     position: relative;
#     overflow: hidden;
# }
# .week-card::after {
#     content: '';
#     position: absolute;
#     top: 0; right: 0; bottom: 0;
#     width: 40%;
#     background: linear-gradient(90deg, transparent, #00f5ff08);
#     pointer-events: none;
# }

# /* Day Card */
# .day-card {
#     background: var(--bg-card);
#     border: 1px solid var(--border-dim);
#     border-left: 3px solid var(--accent-blue);
#     border-radius: 4px;
#     padding: 0.8rem 1rem;
#     margin: 0.5rem 0;
#     position: relative;
#     transition: border-color 0.2s, box-shadow 0.2s;
# }
# .day-card:hover {
#     border-color: var(--accent-blue);
#     box-shadow: 0 0 14px #0096ff18;
# }
# .day-card.completed {
#     border-left-color: var(--accent-green);
#     background: linear-gradient(135deg, #020f08 0%, #030e0a 100%);
#     box-shadow: 0 0 14px #00ff8818;
# }

# .day-title {
#     font-family: 'Rajdhani', sans-serif;
#     font-weight: 700;
#     color: var(--text-primary);
#     font-size: 1rem;
#     letter-spacing: 0.04em;
# }
# .day-meta {
#     color: var(--text-dim);
#     font-family: 'Share Tech Mono', monospace;
#     font-size: 0.72rem;
#     margin-top: 3px;
# }

# /* Topic Tags */
# .topic-tag {
#     display: inline-block;
#     background: #001a30;
#     color: var(--accent-blue);
#     border: 1px solid #1a3a6c;
#     border-radius: 2px;
#     padding: 2px 10px;
#     font-size: 0.72rem;
#     margin: 2px;
#     font-family: 'Share Tech Mono', monospace;
#     letter-spacing: 0.06em;
#     text-transform: uppercase;
# }

# /* Task Item */
# .task-item {
#     background: #050c14;
#     border: 1px solid var(--border-dim);
#     border-radius: 3px;
#     padding: 5px 10px;
#     margin: 4px 0;
#     font-size: 0.88rem;
#     color: var(--text-secondary);
#     font-family: 'Rajdhani', sans-serif;
#     font-weight: 500;
# }
# .task-item::before {
#     content: '▸ ';
#     color: var(--accent-cyan);
# }

# /* Resource Chips */
# .resource-chip {
#     display: inline-block;
#     border-radius: 3px;
#     padding: 3px 10px;
#     font-size: 0.72rem;
#     margin: 3px;
#     font-family: 'Share Tech Mono', monospace;
#     text-decoration: none;
#     letter-spacing: 0.05em;
#     border: 1px solid;
#     transition: box-shadow 0.2s;
# }
# .resource-chip:hover { filter: brightness(1.3); }
# .resource-chip.video   { background: #1a0005; color: #ff4060; border-color: #ff406055; }
# .resource-chip.article { background: #001a10; color: var(--accent-green); border-color: #00ff8844; }
# .resource-chip.course  { background: #001428; color: var(--accent-blue); border-color: #0096ff44; }
# .resource-chip.doc     { background: #0f0020; color: #b06aff; border-color: #7b2fff44; }
# .resource-chip.link    { background: #0a0a10; color: #aaa; border-color: #333; }

# /* Mini Project Box */
# .project-box {
#     background: linear-gradient(135deg, #05100a 0%, #030d07 100%);
#     border: 1px dashed #00ff8866;
#     border-radius: 6px;
#     padding: 1rem 1.2rem;
#     margin: 1rem 0;
#     box-shadow: 0 0 20px #00ff8809;
# }
# .project-title {
#     font-family: 'Orbitron', monospace;
#     font-weight: 700;
#     color: var(--accent-green);
#     font-size: 0.85rem;
#     letter-spacing: 0.08em;
#     text-transform: uppercase;
#     margin-bottom: 6px;
#     text-shadow: var(--glow-green);
# }

# /* Outcome Box */
# .outcome-box {
#     background: linear-gradient(135deg, #040b18 0%, #070f1e 100%);
#     border: 1px solid #0096ff55;
#     border-left: 4px solid var(--accent-blue);
#     color: var(--text-secondary);
#     border-radius: 6px;
#     padding: 1rem 1.5rem;
#     margin-bottom: 1.5rem;
#     font-size: 0.92rem;
#     line-height: 1.7;
#     font-family: 'Rajdhani', sans-serif;
#     box-shadow: 0 0 24px #0096ff0a;
# }
# .outcome-box b { color: var(--accent-cyan); font-family: 'Orbitron', monospace; font-size: 0.75rem; letter-spacing: 0.1em; }

# /* Stat Pill */
# .stat-pill {
#     display: inline-block;
#     background: #080f1a;
#     border: 1px solid var(--border-dim);
#     color: var(--accent-cyan);
#     border-radius: 2px;
#     padding: 5px 14px;
#     font-size: 0.75rem;
#     font-weight: 700;
#     font-family: 'Share Tech Mono', monospace;
#     letter-spacing: 0.08em;
#     margin: 2px;
#     box-shadow: 0 0 8px #00f5ff11;
# }

# /* ── Auth Page ── */
# .auth-logo {
#     text-align: center;
#     font-family: 'Orbitron', monospace;
#     font-weight: 900;
#     font-size: 2.4rem;
#     color: var(--accent-cyan);
#     text-shadow: 0 0 20px #00f5ff, 0 0 60px #00f5ff55;
#     letter-spacing: 0.15em;
#     text-transform: uppercase;
#     animation: pulseglow 3s ease-in-out infinite;
# }
# .auth-sub {
#     text-align: center;
#     color: var(--text-dim);
#     font-family: 'Share Tech Mono', monospace;
#     font-size: 0.8rem;
#     letter-spacing: 0.12em;
#     margin-bottom: 2rem;
#     text-transform: uppercase;
# }

# @keyframes pulseglow {
#     0%, 100% { text-shadow: 0 0 20px #00f5ff, 0 0 60px #00f5ff55; }
#     50%       { text-shadow: 0 0 30px #00f5ff, 0 0 80px #00f5ff88, 0 0 120px #00f5ff22; }
# }

# /* Auth container */
# .auth-panel {
#     background: linear-gradient(135deg, #050c14 0%, #080f1a 100%);
#     border: 1px solid var(--border-dim);
#     border-radius: 8px;
#     padding: 2rem;
#     box-shadow: 0 0 60px #00f5ff08, 0 0 120px #0096ff05;
# }

# /* ── Sidebar Logo ── */
# .sidebar-logo {
#     font-family: 'Orbitron', monospace;
#     font-weight: 900;
#     font-size: 1.1rem;
#     color: var(--accent-cyan);
#     text-shadow: var(--glow-cyan);
#     letter-spacing: 0.12em;
#     text-transform: uppercase;
#     margin-bottom: 2px;
# }
# .sidebar-user {
#     font-family: 'Share Tech Mono', monospace;
#     font-size: 0.72rem;
#     color: var(--text-dim);
#     letter-spacing: 0.06em;
# }

# /* ── Scrollbar ── */
# ::-webkit-scrollbar { width: 4px; }
# ::-webkit-scrollbar-track { background: var(--bg-void); }
# ::-webkit-scrollbar-thumb { background: var(--border-dim); border-radius: 2px; }
# ::-webkit-scrollbar-thumb:hover { background: var(--accent-cyan); }

# /* ── Download Button ── */
# [data-testid="stDownloadButton"] button {
#     font-family: 'Orbitron', monospace !important;
#     font-size: 0.7rem !important;
#     letter-spacing: 0.1em !important;
#     background: linear-gradient(135deg, #0a1a0a 0%, #0f2010 100%) !important;
#     color: var(--accent-green) !important;
#     border: 1px solid #00ff8866 !important;
#     box-shadow: 0 0 12px #00ff8811 !important;
# }
# [data-testid="stDownloadButton"] button:hover {
#     box-shadow: var(--glow-green) !important;
#     transform: translateY(-1px);
# }
# </style>
# """, unsafe_allow_html=True)

# # ---------------------------
# # SESSION STATE INIT
# # ---------------------------
# if "user" not in st.session_state:
#     st.session_state["user"] = None
# if "user_email" not in st.session_state:
#     st.session_state["user_email"] = None

# FILE_PATH = "data.json"

# def load_data():
#     if not os.path.exists(FILE_PATH):
#         return {}
#     with open(FILE_PATH, "r") as f:
#         return json.load(f)

# def save_data(data):
#     with open(FILE_PATH, "w") as f:
#         json.dump(data, f, indent=4)

# create_tables()

# # ---------------------------
# # SAVE DAY PROGRESS
# # ---------------------------

# def _save_day_progress(user_email, roadmap_index, progress_set):
#     file_data = load_data()
#     if user_email in file_data and roadmap_index < len(file_data[user_email]):
#         file_data[user_email][roadmap_index]["day_progress"] = list(progress_set)
#         save_data(file_data)

# # ---------------------------
# # RENDER ROADMAP
# # ---------------------------

# def render_roadmap(roadmap_json: str, user_email: str = None, roadmap_index: int = None):
#     try:
#         data_raw = json.loads(roadmap_json)
#     except Exception:
#         st.markdown(roadmap_json)
#         return

#     progress_key = f"progress_{roadmap_index}" if roadmap_index is not None else "progress_preview"

#     saved_progress = set()
#     if user_email and roadmap_index is not None:
#         file_data = load_data()
#         roadmaps = file_data.get(user_email, [])
#         if roadmap_index < len(roadmaps):
#             saved_progress = set(roadmaps[roadmap_index].get("day_progress", []))

#     if progress_key not in st.session_state:
#         st.session_state[progress_key] = saved_progress

#     outcome = data_raw.get("final_outcome", "")
#     if outcome:
#         st.markdown(
#             f'<div class="outcome-box">🎯 <b>MISSION OBJECTIVE</b><br>{outcome}</div>',
#             unsafe_allow_html=True
#         )

#     total_days = sum(len(w.get("days", [])) for w in data_raw.get("weeks", []))
#     total_hours = sum(
#         d.get("estimated_hours", 0)
#         for w in data_raw.get("weeks", [])
#         for d in w.get("days", [])
#     )
#     completed_days = len(st.session_state[progress_key])
#     progress_pct = (completed_days / total_days * 100) if total_days > 0 else 0

#     c1, c2, c3, c4 = st.columns(4)
#     with c1:  st.markdown(f'<span class="stat-pill">⬡ {data_raw.get("duration_weeks","?")} WEEKS</span>', unsafe_allow_html=True)
#     with c2:  st.markdown(f'<span class="stat-pill">◈ {total_days} DAYS</span>', unsafe_allow_html=True)
#     with c3:  st.markdown(f'<span class="stat-pill">⏱ ~{total_hours}H TOTAL</span>', unsafe_allow_html=True)
#     with c4:  st.markdown(f'<span class="stat-pill">✦ {completed_days}/{total_days} DONE</span>', unsafe_allow_html=True)

#     st.progress(progress_pct / 100, text=f"MISSION PROGRESS: {progress_pct:.1f}%")
#     st.divider()

#     for week in data_raw.get("weeks", []):
#         wn = week.get("week_number", "?")
#         theme = week.get("theme", "")
#         overview = week.get("overview", "")
#         week_days = week.get("days", [])

#         week_done = sum(1 for d in week_days if f"w{wn}d{d['day']}" in st.session_state[progress_key])
#         week_pct = int(week_done / len(week_days) * 100) if week_days else 0

#         st.markdown(
#             f'<div class="week-card">▶ PHASE {wn} — {theme.upper()} &nbsp;<span style="font-size:0.72rem;opacity:0.6;font-family:\'Share Tech Mono\',monospace">[{week_done}/{len(week_days)} · {week_pct}%]</span></div>',
#             unsafe_allow_html=True
#         )
#         if overview:
#             st.caption(f"// {overview}")

#         with st.expander(f"EXPAND PHASE {wn} — {len(week_days)} MODULES →", expanded=(wn == 1)):
#             for day in week_days:
#                 dn = day.get("day", "?")
#                 dtitle = day.get("title", "")
#                 topics = day.get("topics", [])
#                 tasks = day.get("tasks", [])
#                 resources = day.get("resources", [])
#                 hours = day.get("estimated_hours", "?")
#                 day_key = f"w{wn}d{dn}"
#                 is_done = day_key in st.session_state[progress_key]

#                 card_class = "day-card completed" if is_done else "day-card"
#                 check_icon = "✦ COMPLETE" if is_done else f"DAY {dn:02d}"

#                 st.markdown(
#                     f'<div class="{card_class}">'
#                     f'<div class="day-title">[{check_icon}] {dtitle}</div>'
#                     f'<div class="day-meta">⏱ ~{hours}h compute time</div>'
#                     f'</div>',
#                     unsafe_allow_html=True
#                 )

#                 if topics:
#                     tags_html = "".join(f'<span class="topic-tag">{t}</span>' for t in topics)
#                     st.markdown(f'<div style="margin:6px 0 10px 0">{tags_html}</div>', unsafe_allow_html=True)

#                 if tasks:
#                     st.markdown('<span style="font-family:\'Orbitron\',monospace;font-size:0.7rem;color:#0096ff;letter-spacing:0.1em">◈ OBJECTIVES</span>', unsafe_allow_html=True)
#                     for task in tasks:
#                         st.markdown(f'<div class="task-item">{task}</div>', unsafe_allow_html=True)

#                 if resources:
#                     st.markdown('<span style="font-family:\'Orbitron\',monospace;font-size:0.7rem;color:#0096ff;letter-spacing:0.1em">⬡ DATA LINKS</span>', unsafe_allow_html=True)
#                     chips = ""
#                     for r in resources:
#                         rtype = r.get("type", "link").lower()
#                         rtitle = r.get("title", "Resource")
#                         rurl = r.get("url", "#")
#                         chips += f'<a href="{rurl}" target="_blank" class="resource-chip {rtype}">{rtitle}</a> '
#                     st.markdown(f'<div style="margin:6px 0 14px 0">{chips}</div>', unsafe_allow_html=True)

#                 col_cb, _ = st.columns([1, 4])
#                 with col_cb:
#                     checked = st.checkbox(
#                         "✦ MARK COMPLETE" if not is_done else "✦ COMPLETED",
#                         value=is_done,
#                         key=f"cb_{progress_key}_{day_key}"
#                     )
#                     if checked and day_key not in st.session_state[progress_key]:
#                         st.session_state[progress_key].add(day_key)
#                         if user_email and roadmap_index is not None:
#                             _save_day_progress(user_email, roadmap_index, st.session_state[progress_key])
#                         st.rerun()
#                     elif not checked and day_key in st.session_state[progress_key]:
#                         st.session_state[progress_key].discard(day_key)
#                         if user_email and roadmap_index is not None:
#                             _save_day_progress(user_email, roadmap_index, st.session_state[progress_key])
#                         st.rerun()

#                 st.markdown('<hr style="border-color:#0a1628;margin:8px 0"/>', unsafe_allow_html=True)

#         mp = week.get("mini_project", {})
#         if mp:
#             st.markdown(
#                 f'<div class="project-box">'
#                 f'<div class="project-title">⬡ MISSION MODULE: {mp.get("title","").upper()}</div>'
#                 f'<div style="color:#7ab3d4;font-size:0.9rem;margin:6px 0;font-family:Rajdhani,sans-serif">{mp.get("description","")}</div>'
#                 f'<div style="color:#3a6080;font-size:0.78rem;margin-top:8px;font-family:\'Share Tech Mono\',monospace">// DELIVERABLE: {mp.get("deliverable","")}</div>'
#                 f'</div>',
#                 unsafe_allow_html=True
#             )
#         st.markdown("<br>", unsafe_allow_html=True)


# # ---------------------------
# # AUTH
# # ---------------------------

# def show_auth():
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         st.markdown("<br><br><br>", unsafe_allow_html=True)
#         st.markdown('<div class="auth-logo">🛸 ROADMAP.AI</div>', unsafe_allow_html=True)
#         st.markdown(
#             '<div class="auth-sub">▸ personalized mission pathways · powered by AI ◂</div>',
#             unsafe_allow_html=True
#         )
#         st.markdown("<br>", unsafe_allow_html=True)

#         choice = st.radio("", ["Login", "Signup"], horizontal=True, label_visibility="collapsed")
#         email = st.text_input("EMAIL", placeholder="operator@mission.io")
#         password = st.text_input("ACCESS CODE", type="password", placeholder="••••••••")

#         if choice == "Signup":
#             if st.button("INITIALIZE ACCOUNT", use_container_width=True, type="primary"):
#                 if not email or not password:
#                     st.error("⚠ All fields required.")
#                 elif len(password) < 6:
#                     st.error("⚠ Access code must be at least 6 characters.")
#                 else:
#                     success = register_user(email, password)
#                     if success:
#                         st.success("✦ Account created. Proceed to login.")
#                     else:
#                         st.error("⚠ Email already registered.")
#         else:
#             if st.button("AUTHENTICATE", use_container_width=True, type="primary"):
#                 if not email or not password:
#                     st.error("⚠ Credentials required.")
#                 else:
#                     user = login_user(email, password)
#                     if user:
#                         st.session_state["user"] = dict(user)
#                         st.session_state["user_email"] = email
#                         st.rerun()
#                     else:
#                         st.error("⚠ Authentication failed. Check credentials.")


# # ---------------------------
# # GENERATE ROADMAP PAGE
# # ---------------------------

# def show_generate_page():
#     st.markdown(
#         '<h1 style="font-size:1.6rem;letter-spacing:0.12em">🛸 GENERATE MISSION ROADMAP</h1>',
#         unsafe_allow_html=True
#     )
#     st.markdown(
#         '<p style="font-family:\'Share Tech Mono\',monospace;color:#3a6080;font-size:0.8rem;letter-spacing:0.06em">// Define parameters to generate your AI-powered day-by-day mission path</p>',
#         unsafe_allow_html=True
#     )
#     st.divider()

#     field = st.text_input("TARGET FIELD", placeholder="e.g., ML Engineer, Web Development, Data Science")
#     col1, col2 = st.columns(2)
#     with col1:
#         level = st.selectbox("SKILL TIER", ["Beginner", "Intermediate", "Advanced"])
#     with col2:
#         duration = st.number_input("MISSION DURATION (WEEKS)", min_value=1, max_value=52, step=1, value=4)

#     st.caption(f"// Will generate a {duration * 7}-day roadmap with daily tasks, resources, and mission modules.")

#     if st.button("⬡ GENERATE ROADMAP", use_container_width=True, type="primary"):
#         if not field.strip():
#             st.error("⚠ Target field is required.")
#             return

#         with st.spinner("// AI PROCESSING — crafting your mission roadmap..."):
#             try:
#                 roadmap = generate_roadmap(field, level, duration)
#             except Exception as e:
#                 st.error(f"⚠ Generation failed: {e}")
#                 return

#         file_data = load_data()
#         user_email = st.session_state["user_email"]
#         if user_email not in file_data:
#             file_data[user_email] = []

#         file_data[user_email].append({
#             "field": field,
#             "level": level,
#             "duration": duration,
#             "content": roadmap,
#             "day_progress": []
#         })
#         save_data(file_data)

#         st.session_state["generated_roadmap"] = roadmap
#         st.session_state["field_name"] = field
#         st.session_state["generated_roadmap_index"] = len(file_data[user_email]) - 1

#         st.toast("✦ Mission Roadmap Generated Successfully")
#         st.balloons()

#     if "generated_roadmap" in st.session_state:
#         st.divider()
#         st.markdown(
#             f'<h2 style="font-size:1.1rem;letter-spacing:0.1em">◈ {st.session_state.get("field_name","").upper()} — MISSION ROADMAP</h2>',
#             unsafe_allow_html=True
#         )

#         render_roadmap(
#             st.session_state["generated_roadmap"],
#             user_email=st.session_state["user_email"],
#             roadmap_index=st.session_state.get("generated_roadmap_index")
#         )

#         pdf_bytes = create_pdf(st.session_state["generated_roadmap"])
#         st.download_button(
#             label="⬡ DOWNLOAD ROADMAP PDF",
#             data=pdf_bytes,
#             file_name=f"{st.session_state['field_name']}_roadmap.pdf",
#             mime="application/pdf",
#             use_container_width=True
#         )


# # ---------------------------
# # PREVIOUS ROADMAPS
# # ---------------------------

# def show_previous_roadmaps():
#     st.markdown('<h1 style="font-size:1.6rem;letter-spacing:0.12em">📡 MISSION ARCHIVES</h1>', unsafe_allow_html=True)
#     st.divider()

#     file_data = load_data()
#     user_email = st.session_state["user_email"]
#     user_roadmaps = file_data.get(user_email, [])

#     if not user_roadmaps:
#         st.info("// No missions found. Generate your first roadmap.")
#         return

#     st.markdown(
#         f'<p style="font-family:\'Share Tech Mono\',monospace;color:#3a6080;font-size:0.8rem">// {len(user_roadmaps)} saved mission(s) on record</p>',
#         unsafe_allow_html=True
#     )

#     for index, roadmap in enumerate(user_roadmaps):
#         day_progress = roadmap.get("day_progress", [])
#         total_days = roadmap.get("duration", 1) * 7
#         pct = int(len(day_progress) / total_days * 100) if total_days > 0 else 0

#         with st.expander(f"▶ [{roadmap['field'].upper()}] · {roadmap['level'].upper()} · {roadmap['duration']}W  —  {pct}% COMPLETE"):
#             render_roadmap(roadmap["content"], user_email=user_email, roadmap_index=index)
#             st.divider()

#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 pdf_bytes = create_pdf(roadmap["content"])
#                 st.download_button(
#                     "⬡ EXPORT PDF", data=pdf_bytes,
#                     file_name=f"{roadmap['field']}_roadmap.pdf",
#                     mime="application/pdf", key=f"pdf_{index}",
#                     use_container_width=True
#                 )
#             with col2:
#                 if st.button("↻ REGENERATE", key=f"regen_{index}", use_container_width=True):
#                     with st.spinner("// Regenerating mission..."):
#                         new_content = generate_roadmap(roadmap["field"], roadmap["level"], roadmap["duration"])
#                     file_data[user_email][index]["content"] = new_content
#                     file_data[user_email][index]["day_progress"] = []
#                     save_data(file_data)
#                     st.success("✦ Mission regenerated.")
#                     st.rerun()
#             with col3:
#                 if st.button("✕ TERMINATE", key=f"delete_{index}", use_container_width=True):
#                     file_data[user_email].pop(index)
#                     save_data(file_data)
#                     st.success("// Mission record deleted.")
#                     st.rerun()


# # ---------------------------
# # MAIN APP
# # ---------------------------

# def show_main_app():
#     with st.sidebar:
#         st.markdown(
#             '<div class="sidebar-logo">🛸 ROADMAP.AI</div>'
#             f'<div class="sidebar-user">▸ {st.session_state.get("user_email","")}</div>',
#             unsafe_allow_html=True
#         )
#         st.divider()
#         menu = st.radio(
#             "NAV",
#             ["🛸 Generate Roadmap", "📊 Dashboard", "📡 Mission Archives", "⏻ Logout"],
#             label_visibility="collapsed"
#         )

#     if menu == "🛸 Generate Roadmap":
#         show_generate_page()
#     elif menu == "📊 Dashboard":
#         show_dashboard()
#     elif menu == "📡 Mission Archives":
#         show_previous_roadmaps()
#     elif menu == "⏻ Logout":
#         for key in list(st.session_state.keys()):
#             del st.session_state[key]
#         st.rerun()


# # ---------------------------
# # ROUTING
# # ---------------------------

# if st.session_state["user"] is None:
#     show_auth()
# else:
#     show_main_app()

# import streamlit as st
# from database import create_tables
# from roadmap_engine import generate_roadmap, create_pdf
# from auth import register_user, login_user
# from dashboard import show_dashboard
# import json
# import os

# # ---------------------------
# # PAGE CONFIG (must be first)
# # ---------------------------
# st.set_page_config(
#     page_title="AI Roadmap Generator",
#     layout="wide",
#     page_icon="🗺️"
# )

# # ---------------------------
# # CUSTOM CSS
# # ---------------------------
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

# html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
# h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

# .week-card {
#     background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
#     color: white;
#     padding: 1rem 1.5rem;
#     border-radius: 12px;
#     margin-bottom: 0.5rem;
#     font-family: 'Space Grotesk', sans-serif;
#     font-weight: 600;
#     font-size: 1.1rem;
# }

# .day-card {
#     background: #f8f9ff;
#     border-left: 4px solid #4a4a8a;
#     border-radius: 0 10px 10px 0;
#     padding: 0.75rem 1rem;
#     margin: 0.5rem 0;
# }

# .day-card.completed { border-left-color: #27ae60; background: #f0fff4; }

# .day-title { font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: #1a1a2e; font-size: 0.95rem; }
# .day-meta { color: #7c7c9e; font-size: 0.78rem; margin-top: 2px; }

# .topic-tag {
#     display: inline-block;
#     background: #e8e8ff;
#     color: #4a4a8a;
#     border-radius: 20px;
#     padding: 3px 10px;
#     font-size: 0.78rem;
#     margin: 2px;
#     font-weight: 500;
# }

# .task-item {
#     background: #fff;
#     border: 1px solid #e8e8ff;
#     border-radius: 8px;
#     padding: 6px 10px;
#     margin: 4px 0;
#     font-size: 0.85rem;
#     color: #333;
# }

# .resource-chip {
#     display: inline-block;
#     background: #1a1a2e;
#     color: white;
#     border-radius: 6px;
#     padding: 4px 10px;
#     font-size: 0.75rem;
#     margin: 3px;
#     text-decoration: none;
# }
# .resource-chip.video { background: #c0392b; }
# .resource-chip.article { background: #27ae60; }
# .resource-chip.course { background: #2980b9; }
# .resource-chip.doc { background: #8e44ad; }

# .project-box {
#     background: linear-gradient(135deg, #f0f0ff 0%, #e8e8ff 100%);
#     border: 2px dashed #4a4a8a;
#     border-radius: 12px;
#     padding: 1rem 1.2rem;
#     margin: 1rem 0;
# }
# .project-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #1a1a2e; font-size: 1rem; margin-bottom: 4px; }

# .outcome-box {
#     background: linear-gradient(135deg, #1a1a2e 0%, #4a4a8a 100%);
#     color: white;
#     border-radius: 12px;
#     padding: 1rem 1.5rem;
#     margin-bottom: 1.5rem;
#     font-size: 0.9rem;
#     line-height: 1.6;
# }

# .stat-pill {
#     display: inline-block;
#     background: #f0f0ff;
#     color: #4a4a8a;
#     border-radius: 20px;
#     padding: 4px 14px;
#     font-size: 0.82rem;
#     font-weight: 600;
#     margin: 2px;
# }
# </style>
# """, unsafe_allow_html=True)

# # ---------------------------
# # SESSION STATE INIT
# # ---------------------------
# if "user" not in st.session_state:
#     st.session_state["user"] = None
# if "user_email" not in st.session_state:
#     st.session_state["user_email"] = None

# FILE_PATH = "data.json"

# def load_data():
#     if not os.path.exists(FILE_PATH):
#         return {}
#     with open(FILE_PATH, "r") as f:
#         return json.load(f)

# def save_data(data):
#     with open(FILE_PATH, "w") as f:
#         json.dump(data, f, indent=4)

# create_tables()

# # ---------------------------
# # SAVE DAY PROGRESS
# # ---------------------------

# def _save_day_progress(user_email, roadmap_index, progress_set):
#     file_data = load_data()
#     if user_email in file_data and roadmap_index < len(file_data[user_email]):
#         file_data[user_email][roadmap_index]["day_progress"] = list(progress_set)
#         save_data(file_data)

# # ---------------------------
# # RENDER ROADMAP
# # ---------------------------

# def render_roadmap(roadmap_json: str, user_email: str = None, roadmap_index: int = None):
#     try:
#         data_raw = json.loads(roadmap_json)
#     except Exception:
#         st.markdown(roadmap_json)
#         return

#     progress_key = f"progress_{roadmap_index}" if roadmap_index is not None else "progress_preview"

#     # Load saved progress from file
#     saved_progress = set()
#     if user_email and roadmap_index is not None:
#         file_data = load_data()
#         roadmaps = file_data.get(user_email, [])
#         if roadmap_index < len(roadmaps):
#             saved_progress = set(roadmaps[roadmap_index].get("day_progress", []))

#     if progress_key not in st.session_state:
#         st.session_state[progress_key] = saved_progress

#     # Stats
#     outcome = data_raw.get("final_outcome", "")
#     if outcome:
#         st.markdown(f'<div class="outcome-box">🎯 <b>Final Outcome:</b><br>{outcome}</div>', unsafe_allow_html=True)

#     total_days = sum(len(w.get("days", [])) for w in data_raw.get("weeks", []))
#     total_hours = sum(
#         d.get("estimated_hours", 0)
#         for w in data_raw.get("weeks", [])
#         for d in w.get("days", [])
#     )
#     completed_days = len(st.session_state[progress_key])
#     progress_pct = (completed_days / total_days * 100) if total_days > 0 else 0

#     c1, c2, c3, c4 = st.columns(4)
#     with c1: st.markdown(f'<span class="stat-pill">📅 {data_raw.get("duration_weeks","?")} Weeks</span>', unsafe_allow_html=True)
#     with c2: st.markdown(f'<span class="stat-pill">📆 {total_days} Days</span>', unsafe_allow_html=True)
#     with c3: st.markdown(f'<span class="stat-pill">⏱ ~{total_hours}h Total</span>', unsafe_allow_html=True)
#     with c4: st.markdown(f'<span class="stat-pill">✅ {completed_days}/{total_days} Done</span>', unsafe_allow_html=True)

#     st.progress(progress_pct / 100, text=f"Overall Progress: {progress_pct:.1f}%")
#     st.divider()

#     # Weeks
#     for week in data_raw.get("weeks", []):
#         wn = week.get("week_number", "?")
#         theme = week.get("theme", "")
#         overview = week.get("overview", "")
#         week_days = week.get("days", [])

#         week_done = sum(1 for d in week_days if f"w{wn}d{d['day']}" in st.session_state[progress_key])
#         week_pct = int(week_done / len(week_days) * 100) if week_days else 0

#         st.markdown(
#             f'<div class="week-card">📅 Week {wn}: {theme} &nbsp;<span style="font-size:0.8rem;opacity:0.7">{week_done}/{len(week_days)} days · {week_pct}%</span></div>',
#             unsafe_allow_html=True
#         )
#         if overview:
#             st.caption(f"📌 {overview}")

#         with st.expander(f"View all {len(week_days)} days →", expanded=(wn == 1)):
#             for day in week_days:
#                 dn = day.get("day", "?")
#                 dtitle = day.get("title", "")
#                 topics = day.get("topics", [])
#                 tasks = day.get("tasks", [])
#                 resources = day.get("resources", [])
#                 hours = day.get("estimated_hours", "?")
#                 day_key = f"w{wn}d{dn}"
#                 is_done = day_key in st.session_state[progress_key]

#                 card_class = "day-card completed" if is_done else "day-card"
#                 check_icon = "✅" if is_done else f"Day {dn}"

#                 st.markdown(
#                     f'<div class="{card_class}">'
#                     f'<div class="day-title">{check_icon} — {dtitle}</div>'
#                     f'<div class="day-meta">⏱ ~{hours} hours</div>'
#                     f'</div>',
#                     unsafe_allow_html=True
#                 )

#                 if topics:
#                     tags_html = "".join(f'<span class="topic-tag">📘 {t}</span>' for t in topics)
#                     st.markdown(f'<div style="margin:4px 0 8px 0">{tags_html}</div>', unsafe_allow_html=True)

#                 if tasks:
#                     st.markdown("**🎯 Tasks:**")
#                     for task in tasks:
#                         st.markdown(f'<div class="task-item">◦ {task}</div>', unsafe_allow_html=True)

#                 if resources:
#                     st.markdown("**🔗 Resources:**")
#                     chips = ""
#                     for r in resources:
#                         rtype = r.get("type", "link").lower()
#                         rtitle = r.get("title", "Resource")
#                         rurl = r.get("url", "#")
#                         chips += f'<a href="{rurl}" target="_blank" class="resource-chip {rtype}">{rtitle}</a> '
#                     st.markdown(f'<div style="margin:4px 0 12px 0">{chips}</div>', unsafe_allow_html=True)

#                 col_cb, _ = st.columns([1, 4])
#                 with col_cb:
#                     checked = st.checkbox(
#                         "Completed ✓" if is_done else "Mark complete",
#                         value=is_done,
#                         key=f"cb_{progress_key}_{day_key}"
#                     )
#                     if checked and day_key not in st.session_state[progress_key]:
#                         st.session_state[progress_key].add(day_key)
#                         if user_email and roadmap_index is not None:
#                             _save_day_progress(user_email, roadmap_index, st.session_state[progress_key])
#                         st.rerun()
#                     elif not checked and day_key in st.session_state[progress_key]:
#                         st.session_state[progress_key].discard(day_key)
#                         if user_email and roadmap_index is not None:
#                             _save_day_progress(user_email, roadmap_index, st.session_state[progress_key])
#                         st.rerun()

#                 st.markdown("---")

#         mp = week.get("mini_project", {})
#         if mp:
#             st.markdown(
#                 f'<div class="project-box">'
#                 f'<div class="project-title">🛠 Mini Project: {mp.get("title","")}</div>'
#                 f'<div style="color:#333;font-size:0.87rem;margin:4px 0">{mp.get("description","")}</div>'
#                 f'<div style="color:#7c7c9e;font-size:0.82rem;margin-top:6px">📦 Deliverable: {mp.get("deliverable","")}</div>'
#                 f'</div>',
#                 unsafe_allow_html=True
#             )
#         st.markdown("<br>", unsafe_allow_html=True)


# # ---------------------------
# # AUTH
# # ---------------------------

# def show_auth():
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         st.markdown("<br><br>", unsafe_allow_html=True)
#         st.markdown(
#             '<div style="text-align:center;font-size:2.5rem;font-family:Space Grotesk,sans-serif;font-weight:700;color:#1a1a2e">🗺️ AI Roadmap Generator</div>',
#             unsafe_allow_html=True
#         )
#         st.markdown(
#             '<div style="text-align:center;color:#7c7c9e;margin-bottom:2rem">Your personalized day-by-day learning path, powered by AI</div>',
#             unsafe_allow_html=True
#         )
#         choice = st.radio("", ["Login", "Signup"], horizontal=True, label_visibility="collapsed")
#         email = st.text_input("📧 Email", placeholder="you@example.com")
#         password = st.text_input("🔑 Password", type="password", placeholder="••••••••")

#         if choice == "Signup":
#             if st.button("Create Account", use_container_width=True, type="primary"):
#                 if not email or not password:
#                     st.error("Please enter both email and password.")
#                 elif len(password) < 6:
#                     st.error("Password must be at least 6 characters.")
#                 else:
#                     success = register_user(email, password)
#                     if success:
#                         st.success("Account created! Please login.")
#                     else:
#                         st.error("Email already exists.")
#         else:
#             if st.button("Login", use_container_width=True, type="primary"):
#                 if not email or not password:
#                     st.error("Please fill in all fields.")
#                 else:
#                     user = login_user(email, password)
#                     if user:
#                         st.session_state["user"] = dict(user)
#                         st.session_state["user_email"] = email
#                         st.rerun()
#                     else:
#                         st.error("Invalid credentials.")


# # ---------------------------
# # GENERATE ROADMAP PAGE
# # ---------------------------

# def show_generate_page():
#     st.title("🚀 Generate Roadmap")
#     st.write("Fill in the details to get your personalized day-by-day learning roadmap.")
#     st.divider()

#     field = st.text_input("🎯 Enter Field", placeholder="e.g., ML Engineer, Web Development, Data Science")
#     col1, col2 = st.columns(2)
#     with col1:
#         level = st.selectbox("📊 Select Level", ["Beginner", "Intermediate", "Advanced"])
#     with col2:
#         duration = st.number_input("📅 Number of Weeks", min_value=1, max_value=52, step=1, value=4)

#     st.caption(f"This will generate a **{duration * 7}-day** roadmap with daily tasks, resources, and mini projects.")

#     if st.button("✨ Generate Roadmap", use_container_width=True, type="primary"):
#         if not field.strip():
#             st.error("Please enter a field name.")
#             return

#         with st.spinner("🤖 AI is crafting your roadmap... This may take 20-30 seconds."):
#             try:
#                 roadmap = generate_roadmap(field, level, duration)
#             except Exception as e:
#                 st.error(f"Error generating roadmap: {e}")
#                 return

#         file_data = load_data()
#         user_email = st.session_state["user_email"]
#         if user_email not in file_data:
#             file_data[user_email] = []

#         file_data[user_email].append({
#             "field": field,
#             "level": level,
#             "duration": duration,
#             "content": roadmap,
#             "day_progress": []
#         })
#         save_data(file_data)

#         st.session_state["generated_roadmap"] = roadmap
#         st.session_state["field_name"] = field
#         st.session_state["generated_roadmap_index"] = len(file_data[user_email]) - 1

#         st.toast("Roadmap Generated Successfully 🎉")
#         st.balloons()

#     if "generated_roadmap" in st.session_state:
#         st.divider()
#         st.subheader(f"📋 {st.session_state.get('field_name', '')} Roadmap")

#         render_roadmap(
#             st.session_state["generated_roadmap"],
#             user_email=st.session_state["user_email"],
#             roadmap_index=st.session_state.get("generated_roadmap_index")
#         )

#         pdf_bytes = create_pdf(st.session_state["generated_roadmap"])
#         st.download_button(
#             label="📥 Download Roadmap as PDF",
#             data=pdf_bytes,
#             file_name=f"{st.session_state['field_name']}_roadmap.pdf",
#             mime="application/pdf",
#             use_container_width=True
#         )


# # ---------------------------
# # PREVIOUS ROADMAPS
# # ---------------------------

# def show_previous_roadmaps():
    
#     st.title("📚 Previous Roadmaps")
#     st.divider()

#     file_data = load_data()
#     user_email = st.session_state["user_email"]
#     user_roadmaps = file_data.get(user_email, [])

#     if not user_roadmaps:
#         st.info("No roadmaps found. Generate your first one!")
#         return

#     st.write(f"You have **{len(user_roadmaps)}** saved roadmap(s).")

#     for index, roadmap in enumerate(user_roadmaps):
#         day_progress = roadmap.get("day_progress", [])
#         total_days = roadmap.get("duration", 1) * 7
#         pct = int(len(day_progress) / total_days * 100) if total_days > 0 else 0

#         with st.expander(f"📌 {roadmap['field']} | {roadmap['level']} | {roadmap['duration']} Weeks  —  {pct}% complete"):
#             render_roadmap(roadmap["content"], user_email=user_email, roadmap_index=index)
#             st.divider()

#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 pdf_bytes = create_pdf(roadmap["content"])
#                 st.download_button(
#                     "📥 Download PDF", data=pdf_bytes,
#                     file_name=f"{roadmap['field']}_roadmap.pdf",
#                     mime="application/pdf", key=f"pdf_{index}",
#                     use_container_width=True
#                 )
#             with col2:
#                 if st.button("🔄 Regenerate", key=f"regen_{index}", use_container_width=True):
#                     with st.spinner("Regenerating..."):
#                         new_content = generate_roadmap(roadmap["field"], roadmap["level"], roadmap["duration"])
#                     file_data[user_email][index]["content"] = new_content
#                     file_data[user_email][index]["day_progress"] = []
#                     save_data(file_data)
#                     st.success("Roadmap regenerated!")
#                     st.rerun()
#             with col3:
#                 if st.button("🗑 Delete", key=f"delete_{index}", use_container_width=True):
#                     file_data[user_email].pop(index)
#                     save_data(file_data)
#                     st.success("Deleted!")
#                     st.rerun()


# # ---------------------------
# # MAIN APP
# # ---------------------------

# def show_main_app():
#     with st.sidebar:
        
#         st.markdown(
#             '<div style="font-family:Space Grotesk,sans-serif;font-weight:700;font-size:1.2rem;color:#1a1a2e;margin-bottom:4px">🗺️ Roadmap AI</div>',
#             unsafe_allow_html=True
#         )
#         st.caption(f"👤 {st.session_state.get('user_email', '')}")
#         st.divider()
#         menu = st.radio(
#             "Navigation",
#             ["🚀 Generate Roadmap", "📊 Dashboard", "📚 Previous Roadmaps", "🚪 Logout"]
#         )
 

#     if menu == "🚀 Generate Roadmap":
#         show_generate_page()
#     elif menu == "📊 Dashboard":
#        show_dashboard()
#        st.markdown('</div>', unsafe_allow_html=True)    
#     elif menu == "📚 Previous Roadmaps":
#        show_previous_roadmaps()
#     elif menu == "🚪 Logout":
#      for key in list(st.session_state.keys()):
#             del st.session_state[key]
#     st.rerun()


# # ---------------------------
# # ROUTING
# # ---------------------------

# if st.session_state["user"] is None:
#     show_auth()
# else:
#     show_main_app()

