"""
Quick key verification: Create one user via the browser agent.
Kept deliberately short to spend as few tokens as possible.
"""
import os
import sys
import asyncio

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

api_key  = os.getenv("GOOGLE_API_KEY")
model    = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

if not api_key:
    raise ValueError("GOOGLE_API_KEY missing from .env")

from browser_use import Agent, Browser
from browser_use.llm.google.chat import ChatGoogle

llm = ChatGoogle(model=model, api_key=api_key)

TASK = (
    "Go to http://localhost:8000. "
    "Click 'Add User' in the left sidebar. "
    "Fill First Name = 'Alice', Last Name = 'Johnson', "
    "Email = 'alice@company.com'. "
    "Click 'Create Account'. "
    "Confirm the dashboard shows a success message with Alice's name. "
    "Report SUCCESS or FAILURE."
)

async def main():
    print(f"\n[KEY CHECK] Model: {model}")
    print("[TASK] Create user Alice Johnson via browser agent\n")
    browser = Browser(headless=False, disable_security=True)
    agent = Agent(task=TASK, llm=llm, browser=browser, max_failures=2)
    try:
        result = await agent.run(max_steps=15)   # hard cap: 15 steps max
        print(f"\n✅ RESULT:\n{result}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    finally:
        await browser.kill()

if __name__ == "__main__":
    asyncio.run(main())
