# 🏔️ LandFlow AI

> **AI-powered CRM for Indian real estate businesses** — replace Excel sheets, WhatsApp chats, and manual follow-ups with an intelligent multi-agent workflow.

![LandFlow AI Dashboard](docs/dashboard.png)

---

## 🏗️ System Architecture

![LandFlow AI Architecture](docs/architecture.png)

### How It All Works Together

LandFlow AI is built as a **layered system** where each layer has a single responsibility. Here is a plain-English walkthrough of how data and requests flow through the platform:

---

### Layer 1 — User Interface (Streamlit Web App)

The user interacts with the platform entirely through a **Streamlit web application** running locally in their browser. The interface is divided into six sections:

| Section | Purpose |
|---------|---------|
| **Login** | Role-based authentication (Admin / Broker) |
| **Dashboard** | AI-generated business overview + live KPI metrics |
| **Client Hub** | Manage buyers and sellers with AI insights and communication tools |
| **Property Catalog** | Browse, add, and manage land listings |
| **Deal Pipeline** | Track deals across 7 Kanban stages from New Lead to Closed |
| **AI Command Center** | Natural language chat interface for querying the entire CRM |

When a user performs any action (e.g. submitting a natural language query, clicking "Generate AI Insights", or opening a buyer profile), Streamlit triggers a Python function that calls into the **AI Agent layer**.

---

### Layer 2 — AI Agent Orchestration (Google ADK)

This is the intelligence layer of LandFlow AI. It is built using the **Google Antigravity SDK (ADK)** and contains five agents, each with a distinct specialisation:

#### 🧠 Orchestrator Agent
The **entry point for all AI Command Center queries**. When the user types a natural language request such as *"Find buyers for Gurgaon plots under ₹2 Crore"*, the Orchestrator Agent:
1. Reads and interprets the user's intent.
2. Decides which specialist agents to call (can call multiple in sequence).
3. Collects all responses and synthesises a single comprehensive markdown report.
4. Reports which agents and MCP tools were used (shown in the audit trail card in the UI).

#### 🎯 Lead Qualification Agent
Activated when a user requests AI Insights on a buyer profile. It analyses the buyer's budget, location preferences, size requirements, notes, and activity history to produce a structured report:
- **Lead Score** (0–100)
- **Buying Intent** (Very High / High / Medium / Low)
- **Likelihood of Closing** (percentage)
- **Expected Closing Timeline**
- **Potential Risks**
- **Recommended Next Action**

#### 🏠 Property Matching Agent
Activated when a user asks to match buyers with properties. It searches the property catalog for the top 5 most compatible listings for a given buyer based on location, budget, and land size, and explains why each is a good match.

#### 📅 Follow-up Agent
Activated for two purposes:
1. **Daily follow-up check** — scans for overdue tasks and inactive clients.
2. **Communication drafting** — generates personalised WhatsApp messages, emails, call scripts, meeting agendas, and negotiation talking points for any buyer or seller.

#### 📊 Analytics Agent
Activated for the **AI Business Dashboard Brief** and for answering operational questions (e.g. *"Which properties are overpriced?"*, *"Summarise today's business"*). It pulls live statistics from the database and composes a structured executive summary.

---

### Layer 3 — MCP Tool Server (FastMCP)

The agents do not query the database directly. Instead, they communicate with the **FastMCP Tool Server** via a standardised protocol called **Model Context Protocol (MCP)**. This creates a clean separation between the AI reasoning layer and the data access layer.

The MCP server exposes a set of **named tools** that agents can call:

| MCP Tool | What It Does |
|----------|-------------|
| `search_buyers` | Search and filter buyer records |
| `search_sellers` | Search and filter seller records |
| `search_properties` | Search and filter land properties |
| `get_dashboard_stats` | Get aggregate statistics (counts, averages, stages) |
| `get_followups` | Retrieve pending and overdue follow-up tasks |
| `log_activity` | Write a new activity log entry for a client |

Each agent call results in one or more MCP tool calls. These tool calls are **logged in real-time** and displayed in the AI Command Center's audit trail so the user can see exactly what the AI queried.

The MCP server runs as a **subprocess** using `stdio` transport — meaning it starts automatically when any agent runs and terminates when the agent finishes. No separate server process is needed.

---

### Layer 4 — Database (SQLite)

All CRM data is stored in a local **SQLite database** (`landflow.db`). The schema includes six tables:

| Table | Contents |
|-------|---------|
| `users` | Login credentials and roles |
| `buyers` | Buyer profiles (name, phone, budget, location, status) |
| `sellers` | Seller profiles (name, phone, asking price, land area) |
| `properties` | Land listings (location, area, price, status) |
| `deals` | Deal records linking buyers, sellers, and properties with stage tracking |
| `activity_logs` | Timestamped history of calls, site visits, meetings, and notes |
| `followups` | Scheduled tasks with due dates and completion status |
| `mcp_tool_logs` | Audit trail of every MCP tool call made by AI agents |

The database is automatically **initialised and seeded** with realistic sample data (10 buyers, 9 sellers, 20 properties, 13 deals) on first run via `database.py`.

---

### Layer 5 — AI Model Backend (Gemini / DeepSeek)

The agents use one of two configurable AI model backends:

#### Google Gemini (via ADK — Recommended)
- Model: `gemini-3.5-flash` (default) or any Gemini model via `GEMINI_MODEL` env variable
- Free developer tier: 20 requests/day per model
- The ADK handles tool calling natively — agents can invoke MCP tools autonomously during a conversation turn
- Set `GEMINI_API_KEY` in your `.env` file

#### DeepSeek (via OpenAI-compatible API)
- Model: `deepseek-chat`
- Requires a paid account balance
- Uses an alternative flow: the entire database is serialised into the system prompt as context (RAG-style injection), eliminating the need for live tool calls
- Set `DEEPSEEK_API_KEY` in your `.env` file

The application **automatically detects** which key is present and routes accordingly.

---

## ✨ Features

### 📊 AI Business Dashboard
- **Today's AI Business Brief** — Daily executive summary generated by the Analytics Agent
- Revenue Potential, Deals Closing This Week, Conversion Rate, Top Broker, Hot Locations
- Color-coded KPI cards with live data

### 👥 Client Hub (Buyers & Sellers)
- Full CRUD for Buyers and Sellers
- **🤖 AI Insights** — Lead Score, Buying Intent, Likelihood of Closing, Risks, Timeline
- **📬 AI Communication Assistant** — Personalised WhatsApp, Email, Call Script, Meeting Agenda, Negotiation Talking Points

### 🏔️ Property Catalog
- Add, edit, delete land properties with status tracking
- Search and filter listings

### ⛓️ Deal Pipeline
- 7-stage Kanban: New Lead → Contacted → Site Visit → Negotiation → Documentation → Registration → Closed
- Timeline tracking with full activity logs

### 🤖 AI Command Center
- ChatGPT-style natural language interface
- Orchestrator Agent automatically routes to specialist sub-agents
- Live MCP tool call audit trail

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Python + Streamlit |
| AI Agents | Google Antigravity SDK (ADK) |
| AI Models | Google Gemini / DeepSeek |
| Tool Server | FastMCP (stdio transport) |
| Database | SQLite |
| Auth | Session-based role authentication |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/sisprasin/landflow-ai.git
cd landflow-ai
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
Create a `.env` file in the project root:
```env
# Google Gemini (free tier — recommended)
GEMINI_API_KEY="AIzaSy..."

# OR DeepSeek (requires paid balance)
# DEEPSEEK_API_KEY="sk-..."
```

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 5. Run the app
```bash
streamlit run app.py --server.port 8502
```

Open [http://localhost:8502](http://localhost:8502) in your browser.

---

## 🔐 Default Login Credentials

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |
| `broker1` | `broker123` | Broker |

---

## 📁 Project Structure

```
landflow-ai/
├── app.py              # Streamlit frontend (all pages & UI)
├── agents.py           # AI agents (ADK + DeepSeek support)
├── database.py         # SQLite database layer + seeding
├── mcp_server.py       # FastMCP tool server (MCP protocol)
├── requirements.txt    # Python dependencies
├── verify_setup.py     # Setup verification script
├── docs/
│   ├── architecture.png   # System architecture diagram
│   └── dashboard.png      # Dashboard screenshot
└── .gitignore
```

---

## 📄 License

MIT License — feel free to use, modify, and build on this project.
