import os
import re
import io
import json
import time
from urllib.parse import quote_plus
# from dotenv import load_dotenv
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import streamlit as st

def get_api_key():
    try:
        return st.secrets["GROQ_API_KEY"]   # Streamlit Cloud
    except Exception:
        return os.getenv("GROQ_API_KEY")

# load_dotenv()

AI_PROVIDER = "groq"


# ══════════════════════════════════════════════════════════════════
# UNIVERSAL URL BUILDER
# Works for ANY topic — programming, design, music, cooking, etc.
# Strategy:
#   video   → YouTube search (precise query = top result is always relevant)
#   article → Best platform for the field (GFG, MDN, etc.) or Google
#   course  → Best course platform for the field
#   doc     → DevDocs or official docs search
# ══════════════════════════════════════════════════════════════════

def yt(query: str) -> str:
    """YouTube search URL — always returns relevant results for any topic."""
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"

def gfg(query: str) -> str:
    return f"https://www.geeksforgeeks.org/search/?q={quote_plus(query)}"

def mdn(query: str) -> str:
    return f"https://developer.mozilla.org/en-US/search?q={quote_plus(query)}"

def google(query: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(query)}"

def coursera(query: str) -> str:
    return f"https://www.coursera.org/search?query={quote_plus(query)}"

def udemy(query: str) -> str:
    return f"https://www.udemy.com/courses/search/?q={quote_plus(query)}"

def freecodecamp(query: str) -> str:
    return f"https://www.freecodecamp.org/news/search/?query={quote_plus(query)}"

def realpython(query: str) -> str:
    return f"https://realpython.com/search?q={quote_plus(query)}"

def w3schools(query: str) -> str:
    return f"https://www.w3schools.com/search/search_result.asp?search={quote_plus(query)}"

def devdocs(query: str) -> str:
    return f"https://devdocs.io/#q={quote_plus(query)}"

def youtube_search(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"

def khan(query: str) -> str:
    return f"https://www.khanacademy.org/search?page_search_query={quote_plus(query)}"

def edx(query: str) -> str:
    return f"https://www.edx.org/search?q={quote_plus(query)}"

def mit_ocw(query: str) -> str:
    return f"https://ocw.mit.edu/search/?q={quote_plus(query)}"


# ── All supported site_hint values ────────────────────────────────
SITE_BUILDERS = {
    "youtube":         yt,
    "geeksforgeeks":   gfg,
    "realpython":      realpython,
    "mdn":             mdn,
    "w3schools":       w3schools,
    "freecodecamp":    freecodecamp,
    "devdocs":         devdocs,
    "coursera":        coursera,
    "udemy":           udemy,
    "edx":             edx,
    "khanacademy":     khan,
    "mit_ocw":         mit_ocw,
    "cs50":            lambda _: "https://cs50.harvard.edu/x/",
    "python_docs":     lambda q: f"https://docs.python.org/3/search.html?q={quote_plus(q)}",
    "javascript_info": lambda q: f"https://javascript.info/search?query={quote_plus(q)}",
    "kaggle":          lambda q: f"https://www.kaggle.com/search?q={quote_plus(q)}",
    "leetcode":        lambda q: f"https://leetcode.com/search/?q={quote_plus(q)}",
    "github":          lambda q: f"https://github.com/search?q={quote_plus(q)}&type=repositories",
    "google":          google,
}

# ── Field-category → best default sites ──────────────────────────
# Used when AI doesn't provide a site_hint or provides an unknown one.
# Covers programming, but also non-tech fields via "default".
FIELD_SITE_MAP = {
    # Programming languages
    "python":           {"article": "realpython",     "course": "coursera",     "doc": "python_docs"},
    "java":             {"article": "geeksforgeeks",  "course": "udemy",        "doc": "devdocs"},
    "javascript":       {"article": "mdn",            "course": "freecodecamp", "doc": "mdn"},
    "typescript":       {"article": "mdn",            "course": "udemy",        "doc": "mdn"},
    "c++":              {"article": "geeksforgeeks",  "course": "udemy",        "doc": "devdocs"},
    "c#":               {"article": "geeksforgeeks",  "course": "udemy",        "doc": "devdocs"},
    "go":               {"article": "geeksforgeeks",  "course": "udemy",        "doc": "devdocs"},
    "rust":             {"article": "geeksforgeeks",  "course": "udemy",        "doc": "devdocs"},
    "kotlin":           {"article": "geeksforgeeks",  "course": "udemy",        "doc": "devdocs"},
    "swift":            {"article": "geeksforgeeks",  "course": "udemy",        "doc": "devdocs"},
    "php":              {"article": "w3schools",      "course": "udemy",        "doc": "devdocs"},
    "ruby":             {"article": "geeksforgeeks",  "course": "udemy",        "doc": "devdocs"},
    # Frameworks / tech
    "react":            {"article": "freecodecamp",   "course": "udemy",        "doc": "mdn"},
    "node":             {"article": "freecodecamp",   "course": "udemy",        "doc": "mdn"},
    "web":              {"article": "mdn",            "course": "freecodecamp", "doc": "mdn"},
    "html":             {"article": "mdn",            "course": "freecodecamp", "doc": "mdn"},
    "css":              {"article": "mdn",            "course": "freecodecamp", "doc": "mdn"},
    "sql":              {"article": "w3schools",      "course": "coursera",     "doc": "devdocs"},
    "database":         {"article": "geeksforgeeks",  "course": "coursera",     "doc": "devdocs"},
    "django":           {"article": "realpython",     "course": "udemy",        "doc": "devdocs"},
    "flask":            {"article": "realpython",     "course": "udemy",        "doc": "devdocs"},
    "spring":           {"article": "geeksforgeeks",  "course": "udemy",        "doc": "devdocs"},
    # CS topics
    "data structure":   {"article": "geeksforgeeks",  "course": "coursera",     "doc": "devdocs"},
    "algorithm":        {"article": "geeksforgeeks",  "course": "coursera",     "doc": "devdocs"},
    "dsa":              {"article": "geeksforgeeks",  "course": "coursera",     "doc": "devdocs"},
    # ML / AI
    "machine learning": {"article": "geeksforgeeks",  "course": "coursera",     "doc": "devdocs"},
    "deep learning":    {"article": "geeksforgeeks",  "course": "coursera",     "doc": "devdocs"},
    "data science":     {"article": "kaggle",         "course": "coursera",     "doc": "devdocs"},
    "artificial intel": {"article": "geeksforgeeks",  "course": "coursera",     "doc": "devdocs"},
    # DevOps / Cloud
    "devops":           {"article": "freecodecamp",   "course": "udemy",        "doc": "devdocs"},
    "docker":           {"article": "freecodecamp",   "course": "udemy",        "doc": "devdocs"},
    "kubernetes":       {"article": "freecodecamp",   "course": "udemy",        "doc": "devdocs"},
    "aws":              {"article": "freecodecamp",   "course": "udemy",        "doc": "devdocs"},
    "cloud":            {"article": "freecodecamp",   "course": "coursera",     "doc": "devdocs"},
    # Non-tech / universal fallback
    "default":          {"article": "google",         "course": "coursera",     "doc": "google"},
}

def get_sites(field: str) -> dict:
    """Return best site mapping for this field."""
    fl = field.lower()
    for key in FIELD_SITE_MAP:
        if key in fl:
            return FIELD_SITE_MAP[key]
    return FIELD_SITE_MAP["default"]


# ══════════════════════════════════════════════════════════════════
# RESOURCE PROCESSOR
# Converts AI resource metadata → real working URLs.
# Works for ANY field — tech or non-tech.
# ══════════════════════════════════════════════════════════════════

def build_video_url(title: str, search_query: str, field: str) -> str:
    """
    Build a YouTube search URL that surfaces the best, most relevant video.
    Format: "<topic> <field> tutorial" → precise results, not music/random.
    """
    # Clean up the query — add field context if not already present
    fl = field.lower()
    sq = search_query.strip()

    # If the search_query already contains the field name, use as-is
    # Otherwise append it for precision
    if fl not in sq.lower() and len(fl.split()) <= 3:
        sq = f"{sq} {field}"

    # Always append "tutorial" if not already there — filters out music/unrelated
    if "tutorial" not in sq.lower() and "course" not in sq.lower() and "learn" not in sq.lower():
        sq = f"{sq} tutorial"

    return yt(sq)


def build_article_url(title: str, search_query: str, site_hint: str, field: str) -> str:
    """Build article URL on the best platform for this field."""
    sites = get_sites(field)
    site  = site_hint if site_hint in SITE_BUILDERS else sites.get("article", "google")
    return SITE_BUILDERS[site](search_query)


def build_course_url(title: str, search_query: str, site_hint: str, field: str) -> str:
    """Build course URL on the best platform for this field."""
    sites = get_sites(field)
    site  = site_hint if site_hint in SITE_BUILDERS else sites.get("course", "coursera")
    return SITE_BUILDERS[site](search_query)


def build_doc_url(title: str, search_query: str, site_hint: str, field: str) -> str:
    """Build documentation URL."""
    sites = get_sites(field)
    site  = site_hint if site_hint in SITE_BUILDERS else sites.get("doc", "google")
    return SITE_BUILDERS[site](search_query)


def process_resources(resources: list, day_title: str, topics: list, field: str) -> list:
    """
    Convert AI resource metadata into working URLs.
    Guarantees: 1 video + 1 article + 1 course/doc per day.
    Works for ANY subject — coding, design, music, cooking, finance, etc.
    """
    processed   = []
    has_video   = False
    has_article = False
    has_course  = False

    for r in resources:
        rtype        = r.get("type", "link").lower()
        title        = r.get("title", "Resource")
        search_query = (r.get("search_query") or r.get("query") or
                        f"{day_title} {field}").strip()
        site_hint    = r.get("site_hint", "")

        if rtype == "video" and not has_video:
            processed.append({
                "type":  "video",
                "title": title,
                "url":   build_video_url(title, search_query, field)
            })
            has_video = True

        elif rtype == "article" and not has_article:
            processed.append({
                "type":  "article",
                "title": title,
                "url":   build_article_url(title, search_query, site_hint, field)
            })
            has_article = True

        elif rtype in ("course", "doc") and not has_course:
            if rtype == "doc":
                url = build_doc_url(title, search_query, site_hint, field)
            else:
                url = build_course_url(title, search_query, site_hint, field)
            processed.append({"type": rtype, "title": title, "url": url})
            has_course = True

    # ── Guarantee at least 1 video ──────────────────────────────
    if not has_video:
        sq = f"{day_title} {field} tutorial"
        processed.insert(0, {
            "type":  "video",
            "title": f"{day_title} – Video Tutorial",
            "url":   yt(sq)
        })

    # ── Guarantee at least 1 article ────────────────────────────
    if not has_article:
        sites = get_sites(field)
        site  = sites.get("article", "google")
        processed.append({
            "type":  "article",
            "title": f"{day_title} – Article",
            "url":   SITE_BUILDERS[site](f"{day_title} {field}")
        })

    # ── Guarantee at least 1 course ─────────────────────────────
    if not has_course:
        sites = get_sites(field)
        site  = sites.get("course", "coursera")
        processed.append({
            "type":  "course",
            "title": f"{field} Course",
            "url":   SITE_BUILDERS[site](f"{field} {day_title}")
        })

    return processed


# ══════════════════════════════════════════════════════════════════
# POST-PROCESS: run after AI generates roadmap JSON
# ══════════════════════════════════════════════════════════════════

def post_process_roadmap(roadmap_json: str, field: str) -> str:
    try:
        data = json.loads(roadmap_json)
    except Exception:
        return roadmap_json

    for week in data.get("weeks", []):
        for day in week.get("days", []):
            day["resources"] = process_resources(
                day.get("resources", []),
                day.get("title", ""),
                day.get("topics", []),
                field
            )
    return json.dumps(data)


# ══════════════════════════════════════════════════════════════════
# MAIN PUBLIC FUNCTION
# ══════════════════════════════════════════════════════════════════

def generate_roadmap(field: str, level: str, duration: int) -> str:
    if AI_PROVIDER == "groq":
        raw = groq_generate(field, level, duration)
    elif AI_PROVIDER == "gemini":
        raw = gemini_generate(field, level, duration)
    elif AI_PROVIDER == "openai":
        raw = openai_generate(field, level, duration)
    else:
        raise ValueError(f"Unknown AI provider: {AI_PROVIDER}")
    return post_process_roadmap(raw, field)


# ══════════════════════════════════════════════════════════════════
# PROMPT — universal, works for any field
# ══════════════════════════════════════════════════════════════════

def build_prompt(field: str, level: str, duration: int) -> str:
    return f"""Create a detailed, day-by-day learning roadmap in STRICT JSON format.

Field: {field}
Level: {level}
Duration: {duration} weeks (exactly {duration * 7} days total)

Return ONLY valid JSON — no markdown fences, no explanation, no extra text before or after.

JSON structure:
{{
  "field": "{field}",
  "level": "{level}",
  "duration_weeks": {duration},
  "final_outcome": "2-3 sentences describing what the learner will achieve by the end",
  "weeks": [
    {{
      "week_number": 1,
      "theme": "Short descriptive theme for this week",
      "overview": "1-2 sentences about what this week covers",
      "days": [
        {{
          "day": 1,
          "title": "Specific title for what is learned today",
          "topics": ["specific topic 1", "specific topic 2"],
          "tasks": [
            "Concrete actionable task 1",
            "Concrete actionable task 2",
            "Concrete actionable task 3"
          ],
          "resources": [
            {{
              "type": "video",
              "title": "Descriptive title of the best video for this exact topic",
              "search_query": "exact topic name beginner tutorial {field}",
              "site_hint": "youtube"
            }},
            {{
              "type": "article",
              "title": "Descriptive article title for this topic",
              "search_query": "exact topic name {field}",
              "site_hint": "geeksforgeeks"
            }},
            {{
              "type": "course",
              "title": "Best course title for this topic",
              "search_query": "exact topic name {field} course",
              "site_hint": "coursera"
            }}
          ],
          "estimated_hours": 2
        }}
      ],
      "mini_project": {{
        "title": "Mini project title",
        "description": "What to build/create and why it reinforces learning",
        "deliverable": "Specific output the learner should produce"
      }}
    }}
  ]
}}

STRICT RULES:
1. EXACTLY {duration} weeks, EXACTLY 7 days per week — no exceptions
2. Day 7 of each week = lighter review/practice/consolidation day
3. estimated_hours per day: between 1 and 4
4. Tasks: minimum 3 per day, concrete and actionable (not vague like "learn about X")
5. Resources: EXACTLY 3 per day — one video, one article, one course
6. search_query: MUST be very specific to that day's exact topic.
   Good: "python list comprehension tutorial for beginners"
   Bad:  "python tutorial"
7. site_hint: pick the most appropriate from this list:
   youtube, geeksforgeeks, realpython, mdn, w3schools, freecodecamp,
   python_docs, javascript_info, devdocs, coursera, udemy, edx,
   khanacademy, mit_ocw, cs50, kaggle, leetcode, google
   → Use "google" as site_hint for non-technical fields (design, music, business, etc.)
8. Do NOT include a "url" field — URLs are built automatically from search_query + site_hint
9. The roadmap must be tailored specifically to "{field}" — not generic programming content
10. For non-technical fields (music, cooking, design, business, finance, fitness, etc.),
    use site_hint "youtube" for videos and "google" for articles/courses
"""


# ══════════════════════════════════════════════════════════════════
# GROQ
# ══════════════════════════════════════════════════════════════════

def groq_generate(field: str, level: str, duration: int) -> str:
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file.")

    client = Groq(api_key=api_key)
    prompt = build_prompt(field, level, duration)
    MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
    ]

    last_error = None
    for model in MODELS:
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert curriculum designer and career mentor. "
                                "You create detailed learning roadmaps for ANY subject — "
                                "technical or non-technical. "
                                "Respond with valid JSON only — no markdown, no extra text. "
                                "Each resource must have: type, title, search_query, site_hint. "
                                "Do NOT include a url field. "
                                "Make search_query very specific to the day's exact topic."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=8000,
                )
                raw = response.choices[0].message.content.strip()
                raw = re.sub(r"^```json\s*", "", raw)
                raw = re.sub(r"^```\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                raw = raw.strip()
                json.loads(raw)  # validate
                return raw

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if "rate_limit" in err_str or "429" in err_str or "503" in err_str:
                    time.sleep(2 * (attempt + 1))
                    continue
                elif "model_not_found" in err_str or "404" in err_str:
                    break
                else:
                    raise

    raise ValueError(
        f"All Groq models failed. Last error: {last_error}\n\n"
        "Check your GROQ_API_KEY in .env and try again."
    )


# ══════════════════════════════════════════════════════════════════
# GEMINI
# ══════════════════════════════════════════════════════════════════

def gemini_generate(field: str, level: str, duration: int) -> str:
    try:
        from google import genai as google_genai
    except ImportError:
        raise ValueError("Run: pip install google-genai")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")

    client = google_genai.Client(api_key=api_key)
    prompt = build_prompt(field, level, duration)
    MODELS = [
        "gemini-2.5-flash-preview-04-17",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ]

    last_error = None
    for model in MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                raw = response.text.strip()
                raw = re.sub(r"^```json\s*", "", raw)
                raw = re.sub(r"^```\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                json.loads(raw)
                return raw
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(2 * (attempt + 1))
                    continue
                elif "404" in err_str or "NOT_FOUND" in err_str:
                    break
                else:
                    raise

    raise ValueError(f"All Gemini models unavailable. Last error: {last_error}")


# ══════════════════════════════════════════════════════════════════
# OPENAI
# ══════════════════════════════════════════════════════════════════

def openai_generate(field: str, level: str, duration: int) -> str:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert curriculum designer. Return only valid JSON."},
            {"role": "user",   "content": build_prompt(field, level, duration)}
        ]
    )
    return response.choices[0].message.content


# ══════════════════════════════════════════════════════════════════
# PDF CREATION
# ══════════════════════════════════════════════════════════════════

def create_pdf(roadmap_json: str) -> bytes:
    buffer = io.BytesIO()
    try:
        data = json.loads(roadmap_json)
    except Exception:
        return _plain_pdf(roadmap_json)

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch,   bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()

    title_style   = ParagraphStyle("T", parent=styles["Title"],   fontSize=22, textColor=colors.HexColor("#1a1a2e"), spaceAfter=4)
    sub_style     = ParagraphStyle("S", parent=styles["Normal"],  fontSize=11, textColor=colors.HexColor("#4a4a8a"), spaceAfter=14)
    week_style    = ParagraphStyle("W", parent=styles["Heading1"],fontSize=14, textColor=colors.HexColor("#1a1a2e"), spaceBefore=18, spaceAfter=6)
    day_style     = ParagraphStyle("D", parent=styles["Heading2"],fontSize=12, textColor=colors.HexColor("#16213e"), spaceBefore=10, spaceAfter=4)
    label_style   = ParagraphStyle("L", parent=styles["Normal"],  fontSize=8,  textColor=colors.HexColor("#7c7c9e"), spaceBefore=5, spaceAfter=2, fontName="Helvetica-Bold")
    body_style    = ParagraphStyle("B", parent=styles["Normal"],  fontSize=10, textColor=colors.HexColor("#333333"), spaceAfter=2, leftIndent=10)
    project_style = ParagraphStyle("P", parent=styles["Normal"],  fontSize=10, textColor=colors.HexColor("#1a1a2e"), spaceBefore=8, leftIndent=10, spaceAfter=4)

    elements = []
    elements.append(Paragraph(f"{data.get('field', 'Learning')} Roadmap", title_style))
    elements.append(Paragraph(f"{data.get('level', '')} Level · {data.get('duration_weeks', '?')} Weeks", sub_style))
    if data.get("final_outcome"):
        elements.append(Paragraph(f"<b>Goal:</b> {data['final_outcome']}", body_style))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e")))
    elements.append(Spacer(1, 0.1 * inch))

    for week in data.get("weeks", []):
        elements.append(Paragraph(
            f"Week {week.get('week_number', '?')}: {week.get('theme', '')}", week_style))
        if week.get("overview"):
            elements.append(Paragraph(week["overview"], body_style))

        for day in week.get("days", []):
            elements.append(Paragraph(
                f"Day {day.get('day', '?')}: {day.get('title', '')}  [{day.get('estimated_hours', '')}h]",
                day_style))

            if day.get("topics"):
                elements.append(Paragraph("TOPICS", label_style))
                for t in day["topics"]:
                    elements.append(Paragraph(f"• {t}", body_style))

            if day.get("tasks"):
                elements.append(Paragraph("TASKS", label_style))
                for t in day["tasks"]:
                    elements.append(Paragraph(f"✓ {t}", body_style))

            if day.get("resources"):
                elements.append(Paragraph("RESOURCES", label_style))
                for r in day["resources"]:
                    elements.append(Paragraph(
                        f"[{r.get('type','').upper()}] "
                        f"<a href='{r.get('url','')}' color='#2980b9'>{r.get('title','')}</a>",
                        body_style))

        mp = week.get("mini_project", {})
        if mp:
            elements.append(Spacer(1, 0.1 * inch))
            elements.append(Paragraph(
                f"<b>🛠 Mini Project: {mp.get('title', '')}</b><br/>"
                f"{mp.get('description', '')}<br/>"
                f"<i>Deliverable: {mp.get('deliverable', '')}</i>",
                project_style))

        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


def _plain_pdf(text: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []
    for line in text.split("\n"):
        line = re.sub(r"^#+\s*", "", line.strip()).replace("**", "")
        if line:
            elements.append(Paragraph(line, styles["Normal"]))
        else:
            elements.append(Spacer(1, 0.1 * inch))
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()

