# Upchaar Care Agent 🏥

An AI-powered healthcare appointment assistant built with **Agentic AI, Python, FastAPI, LangChain, Groq, and the Model Context Protocol (MCP)**. The agent uses tools to help users find doctors, check appointment availability, book or cancel appointments, and retrieve appointment details.

## 🚀 Project Overview

Upchaar Care Agent demonstrates how an LLM-powered agent can interact with external tools to complete healthcare appointment workflows rather than simply generating text responses.

The application exposes a REST API through FastAPI. Users can send natural-language messages, and the agent can select and execute relevant tools to respond to appointment-related requests.

## ✨ Features

* **Doctor Discovery:** Retrieve the list of available doctors.
* **Appointment Availability:** Check available appointment slots.
* **Appointment Booking:** Book appointments using the available booking tools.
* **Appointment Cancellation:** Cancel existing appointments.
* **Appointment Lookup:** Retrieve details of an existing appointment.
* **Tool Calling:** Enable the AI agent to select and invoke tools based on user requests.
* **MCP Integration:** Expose healthcare operations through a Model Context Protocol server.
* **REST API:** Interact with the agent through FastAPI endpoints.
* **Conversation Threads:** Pass a `thread_id` to associate requests with a conversation thread.
* **Evaluation Suite:** Run structured evaluation cases to assess agent behavior and tool usage.

## 🛠️ Tech Stack

| Technology                   | Purpose                                                 |
| ---------------------------- | ------------------------------------------------------- |
| Python                       | Core application logic                                  |
| FastAPI                      | REST API and application server                         |
| Pydantic                     | Request validation and response schemas                 |
| LangChain                    | Agent orchestration and LLM integration                 |
| Groq                         | Language model inference                                |
| `openai/gpt-oss-120b`        | Configured model name, subject to provider availability |
| Model Context Protocol (MCP) | Tool integration for healthcare operations              |
| SQLite                       | Local database for appointment-related data             |
| Uvicorn                      | ASGI server                                             |
| python-dotenv                | Environment variable configuration                      |
| JSON                         | Evaluation cases and evaluation reports                 |

## 🏗️ Architecture

The application follows a tool-using agent architecture:

1. **Client:** Sends a natural-language request to the API.
2. **FastAPI:** Validates the request and forwards it to the agent.
3. **AI Agent:** Uses the configured language model to interpret the request and determine which tool is needed.
4. **MCP Tools:** Perform supported operations such as listing doctors, checking slots, booking appointments, cancelling appointments, and retrieving appointment details.
5. **Database Layer:** Handles local healthcare and appointment data.
6. **API Response:** Returns the agent's reply and information about the tools used.

## 📂 Project Structure

```text
upchar-care-agent/
├── agent.py                 # Agent initialization and execution
├── api.py                   # FastAPI application and endpoints
├── db.py                    # Database operations
├── mcp_server.py            # Healthcare tool definitions
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .gitignore               # Files excluded from Git
├── README.md                # Project documentation
└── evals/
    ├── eval_cases.json      # Evaluation test cases
    ├── run_evals.py         # Evaluation runner
    ├── latest.json          # Latest evaluation report
    ├── baseline.json        # Baseline evaluation report
    └── all_tests_passed.json
```

## ⚙️ Getting Started

### Prerequisites

* Python 3.10 or a compatible version supported by the installed dependencies
* A Groq API key
* Git (optional, for cloning the repository)

### 1. Clone the repository

```bash
git clone https://github.com/ShrutiGoswami14/upchar-care_agent.git
cd upchar-care_agent
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local `.env` file from the provided template:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure the values:

```dotenv
GROQ_API_KEY=your_groq_api_key
MODEL_NAME=openai/gpt-oss-120b
```

Use a model name currently supported by your Groq account if the configured model is unavailable.

**Security:** Never commit your real `.env` file or expose your API key in public repositories.

### 5. Start the API server

```powershell
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

The server will run locally at:

`http://127.0.0.1:8000`

## 🔌 API Endpoints

| Method | Endpoint  | Description                                                      |
| ------ | --------- | ---------------------------------------------------------------- |
| GET    | `/`       | Returns the application welcome message and endpoint information |
| GET    | `/health` | Checks API health                                                |
| POST   | `/chat`   | Sends a message to the AI agent                                  |

### Example: Chat with the agent

**Request**

```http
POST /chat
Content-Type: application/json
```

```json
{
  "message": "List all available doctors",
  "thread_id": "demo-session-1"
}
```

**Example response structure**

```json
{
  "reply": "Here are the doctors currently available at Upchar Health...",
  "tools_used": [
    {
      "tool": "list_doctors",
      "args": {}
    }
  ]
}
```

The actual reply and tool arguments depend on the request and the agent's execution.

### Interactive API documentation

Once the server is running, open:

* Swagger UI: http://127.0.0.1:8000/docs
* OpenAPI schema: http://127.0.0.1:8000/openapi.json
* Health check: http://127.0.0.1:8000/health

You can use Swagger UI to submit requests to the `/chat` endpoint without writing a separate client.

## 🧪 Evaluation and Testing

The project includes an evaluation suite under `evals/` to assess agent behavior across different healthcare appointment scenarios.

The evaluation cases cover areas such as:

* Doctor discovery and appointment availability
* Booking, cancellation, and appointment lookup
* Missing or invalid information
* Unavailable slots and booking conflicts
* Unknown doctors and unsupported requests
* Safety-related responses and prompt-injection attempts

Evaluation reports are stored as JSON files. Use the evaluation runner to execute the test suite according to the project's current implementation.

## 🔐 Safety and Limitations

* This project is a development and demonstration application, not a replacement for a qualified healthcare professional.
* It is intended for healthcare appointment assistance, not autonomous diagnosis or treatment.
* The availability and correctness of responses depend on the configured model, tools, and database contents.
* The current setup is intended for local development and requires additional security, privacy, persistence, and deployment work before production use.
* Do not store real patient information in a public development environment.

## 🎯 Project Objective

The goal of this project is to explore and demonstrate practical Agentic AI engineering concepts, including LLM integration, tool calling, MCP-based integrations, API development, database operations, and structured evaluation.



---

*Upchaar Care Agent — Exploring practical Agentic AI for healthcare appointment workflows.*
