"""
IT Admin Panel — FastAPI Backend
Serves the dashboard UI and exposes endpoints for the autonomous IT Agent.
"""
import asyncio
import os
import secrets
import string
import sys
import uuid
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# ── Path setup ────────────────────────────────────────────────────────────────
# Ensure the project root is on sys.path so 'agent' can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agent.agent import run_agent  # noqa: E402 (must come after sys.path fix)

# ── App & Templates ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="CorpAdmin — IT Support Panel")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ── In-Memory Data Store ──────────────────────────────────────────────────────
# Simulates a real user directory for demonstration purposes.
users = [
    {"id": "user-1", "name": "John Doe",   "email": "john@company.com", "status": "active",   "password": "InitialPass123!"},
    {"id": "user-2", "name": "Jane Smith", "email": "jane@company.com", "status": "active",   "password": "InitialPass456!"},
]

# Tracks the single active agent task to allow remote cancellation.
active_tasks: dict = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def generate_password(length: int = 12) -> str:
    """Generate a cryptographically strong random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def find_user(user_id: str) -> dict | None:
    """Return user dict by ID, or None if not found."""
    return next((u for u in users if u["id"] == user_id), None)


# ── Routes — Dashboard ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    message: Optional[str] = None,
    detail: Optional[str] = None,
):
    return templates.TemplateResponse(request, "index.html", {
        "users": users,
        "message": message,
        "detail": detail,
        "title": "Dashboard - AdminOS",
    })


# ── Routes — User Management ──────────────────────────────────────────────────

@app.get("/create", response_class=HTMLResponse)
async def create_user_page(request: Request):
    return templates.TemplateResponse(request, "create_user.html", {
        "title": "Add User - AdminOS",
    })


@app.post("/create")
async def create_user(
    name: str = Form(...),
    email: str = Form(...),
    password: Optional[str] = Form(None),
):
    final_password = password.strip() if password and password.strip() else generate_password()
    new_user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "status": "active",
        "password": final_password,
    }
    users.append(new_user)
    return RedirectResponse(
        url=f"/?message=User {name} created successfully!&detail=Account Password: {final_password}",
        status_code=303,
    )


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def user_details(request: Request, user_id: str):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse(request, "user_details.html", {
        "user": user,
        "title": f"Manage {user['name']} - AdminOS",
    })


@app.post("/user/{user_id}/reset-password")
async def reset_password(user_id: str):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_password = generate_password()
    user["password"] = new_password
    return RedirectResponse(
        url=f"/?message=Password reset for {user['email']}!&detail=New Password: {new_password}",
        status_code=303,
    )


@app.post("/user/{user_id}/deactivate")
async def deactivate_user(user_id: str):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["status"] = "inactive"
    return RedirectResponse(
        url=f"/?message=User {user['name']} deactivated!",
        status_code=303,
    )


@app.post("/user/{user_id}/activate")
async def activate_user(user_id: str):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["status"] = "active"
    return RedirectResponse(
        url=f"/?message=User {user['name']} reactivated!",
        status_code=303,
    )


# ── Routes — IT Agent Chat ────────────────────────────────────────────────────

@app.get("/trigger", response_class=HTMLResponse)
async def trigger_page(request: Request):
    return templates.TemplateResponse(request, "trigger.html", {
        "title": "Chat Simulator - IT Agent",
    })


@app.post("/trigger")
async def trigger_agent(task: str = Form(...)):
    """
    Trigger the browser agent with a natural-language task.
    If no URL is specified, the task is automatically scoped to the local admin panel.
    """
    # Implicit context: default to local admin panel if no URL is mentioned.
    if "http" not in task.lower() and "notion" not in task.lower():
        context_task = f"Go to http://127.0.0.1:8000. {task}"
    else:
        context_task = task

    # Cancel any already-running task before starting a new one.
    if "latest" in active_tasks:
        active_tasks["latest"].cancel()

    agent_task = asyncio.create_task(run_agent(context_task))
    active_tasks["latest"] = agent_task

    try:
        result = await agent_task
        return {"result": result}
    except asyncio.CancelledError:
        return {"result": "⛔ Agent execution was terminated by user."}
    finally:
        if active_tasks.get("latest") is agent_task:
            del active_tasks["latest"]


@app.post("/terminate")
async def terminate_agent():
    """Cancel the currently running agent task."""
    if "latest" in active_tasks:
        active_tasks["latest"].cancel()
        return {"status": "success", "message": "Agent terminated."}
    return {"status": "error", "message": "No active agent task found."}


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
