import json
import re
import anthropic
from datetime import date


def process_profile(profile_text: str, api_key: str, url: str = None) -> dict:
    """
    Analyse a pasted LinkedIn profile and return structured pitch deck data.

    Returns a dict with keys:
        designation, years_experience, first_job_date, one_line_summary,
        experience_highlights (list of {company, role}),
        education (list of {degree, institution})
    """
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

    # Extract the text block (skip thinking blocks)
    raw = ""
    for block in message.content:
        if block.type == "text":
            raw = block.text.strip()
            break

    if not raw:
        raise ValueError("No response received from Claude.")

    # Strip markdown code fences if present (e.g. ```json ... ```)
    raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()

    return json.loads(raw)
