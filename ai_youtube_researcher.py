"""
Automated AI Web Researcher & YouTube Script Generator

Pipeline:
    Topic
      ↓
    Research Breakdown
      ↓
    5-Minute YouTube Script
      ↓
    Visual / B-Roll Plan
      ↓
    Terminal Output

Requirements:
    pip install openai

Environment variable:
    OPENAI_API_KEY

Example:
    python ai_youtube_researcher.py "Claude Code CLI Features & Vibecoding"
"""

import os
import sys
from openai import OpenAI


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

# You can change this to another available OpenAI model.
MODEL = "gpt-5.6-luna"

# Approximately 5 minutes of spoken YouTube content.
TARGET_SCRIPT_LENGTH = "650-800 words"


# ------------------------------------------------------------
# OPENAI CLIENT
# ------------------------------------------------------------

def create_client():
    """
    Creates the OpenAI client.

    The API key is read from the OPENAI_API_KEY environment
    variable instead of being written directly into the source code.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set.\n"
            "Set it as an environment variable before running the script."
        )

    return OpenAI(api_key=api_key)


# ------------------------------------------------------------
# LLM HELPER
# ------------------------------------------------------------

def ask_llm(client, prompt):
    """
    Sends a prompt to the model and returns its text response.

    Keeping this in one function makes it easy to:
        - change models
        - add logging
        - add retries later
        - add token/cost tracking later
    """

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    return response.output_text


# ------------------------------------------------------------
# STEP 1 — RESEARCH BREAKDOWN
# ------------------------------------------------------------

def generate_research(client, topic):
    """
    Turns the user's topic into a structured 3-step research plan.

    The model is instructed to separate:
        1. What the topic is
        2. Why it matters
        3. Important examples / demonstrations
    """

    prompt = f"""
You are a senior technology researcher preparing research
for a YouTube video.

TOPIC:
{topic}

Create a concise 3-step research breakdown.

STEP 1 — CORE CONCEPT
Explain what the topic is and identify the most important
concepts a viewer needs to understand.

STEP 2 — FEATURES / EVIDENCE
Identify the most important features, capabilities,
examples, demonstrations, or documented facts that should
appear in a YouTube video.

STEP 3 — PRACTICAL TAKEAWAYS
Explain what someone watching the video should understand,
try, compare, or remember.

Requirements:
- Be factual.
- Clearly distinguish facts from opinions.
- Avoid inventing features, commands, statistics, or quotes.
- Prioritize information useful for a 5-minute technology video.
- Use clear headings.
"""

    return ask_llm(client, prompt)


# ------------------------------------------------------------
# STEP 2 — YOUTUBE SCRIPT
# ------------------------------------------------------------

def generate_script(client, topic, research):
    """
    Uses the research produced by Step 1 as context for a
    second LLM call.

    This is the prompt-chain portion of the application:

        Topic → Research → Script
    """

    prompt = f"""
You are a professional YouTube technology scriptwriter.

VIDEO TOPIC:
{topic}

RESEARCH:
{research}

Using the research above, write a production-ready
approximately 5-minute YouTube script.

TARGET LENGTH:
{TARGET_SCRIPT_LENGTH}

STRUCTURE:

[HOOK]
Grab the viewer's attention immediately.

[INTRO]
Quickly explain what the video is about.

[SECTION 1]
Explain the first major idea.

[SECTION 2]
Explain the important features/examples.

[DEMO]
Describe what should be demonstrated on screen.

[SECTION 3]
Explain the practical implications and takeaways.

[ENDING]
Summarize the most useful points and provide a natural
closing.

SCRIPT REQUIREMENTS:
- Write natural spoken English.
- Keep sentences relatively short.
- Avoid sounding like a textbook.
- Do not invent facts.
- Do not include citations inside the spoken narration.
- Use [SCREEN: ...] markers where a visual demonstration
  would naturally occur.
- Make the script interesting without using exaggerated
  clickbait.
- The result should be directly usable by a YouTube creator.
"""

    return ask_llm(client, prompt)


# ------------------------------------------------------------
# STEP 3 — B-ROLL / VISUAL PLAN
# ------------------------------------------------------------

def generate_broll_plan(client, topic, script):
    """
    Converts the completed script into a production plan.

    Each row connects:
        timestamp → narration → visual

    This makes the output useful for actually recording/editing
    the YouTube video.
    """

    prompt = f"""
You are a YouTube video production director.

VIDEO TOPIC:
{topic}

SCRIPT:
{script}

Create a detailed visual B-roll plan for this script.

For every major audio section provide:

1. TIMESTAMP
2. AUDIO / NARRATION SUMMARY
3. PRIMARY VISUAL
4. B-ROLL TYPE
5. SCREEN RECORDING / UI DEMO
6. EDITING NOTE

Prioritize visuals such as:
- Browser recordings
- Terminal recordings
- Code editor footage
- Product UI demonstrations
- Cursor movements
- Before/after comparisons
- Text overlays
- Simple diagrams
- Zoom-ins on important UI elements

For technical demonstrations, specify exactly what should
be visible on screen without inventing commands or features.

Keep the plan synchronized with the script.
"""

    return ask_llm(client, prompt)


# ------------------------------------------------------------
# TERMINAL FORMATTING
# ------------------------------------------------------------

def print_section(title, content):
    """
    Prints a visually separated section in the terminal.
    """

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(content)


# ------------------------------------------------------------
# MAIN APPLICATION
# ------------------------------------------------------------

def main():
    """
    Main execution pipeline.

    The user provides a topic, then the application executes:

        1. Research
        2. Script generation
        3. B-roll planning
    """

    # --------------------------------------------------------
    # Get topic from CLI arguments
    # --------------------------------------------------------

    if len(sys.argv) < 2:
        print(
            'Usage:\n'
            '  python ai_youtube_researcher.py '
            '"Your Video Topic"'
        )
        sys.exit(1)

    # Join all arguments so topics containing spaces work.
    topic = " ".join(sys.argv[1:])

    print("\nAI YouTube Researcher")
    print("-" * 80)
    print(f"Topic: {topic}")

    try:
        # Create the OpenAI client.
        client = create_client()

        # ----------------------------------------------------
        # STEP 1
        # ----------------------------------------------------

        print("\n[1/3] Researching topic...")

        research = generate_research(
            client,
            topic
        )

        print("Research complete.")

        # ----------------------------------------------------
        # STEP 2
        # ----------------------------------------------------

        print("\n[2/3] Writing 5-minute YouTube script...")

        script = generate_script(
            client,
            topic,
            research
        )

        print("Script complete.")

        # ----------------------------------------------------
        # STEP 3
        # ----------------------------------------------------

        print("\n[3/3] Creating visual B-roll plan...")

        broll = generate_broll_plan(
            client,
            topic,
            script
        )

        print("B-roll plan complete.")

        # ----------------------------------------------------
        # FINAL OUTPUT
        # ----------------------------------------------------

        print_section(
            "RESEARCH BREAKDOWN",
            research
        )

        print_section(
            "5-MINUTE YOUTUBE SCRIPT",
            script
        )

        print_section(
            "VISUAL B-ROLL PLAN",
            broll
        )

        print("\n" + "=" * 80)
        print("PIPELINE COMPLETE")
        print("=" * 80)

    except Exception as error:
        # Catch API/configuration errors and give the user a
        # readable message instead of a huge traceback.
        print("\nERROR:")
        print(error)
        sys.exit(1)


# ------------------------------------------------------------
# PROGRAM ENTRY POINT
# ------------------------------------------------------------

if __name__ == "__main__":
    main()
