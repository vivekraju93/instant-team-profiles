import anthropic
from datetime import date


def process_profile(profile_text: str, api_key: str, url: str = None) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    today_str = date.today().strftime("%B %d, %Y")

    url_context = f"\nLinkedIn URL: {url}" if url else ""

    system_prompt = (
        "You are an expert at analyzing LinkedIn profiles and creating concise, "
        "impressive pitch deck team slides. You extract the most relevant information "
        "for investors and present it in a clean, copyable plain-text format."
    )

    user_prompt = f"""Analyze this LinkedIn profile and generate pitch deck team slide content.

Today's date: {today_str}{url_context}

LinkedIn Profile Text:
---
{profile_text}
---

Return ONLY the formatted output below — no preamble, no commentary, nothing else.

==================================================
PITCH DECK TEAM PROFILE
==================================================

DESIGNATION
[Current job title only — never the company name.
 Correct: "Co-Founder & CEO"  Wrong: "Co-Founder & CEO at Acme Corp"]

YEARS OF EXPERIENCE
[X years]
(First job: [Month Year] → Today)

ONE-LINE SUMMARY
[5–8 words. Be specific and punchy — mention prestigious employers, exits/IPOs,
 scale of impact, or notable credentials. Examples:
 "Ex-McKinsey partner, scaled 3 unicorns"
 "MIT PhD, 2 exits, built Google Maps"
 "15 years in fintech, former Goldman VP"
 Avoid vague phrases like "Experienced leader with 10+ years".]

EXPERIENCE HIGHLIGHTS
(Use these for the company logo slide — company name + role only)
[Company] | [Job Title]
[Company] | [Job Title]
...
[Write "None — no prominent prior roles to highlight" if nothing qualifies]

EDUCATION
[Degree, Field] | [Institution]
[Degree, Field] | [Institution]
...

PROFILE PHOTO
Download manually: go to their LinkedIn profile → right-click photo → Save Image As

==================================================
HOW TO USE IN KEYNOTE
- DESIGNATION → title text box
- YEARS OF EXPERIENCE → sub-title or stat text box
- ONE-LINE SUMMARY → tagline text box
- EXPERIENCE HIGHLIGHTS → search "[Company] logo PNG transparent" for each logo
- EDUCATION → education text box
- PHOTO → drag the saved image file into the slide
==================================================

RULES (follow exactly):

DESIGNATION
- Job title only. Never include the company name.

YEARS OF EXPERIENCE
- Count from the START DATE of their very first job to today ({today_str}).
- Round to the nearest whole year (8.5 → 9 years).
- If the exact start date is missing, estimate from context (graduation year, other dates).

ONE-LINE SUMMARY
- This is the most important field. Make it memorable and investor-facing.
- Mention well-known brands, number of exits/IPOs if applicable, prestigious degrees.
- Must be 5–8 words.

EXPERIENCE HIGHLIGHTS — include ONLY companies that satisfy BOTH conditions:
  1. WELL-KNOWN company (examples of what qualifies):
     - Major tech: Google, Meta, Apple, Microsoft, Amazon, Netflix, Uber, Airbnb,
       Stripe, Palantir, Spotify, Twitter/X, Snap, LinkedIn, Salesforce, Oracle, SAP
     - Top consulting: McKinsey, BCG, Bain, Deloitte, Accenture, Oliver Wyman, Roland Berger
     - Top banks/finance: Goldman Sachs, JPMorgan, Morgan Stanley, Citi, BlackRock,
       Bridgewater, Sequoia, Andreessen Horowitz, SoftBank
     - Well-known unicorns with major funding or exits
     - Military officer roles, prominent government positions
     - Major media: NYT, BBC, Bloomberg, Financial Times
  2. SENIOR or MANAGERIAL role (examples of what qualifies):
     - C-suite: CEO, CTO, COO, CFO, CMO, CRO, CPO
     - VP, SVP, EVP, Director, Senior Director, Managing Director
     - Senior [any role], Lead [any role], Principal [any role]
     - Head of [anything], General Manager, Founder, Co-Founder
     - Partner (consulting/law/VC)
     - EXCLUDE: Intern, Analyst (entry-level), Associate (entry-level IC),
       Junior [anything], Trainee, individual contributor without "Senior/Lead/Principal"

  List at most 4 companies. Fewer is fine if fewer qualify.

EDUCATION
- Include all degrees (bachelor's, master's, MBA, PhD, etc.).
- Format: "MBA" or "B.Tech, Computer Science" or "PhD, Physics" or "B.A., Economics".
- Include institution name even if not prestigious.
"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Extract the text block (skip thinking blocks)
    for block in message.content:
        if block.type == "text":
            return block.text.strip()

    return "(No output generated — please try again)"
