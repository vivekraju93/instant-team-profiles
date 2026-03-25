#!/usr/bin/env python3
"""
instant-team-profiles: Generate pitch deck team slide content from a LinkedIn profile.

HOW TO GET THE PROFILE TEXT:
  1. Open the LinkedIn profile in your browser
  2. Scroll to load the full page (expand "Show all experience", "Show all education")
  3. Select all text on the page  (Ctrl+A on Windows/Linux, Cmd+A on Mac)
  4. Copy  (Ctrl+C / Cmd+C)
  5. Either paste it when prompted below, OR save it to a .txt file and use --file
"""

import sys
import os
import click
from dotenv import load_dotenv

from profile_processor import process_profile


@click.command()
@click.option(
    "--file", "-f", "input_file",
    type=click.Path(exists=True),
    help="Path to a .txt file containing the pasted LinkedIn profile text.",
)
@click.option(
    "--url", "-u",
    help="LinkedIn profile URL (shown in output for reference — not fetched automatically).",
)
def main(input_file: str, url: str):
    """Generate pitch deck team slide content from a LinkedIn profile.

    Paste the raw text copied from a LinkedIn profile page, or point to a saved
    text file with --file. The tool uses Claude AI to extract and format the key
    information needed for a pitch deck team slide.
    """
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        click.echo(
            "Error: ANTHROPIC_API_KEY is not set.\n"
            "Copy .env.example to .env and add your Anthropic API key.",
            err=True,
        )
        sys.exit(1)

    # --- Get profile text ---
    if input_file:
        click.echo(f"Reading profile text from: {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            profile_text = f.read()
    else:
        if url:
            click.echo(f"Profile URL: {url}")
        click.echo(
            "\nPaste the LinkedIn profile text below, then press Enter and:\n"
            "  Mac/Linux: Ctrl+D\n"
            "  Windows:   Ctrl+Z then Enter\n"
        )
        try:
            profile_text = sys.stdin.read()
        except KeyboardInterrupt:
            click.echo("\nCancelled.")
            sys.exit(0)

    if not profile_text.strip():
        click.echo("Error: No profile text provided.", err=True)
        sys.exit(1)

    click.echo("\nAnalyzing profile with Claude...\n")

    try:
        result = process_profile(profile_text, api_key, url)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
