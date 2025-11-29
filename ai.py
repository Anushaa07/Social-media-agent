import streamlit as st
from groq import Groq
from requests.exceptions import RequestException
import re
import pandas as pd
import datetime

# === CONFIG & CLIENT INITIALIZATION ===
import os
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

TONES = ["Formal", "Funny", "Casual", "Professional", "Inspirational"]

PLATFORM_OPTIONS = [
    "📸 Instagram",
    "▶️ YouTube",
    "🐦 Twitter",
    "👔 LinkedIn"
]

# === SESSION STATE INIT ===
if 'ideas_output' not in st.session_state:
    st.session_state['ideas_output'] = None
if 'platform_used_name' not in st.session_state:
    st.session_state['platform_used_name'] = ""
if 'topic_used' not in st.session_state:
    st.session_state['topic_used'] = ""
if 'tone_used' not in st.session_state:
    st.session_state['tone_used'] = ""
if 'scheduler' not in st.session_state:
    st.session_state['scheduler'] = []

# === SAFE GROQ WRAPPER ===
def safe_groq_chat(prompt, system="You are a helpful assistant. Respond concisely."):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# === AI LOGIC ===
def generate_content_ideas(topic, platform_name, tone):
    prompt = (
        f"Generate 5 creative professional ideas for {platform_name} about {topic}. "
        f"Use a {tone.lower()} tone. Number them 1-5 with short title + 1–2 sentence description."
    )
    return safe_groq_chat(prompt)

def generate_caption_and_hashtags(idea, platform_name, tone):
    prompt = (
        f"Write a caption + hashtags for {platform_name}.\nIdea: {idea}\n"
        f"Tone: {tone.lower()}.\nCaption first, hashtags second line."
    )
    return safe_groq_chat(prompt)

def generate_hooks_for_idea(idea, tone, count=8):
    prompt = (
        f"Generate {count} short hooks for:\n{idea}\nTone: {tone.lower()}.\n"
        "Hooks: 3–10 words. One per line."
    )
    return safe_groq_chat(prompt)

def repurpose_for_platform(idea, target_platform, tone):
    instr = {
        "twitter": "Write a tweet under 280 chars with 2–4 hashtags.",
        "linkedin": "Write a 60–150 word LinkedIn post with value & CTA.",
        "youtube": "Write a 45–60 sec YouTube Shorts script."
    }.get(target_platform.lower(), "Adapt this idea concisely.")
    prompt = f"Adapt this idea for {target_platform}:\n{idea}\n{instr}\nTone: {tone.lower()}."
    return safe_groq_chat(prompt)

def evaluate_content_strength(title, caption, platform_name, tone):
    prompt = (
        f"Evaluate post for {platform_name}.\n"
        "Return:\nScore: <0-100>\nReasons:\n- ...\nSuggestions:\n- ...\n"
        f"Title: {title}\nCaption: {caption}\nTone: {tone}"
    )
    return safe_groq_chat(prompt)

def generate_scheduler_plan(topic, platform_name, tone, days=30):
    prompt = (
        f"Create a {days}-day plan for {platform_name} on {topic}. "
        "Format: Day <n>: <short title> – <1 sentence instruction>."
    )
    return safe_groq_chat(prompt)

# === PARSER HELPERS ===
def parse_ideas(text):
    ideas = []
    parts = re.split(r'\n?\s*\d+\.\s*', text)
    for part in parts:
        s = part.strip()
        if not s:
            continue
        if ':' in s:
            title, desc = s.split(':', 1)
        else:
            s_split = re.split(r'(?<=[.!?]) +', s)
            title = s_split[0]
            desc = " ".join(s_split[1:]) if len(s_split) > 1 else ""
        ideas.append((title.strip(), desc.strip()))
    return ideas

def split_caption_and_hashtags(text):
    if not text:
        return "", ""
    lines = text.split("\n")
    caption = lines[0].strip()
    hashtags = lines[1].strip() if len(lines) > 1 else ""
    return caption, hashtags

def parse_score_response(text):
    if not text:
        return None, [], []
    m = re.search(r'Score\s*[:\-]\s*(\d{1,3})', text)
    score = int(m.group(1)) if m else None
    score = max(0, min(100, score)) if score is not None else None

    reasons_block = re.search(r'Reasons\s*[:\-](.*?)(Suggestions|$)', text, re.S)
    suggestions_block = re.search(r'Suggestions\s*[:\-](.*)', text, re.S)

    reasons = []
    suggestions = []

    if reasons_block:
        reasons_raw = reasons_block.group(1).strip()
        reasons = [r.strip("- ").strip() for r in reasons_raw.split("\n") if r.strip()]

    if suggestions_block:
        sugs_raw = suggestions_block.group(1).strip()
        suggestions = [s.strip("- ").strip() for s in sugs_raw.split("\n") if s.strip()]

    return score, reasons, suggestions

# === THEME PACK 2 — MINIMAL PRO (APPLIED) ===
st.set_page_config(page_title="AI Social Media Agent", layout="wide")

st.markdown("""
<style>
/* App background */
.stApp {
    background: #f7f9fc;
    color: #2b2b2b;
    font-family: 'Inter', sans-serif;
}

/* Headings */
h1, h2, h3 {
    color: #111;
}

/* Expanders */
div[data-testid="stExpander"] {
    background: #ffffff;
    border-radius: 10px;
    border: 1px solid #e3e6eb;
    box-shadow: 0px 3px 8px rgba(0,0,0,0.04);
    padding: 10px;
}

/* Buttons */
.stButton>button {
    background: #eef4ff;
    color: #111;
    border: 1px solid #d0d8ff;
    border-radius: 8px;
}
.stButton>button:hover {
    background: #dce7ff;
}

/* Table Background */
[data-testid="stTable"] {
    background: white !important;
}
</style>
""", unsafe_allow_html=True)

# === LAYOUT ===
col_input, col_output = st.columns([1, 3])

# ========== LEFT PANEL ========== #
with col_input:
    st.header("Parameters")

    topic = st.text_input("Topic (e.g., sustainable fashion)")
    platform_with_emoji = st.selectbox("Platform", PLATFORM_OPTIONS)
    platform_name = platform_with_emoji.split(" ")[1]
    tone = st.selectbox("Tone/style", TONES, index=3)

    st.markdown("---")

    generate_btn = st.button("Generate Content Ideas", use_container_width=True)

    st.markdown("---")
    st.subheader("Scheduler")

    main_scheduler_date = st.date_input("Pick a date to preview/add", value=datetime.date.today())
    scheduler_view_days = st.selectbox("View schedule range", ["7 days", "30 days"])

    if st.button("Show Schedule"):
        # Updated replacement for deprecated st.experimental_set_query_params
        st.query_params.update({"show_schedule": "1"})

# ========== RIGHT PANEL ========== #
with col_output:
    st.title("🤖 AI Social Media Agent")
    st.caption("Generates ideas, hooks, repurposes, evaluates strength, and schedules posts.")

    st.markdown("---")

    # No ideas yet
    if st.session_state['ideas_output'] is None:
        st.info("Enter parameters and click Generate.")
    else:
        st.markdown(f"### {st.session_state['topic_used']} — Ideas for {st.session_state['platform_used_name']}")

        # Render ideas
        for idx, (title, description) in enumerate(st.session_state['ideas_output'], start=1):
            with st.expander(f"{idx}. {title}"):
                st.markdown(f"**Summary:** {description}")

                cap_key = f"caption_{idx}"
                if cap_key in st.session_state:
                    caption, hashtags = split_caption_and_hashtags(st.session_state[cap_key])
                    st.markdown("**Caption Preview:**")
                    st.code(caption)
                    st.markdown("**Hashtags:**")
                    st.code(hashtags)
                else:
                    st.info("Click Generate Caption.")

                # Action row
                a1, a2, a3, a4, a5 = st.columns(5)

                if a1.button("Generate Caption", key=f"capbtn_{idx}"):
                    out = generate_caption_and_hashtags(f"{title}: {description}", platform_name, tone)
                    st.session_state[cap_key] = out

                if a2.button("Generate Hooks", key=f"hooksbtn_{idx}"):
                    st.session_state[f"hooks_{idx}"] = generate_hooks_for_idea(f"{title}: {description}", tone)

                if a3.button("Twitter", key=f"twt_{idx}"):
                    st.session_state[f"rep_twitter_{idx}"] = repurpose_for_platform(f"{title}: {description}", "Twitter", tone)

                if a4.button("LinkedIn", key=f"ln_{idx}"):
                    st.session_state[f"rep_linkedin_{idx}"] = repurpose_for_platform(f"{title}: {description}", "LinkedIn", tone)

                if a5.button("YouTube", key=f"yt_{idx}"):
                    st.session_state[f"rep_youtube_{idx}"] = repurpose_for_platform(f"{title}: {description}", "YouTube", tone)

                # Hooks
                if f"hooks_{idx}" in st.session_state:
                    st.markdown("**Hooks:**")
                    st.text(st.session_state[f"hooks_{idx}"])

                # Repurposed
                for p in ["twitter", "linkedin", "youtube"]:
                    k = f"rep_{p}_{idx}"
                    if k in st.session_state:
                        st.markdown(f"**{p.capitalize()} Version:**")
                        st.code(st.session_state[k])

                # Evaluate
                if st.button("Evaluate Strength", key=f"eval_{idx}"):
                    if cap_key not in st.session_state:
                        st.session_state[cap_key] = generate_caption_and_hashtags(f"{title}: {description}", platform_name, tone)
                    caption, _ = split_caption_and_hashtags(st.session_state[cap_key])
                    eval_raw = evaluate_content_strength(title, caption, platform_name, tone)
                    score, reasons, suggestions = parse_score_response(eval_raw)
                    st.session_state[f"eval_score_{idx}"] = score
                    st.session_state[f"eval_reasons_{idx}"] = reasons
                    st.session_state[f"eval_suggestions_{idx}"] = suggestions

                if f"eval_score_{idx}" in st.session_state:
                    st.markdown(f"**Score:** {st.session_state[f'eval_score_{idx}']}/100")
                    st.markdown("**Reasons:**")
                    for r in st.session_state[f"eval_reasons_{idx}"]:
                        st.markdown("- " + r)
                    st.markdown("**Suggestions:**")
                    for s in st.session_state[f"eval_suggestions_{idx}"]:
                        st.markdown("- " + s)

                # Add to scheduler
                if st.button("Add to Scheduler", key=f"addsch_{idx}"):
                    caption, hashtags = split_caption_and_hashtags(st.session_state.get(cap_key, ""))
                    st.session_state['scheduler'].append({
                        "date": main_scheduler_date.isoformat(),
                        "platform": platform_name,
                        "title": title,
                        "caption": caption,
                        "hashtags": hashtags
                    })
                    st.success(f"Added to {main_scheduler_date}")

                st.markdown("---")

    # ========== SCHEDULER ==========
    st.header("Content Scheduler")

    if not st.session_state['scheduler']:
        st.info("No scheduled posts.")
    else:
        df = pd.DataFrame(st.session_state['scheduler'])
        df['date'] = pd.to_datetime(df['date']).dt.date
        df = df.sort_values("date")
        st.table(df)

    st.markdown("---")
    st.subheader("Bulk Tools")

    b1, b2, b3 = st.columns(3)

    if b1.button("Generate 30-day Plan"):
        st.session_state['bulk_plan'] = generate_scheduler_plan(st.session_state.get('topic_used', topic), platform_name, tone)

    if b2.button("Export CSV"):
        if st.session_state['scheduler']:
            csv = pd.DataFrame(st.session_state['scheduler']).to_csv(index=False)
            st.download_button("Download CSV", csv, file_name="schedule.csv")
        else:
            st.warning("Scheduler empty.")

    if b3.button("Clear Scheduler"):
        st.session_state['scheduler'] = []
        st.success("Scheduler cleared.")

    if 'bulk_plan' in st.session_state:
        st.code(st.session_state['bulk_plan'])

# ========== MAIN GENERATE BUTTON ==========
if generate_btn:
    if not topic.strip():
        st.error("Enter a topic first.")
    else:
        # Clear caches
        for key in list(st.session_state.keys()):
            if key.startswith(("caption_", "hooks_", "rep_", "eval_")):
                del st.session_state[key]

        st.session_state['platform_used_name'] = platform_name
        st.session_state['topic_used'] = topic
        st.session_state['tone_used'] = tone

        with st.spinner("Generating ideas..."):
            raw = generate_content_ideas(topic, platform_name, tone)

        parsed = parse_ideas(raw)
        st.session_state['ideas_output'] = parsed
        st.success("Ideas generated.")
