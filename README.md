# IT Support Agent — Autonomous Browser Automation

An AI-powered IT Support Agent that handles enterprise workflows (user provisioning, password resets) using natural language and browser-based automation.

## Overview
This project demonstrates an agentic workflow where an AI "worker" interacts with an IT Admin Panel exactly like a human would. Using **Vision-to-Action** logic, it interprets UI elements, follows conditional instructions, and reports results back to the team.

### Features
- **Mock IT Admin Panel**: Developed with **FastAPI** to simulate a realistic enterprise dashboard.
- **Autonomous Agent**: Built with **Browser-Use** and **Gemini 2.5 Flash Lite**.
- **Slack-style Chat Simulator**: A web interface for triggering agent tasks via natural language.
- **Conditional Logic**: Handles state-dependent tasks (e.g., reactivate account -> reset password).
- **SaaS Integration**: Compatible with real-world platforms like Notion.

## 🛠️ Technical Stack
- **Backend**: FastAPI, Jinja2 (Templates), Uvicorn.
- **AI/Automation**: Browser-Use, Playwright, Google Gemini API.
- **Styling**: Vanilla CSS with a focus on rich, premium aesthetics.

## Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-link>
   cd decawork
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash-lite
   ```

4. **Run the Dashboard**:
   ```bash
   python admin_panel/main.py
   ```
   *The dashboard will be available at [http://localhost:8000](http://localhost:8000)*

5. **Run the Agent (CLI Mode)**:
   ```bash
   python agent/agent.py
   ```

## Demo Scenarios
- **Scenario 1**: Create a new user account with a specific password.
- **Scenario 2**: Reset a forgotten password and report the new one.
- **Scenario 3**: Multi-step activation of an inactive user before performing a reset.
- **Scenario 4**: SaaS login readiness check for Notion.

## Key Design Decisions
- **Multimodal Vision**: Used Gemini's vision capabilities to handle UI feedback without fragile CSS selectors.
- **Self-Correction**: Implemented robust retry logic to handle model 503 errors and peak demand.
- **Human-in-the-Loop**: The Chat Simulator allows seamless interaction between human managers and AI workers.
