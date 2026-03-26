import json
import re
import anthropic
import streamlit as st
from datetime import date


def process_profile(profile_text: str, api_key: str, url: str = None) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    today_str = date.today().strftime("%B %d, %Y")
    url_context = f"\nLinkedIn URL: {url}" if url else ""

    system_prompt = (
        "You are an expert at analysing LinkedIn profiles for investor pitch deck team slides. "
        "Always respond with a single valid JSON object and nothing else."
    )

    user_prompt = f"""Analyse this LinkedIn profile and return a JSON object for a pitch deck team slide.

Today's date: {today_str}{url_context}

LinkedIn Profile Text:
---
{profile_text}
---

Return ONLY a valid JSON object with this exact structure (no markdown, no explanation):
{{
  "designation": "Current job title only — never include the company name",
  "years_experience": "X years",
  "first_job_date": "Month Year",
  "one_line_summary": "5–8 word punchy summary highlighting pedigree",
  "experience_highlights": [
    {{"company": "Company Name", "role": "Job Title"}},
    {{"company": "Company Name", "role": "Job Title"}}
  ],
  "education": [
    {{"degree": "Degree, Field", "institution": "Institution Name"}},
    {{"degree": "Degree, Field", "institution": "Institution Name"}}
  ]
}}

RULES — follow exactly:

DESIGNATION
- Job title only. Never include the company name.
- Correct: "Co-Founder & CEO"   Wrong: "Co-Founder & CEO at Acme Corp"

YEARS_EXPERIENCE
- Count from the START DATE of their very first job to today ({today_str}).
- Round to the nearest whole year (8.5 → 9). Format as "X years".
- If exact start date is missing, estimate from context (graduation year, other dates).

FIRST_JOB_DATE
- Month and year of their very first job, e.g. "June 2010".

ONE_LINE_SUMMARY
- 5–8 words. Specific and punchy — name well-known employers, # of exits/IPOs, prestigious degrees, or scale of impact.
- Good: "Ex-McKinsey partner, scaled 3 unicorns" / "MIT PhD, 2 exits, built Google Maps"
- Bad: "Experienced leader with 10+ years" (too vague)

EXPERIENCE_HIGHLIGHTS
- Include ONLY companies that satisfy BOTH:
  1. WELL-KNOWN: Fortune 500, major tech (Google, Meta, Apple, Microsoft, Amazon, Netflix,
     Uber, Airbnb, Stripe, Palantir, Spotify, Twitter/X, Snap, LinkedIn, Salesforce, Oracle,
     SAP), top consulting (McKinsey, BCG, Bain, Deloitte, Accenture, Oliver Wyman),
     top banks/finance (Goldman Sachs, JPMorgan, Morgan Stanley, Citi, BlackRock,
     Bridgewater, Sequoia, a16z, SoftBank), well-known unicorns with exits,
     military officer roles, prominent government, major media (NYT, BBC, Bloomberg).
  2. SENIOR / MANAGERIAL: C-suite (CEO/CTO/COO/CFO/CMO/CPO/CRO), VP/SVP/EVP,
     Director/Senior Director/Managing Director, Senior [any], Lead [any],
     Principal [any], Head of [any], General Manager, Founder/Co-Founder,
     Partner (consulting/law/VC).
     EXCLUDE: Intern, Analyst (entry-level), Associate (entry-level IC),
     Junior [any], Trainee, Engineer without Senior/Lead/Principal prefix.
- Maximum 4 entries. Fewer is fine.
- If nothing qualifies, return an empty array [].

EDUCATION
- Include ALL degrees (bachelor's, master's, MBA, PhD, etc.).
- Format degree as: "MBA", "B.Tech, Computer Science", "PhD, Physics", "B.A., Economics".
- Include all institutions regardless of prestige.
"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = ""
    for block in message.content:
        if block.type == "text":
            raw = block.text.strip()
            break

    if not raw:
        raise ValueError("No response received from Claude.")

    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw).strip()

    return json.loads(raw)


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Team Profile Generator | Deck Rooster",
    page_icon="🐓",
    layout="centered",
)

# ── Deck Rooster brand styles ─────────────────────────────────────────────────
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
    :root {
        --dr-off-white:   #fcf7ea;
        --dr-classic:     #f6f1e2;
        --dr-green:       #16c64f;
        --dr-sacramento:  #008440;
        --dr-forest:      #144b3e;
        --dr-onyx:        #30473f;
        --dr-taupe:       #cbc3ae;
    }

    html, body, [class*="css"] {
        font-family: 'Lora', Georgia, serif;
        color: var(--dr-onyx);
    }

    .stApp { background-color: var(--dr-off-white); }

    h1, h2, h3, h4,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Plus Jakarta Sans', Arial, sans-serif !important;
        color: var(--dr-forest) !important;
    }

    .stButton > button {
        background-color: var(--dr-green) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 24px !important;
        font-family: 'Plus Jakarta Sans', Arial, sans-serif !important;
        font-weight: 600 !important;
        padding: 0.55rem 2rem !important;
        transition: background-color 0.2s ease;
    }
    .stButton > button:hover:not(:disabled) {
        background-color: var(--dr-sacramento) !important;
    }
    .stButton > button:disabled {
        opacity: 0.45 !important;
    }

    .stTextInput  > div > div > input,
    .stTextArea   > div > div > textarea {
        border-radius: 8px !important;
        border: 1px solid var(--dr-taupe) !important;
        background-color: var(--dr-classic) !important;
        font-family: 'Lora', Georgia, serif !important;
        color: var(--dr-onyx) !important;
    }
    .stTextInput  > div > div > input:focus,
    .stTextArea   > div > div > textarea:focus {
        border-color: var(--dr-green) !important;
        box-shadow: 0 0 0 2px rgba(22,198,79,0.18) !important;
    }

    details > summary,
    .streamlit-expanderHeader {
        font-family: 'Plus Jakarta Sans', Arial, sans-serif !important;
        color: var(--dr-onyx) !important;
    }

    hr { border-color: var(--dr-taupe) !important; }

    .dr-label {
        font-family: 'Plus Jakarta Sans', Arial, sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--dr-sacramento);
        margin: 1.1rem 0 0.15rem;
    }

    .dr-note {
        background: var(--dr-classic);
        border-left: 3px solid var(--dr-green);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-top: 1.25rem;
    }
    .dr-note .note-label {
        font-family: 'Plus Jakarta Sans', Arial, sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--dr-sacramento);
    }
    .dr-note .note-body {
        font-family: 'Lora', Georgia, serif;
        font-size: 0.9rem;
        color: var(--dr-onyx);
        margin-top: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; padding: 2rem 0 1.5rem;">
        <h1 style="font-family:'Plus Jakarta Sans',Arial,sans-serif;
                   color:#144b3e; font-size:2.1rem; margin-bottom:0.4rem;">
            Team Profile Generator
        </h1>
        <p style="font-family:'Lora',Georgia,serif; color:#30473f;
                  font-size:1rem; margin:0;">
            Generate pitch deck team slide content from a LinkedIn profile
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Instructions expander ─────────────────────────────────────────────────────
with st.expander("How to get the LinkedIn profile text"):
    st.markdown(
        """
        1. Open the LinkedIn profile in your browser
        2. Scroll down and click **"Show all experience"** and **"Show all education"**
        3. Select all text on the page — **Cmd+A** (Mac) or **Ctrl+A** (Windows)
        4. Copy — **Cmd+C** / **Ctrl+C**
        5. Paste into the text area below
        """
    )

# ── Inputs ────────────────────────────────────────────────────────────────────
url = st.text_input(
    "LinkedIn Profile URL",
    placeholder="https://linkedin.com/in/... (optional)",
)

profile_text = st.text_area(
    "Paste LinkedIn profile text",
    height=260,
    placeholder="Paste the copied text from the LinkedIn profile page here…",
)

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    generate = st.button(
        "Generate Profile",
        type="primary",
        use_container_width=True,
        disabled=not profile_text.strip(),
    )

# ── Generate ──────────────────────────────────────────────────────────────────
if generate and profile_text.strip():
    with st.spinner("Analysing profile with Claude…"):
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except (KeyError, FileNotFoundError):
            st.error(
                "API key not configured. "
                "Add `ANTHROPIC_API_KEY` to your Streamlit secrets — "
                "`.streamlit/secrets.toml` locally, or Settings → Secrets on Streamlit Cloud."
            )
            st.stop()

        try:
            result = process_profile(profile_text, api_key, url or None)
        except Exception as exc:
            st.error(f"Something went wrong: {exc}")
            st.stop()

    st.divider()
    st.markdown(
        "<h2 style='font-family:\"Plus Jakarta Sans\",Arial,sans-serif;"
        "color:#144b3e; margin-bottom:0.25rem;'>Your Pitch Deck Profile</h2>"
        "<p style='font-family:\"Lora\",Georgia,serif; color:#30473f; "
        "font-size:0.875rem; margin-bottom:1rem;'>"
        "Click any field to select it, then copy and paste into your Keynote slide.</p>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="dr-label">Designation</p>', unsafe_allow_html=True)
        st.text_input("_des", value=result["designation"],
                      label_visibility="collapsed", key="r_designation")
    with c2:
        yrs_label = result["years_experience"]
        if result.get("first_job_date"):
            yrs_label += f"  ·  since {result['first_job_date']}"
        st.markdown('<p class="dr-label">Years of Experience</p>', unsafe_allow_html=True)
        st.text_input("_yrs", value=yrs_label,
                      label_visibility="collapsed", key="r_years")

    st.markdown('<p class="dr-label">One-Line Summary</p>', unsafe_allow_html=True)
    st.text_input("_sum", value=result["one_line_summary"],
                  label_visibility="collapsed", key="r_summary")

    st.markdown(
        '<p class="dr-label">Experience Highlights '
        '<span style="font-weight:400;text-transform:none;letter-spacing:0;">'
        '— for company logo slide</span></p>',
        unsafe_allow_html=True,
    )
    highlights = result.get("experience_highlights", [])
    if highlights:
        for i, exp in enumerate(highlights):
            st.text_input(
                f"_exp{i}",
                value=f"{exp['company']} | {exp['role']}",
                label_visibility="collapsed",
                key=f"r_exp_{i}",
            )
    else:
        st.caption("No prominent prior roles to highlight.")

    st.markdown('<p class="dr-label">Education</p>', unsafe_allow_html=True)
    for i, edu in enumerate(result.get("education", [])):
        st.text_input(
            f"_edu{i}",
            value=f"{edu['degree']} | {edu['institution']}",
            label_visibility="collapsed",
            key=f"r_edu_{i}",
        )

    st.markdown(
        """
        <div class="dr-note">
            <div class="note-label">Profile Photo</div>
            <div class="note-body">
                Right-click the photo on LinkedIn → <em>Save Image As</em>,
                then drag it into your Keynote slide.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
