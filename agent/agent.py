"""
Autonomous IT Support Agent
Uses browser-use + Google Gemini to perform IT tasks via real browser automation.
Includes robust retry logic for API rate limits and high-demand errors.
"""
import asyncio
import os
import sys

# Force UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

# Load environment variables before any other imports that depend on them
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please check your configuration.")

from browser_use import Agent, Browser                  # noqa: E402
from browser_use.llm.google.chat import ChatGoogle      # noqa: E402

# ── LLM Initialization ────────────────────────────────────────────────────────
# Initialized once globally so the server doesn't recreate it per-request.
llm = ChatGoogle(model=model_name, api_key=api_key)

# ── Core Agent Runner ─────────────────────────────────────────────────────────

async def run_agent(task_description: str) -> str:
    """
    Execute a browser-based automation task using the configured LLM.

    Retries up to `max_retries` times on transient high-demand (503) errors.
    Always ensures the browser window is closed after each attempt.

    Args:
        task_description: Plain-English instruction for the agent.

    Returns:
        A string summary of the agent's result, or an error message.
    """
    print(f"\n{'='*60}")
    print(f"  MODEL : {model_name}")
    print(f"  TASK  : {task_description}")
    print(f"{'='*60}\n")

    max_retries = 5

    for attempt in range(max_retries):
        browser = Browser(headless=False, disable_security=True)

        try:
            agent = Agent(
                task=task_description,
                llm=llm,
                browser=browser,
                max_failures=3,
            )
            result = await agent.run()
            result_str = str(result)
            print(f"\n✅ TASK COMPLETE:\n{result_str}")
            return result_str

        except asyncio.CancelledError:
            # Propagate cancellation so the caller can handle it cleanly.
            raise

        except Exception as e:
            error_str = str(e).lower()
            is_transient = any(k in error_str for k in ("503", "high demand", "unavailable"))

            if is_transient and attempt < max_retries - 1:
                wait = 15
                print(f"\n⚠️  {model_name} is at peak demand. Retrying in {wait}s "
                      f"(attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(wait)
                continue

            print(f"\n❌ AGENT ERROR: {e}")
            return f"Error: {e}"

        finally:
            await browser.kill()

    return "Error: Maximum retries reached. The model may still be unavailable."


# ── Demo Task Catalogue ───────────────────────────────────────────────────────
# Used when running agent.py directly from the CLI.

DEMO_TASKS = [
    (
        "TEST 1 — CREATE USER",
        "Go to http://localhost:8000. Navigate to 'Add User'. "
        "Fill First Name 'Alice', Last Name 'Johnson', Email 'alice@company.com', "
        "and Password 'Welcome123!'. Click 'Create Account'. Verify the success message.",
    ),
    (
        "TEST 2 — RESET PASSWORD",
        "Go to http://localhost:8000. Find 'John Doe', click 'Manage →'. "
        "Click 'Reset →' next to 'Reset Password'. "
        "Read the new password from the success message and report it.",
    ),
    (
        "TEST 3 — NEGATIVE / NOT FOUND",
        "Go to http://localhost:8000. Search for user 'zorp@company.com'. "
        "If not found, report that the user does not exist. Do not invent details.",
    ),
    (
        "TEST 4 — CONDITIONAL LOGIC (Reactivate → Reset)",
        "Go to http://localhost:8000. Look for 'Jane Smith'. "
        "If her status is 'inactive', click 'Manage →' then 'Reactivate →'. "
        "Once she is active, click 'Reset →' for 'Reset Password'. "
        "Report the final new password shown.",
    ),
    (
        "TEST 5 — SAAS DEMO (Notion)",
        "Go to https://www.notion.so/login. "
        "Confirm the 'Email' input field is visible to verify the page loaded correctly. "
        "Do not enter any credentials.",
    ),
]


# ── CLI Entry Point ───────────────────────────────────────────────────────────

async def main():
    print("\n🤖  CorpAdmin — IT Support Agent")
    print("=" * 60)
    print("  1. Run all DEMO tasks")
    print("  2. Run a CUSTOM task")
    print("  3. Exit")

    choice = input("\nChoose [1/2/3]: ").strip()

    if choice == "1":
        for i, (label, task) in enumerate(DEMO_TASKS):
            print(f"\n▶️  Starting {label}...")
            await run_agent(task)
            if i < len(DEMO_TASKS) - 1:
                input("\n⏸  Press Enter to continue to the next demo task...")

    elif choice == "2":
        while True:
            raw_task = input("\nEnter IT Support Request (or 'exit' to quit): ").strip()
            if raw_task.lower() == "exit":
                break
            if raw_task:
                # Always anchor to the local panel unless the user explicitly provides a URL.
                locked_task = (
                    f"Go to http://localhost:8000 and then: {raw_task}. "
                    "If a new password or specific status is shown, include it in your final answer."
                )
                await run_agent(locked_task)

    print("\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
