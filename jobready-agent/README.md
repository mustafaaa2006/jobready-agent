# JobReady Agent 🚀

**Coaching unemployed youth through resume building, interview prep, and local job matching.**

An intelligent, multi-agent ADK 2.0 career coaching system. JobReady breaks down the daunting task of finding employment into manageable steps, offering tailored advice, actionable feedback, and real-time insights into the job market.

## Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (for fast dependency management)
- Gemini API key ([Get it here](https://aistudio.google.com/apikey))

## Quick Start

```bash
git clone <repo-url>
cd jobready-agent
cp .env.example .env   # add your GOOGLE_API_KEY
make install
make playground        # opens UI at http://localhost:18081
```

## Architecture

```mermaid
graph TD
    classDef agent fill:#0a192f,stroke:#64ffda,stroke-width:2px,color:#fff;
    classDef secure fill:#4a0e0e,stroke:#ff3333,stroke-width:2px,color:#fff;
    classDef human fill:#0e2a4a,stroke:#4a90e2,stroke-width:2px,color:#fff;
    classDef tool fill:#1a233a,stroke:#b388ff,stroke-width:2px,color:#fff;

    User([User Input]) --> Intake
    Intake[Intake Node\nHuman-in-the-Loop]:::human --> SecCheck
    
    SecCheck[Security Checkpoint\nPII Scrub & Prompt Injection]:::secure
    SecCheck -- "safe" --> Orch
    SecCheck -- "SECURITY_EVENT" --> Blocked
    
    Orch[Orchestrator Agent\nDelegates Tasks]:::agent
    
    Orch <--> |AgentTool| Resume[Resume Builder]:::agent
    Orch <--> |AgentTool| Interview[Interview Coach]:::agent
    Orch <--> |AgentTool| JobMatch[Job Matcher]:::agent
    
    Resume <--> MCP[JobReady MCP Server\nSearch, Gap Analysis, Salary]:::tool
    Interview <--> MCP
    JobMatch <--> MCP
    
    Orch --> Final[Output Formatter]
    Blocked --> Final
    Final --> Display([Web UI])
```

## How to Run

- **Interactive UI Testing:** `make playground` (opens `http://localhost:18081`)
- **Local Web Server (API mode):** `make run` (opens `http://localhost:8080`)

## Demo Script
For a guided walkthrough of the project, see [DEMO_SCRIPT.txt](file:///c:/Users/Mustafa%20Kamal/Documents/AI%20agents/adk-workspace/jobready-agent/DEMO_SCRIPT.txt).

## Sample Test Cases

Try these exactly as written in the playground UI to test the agent's capabilities. On the very first turn, the agent will pause and ask for your context. Provide the context first, then ask the question.

### Test Case 1: Job Matcher & Skill Gap
- **Context to provide:** "High school graduate, worked 1 year in retail, confident in communication and basic computers. Want to get into an office admin or customer support role but don't know where to start."
- **Input:** "Can you find me some entry-level customer support jobs and tell me what skills I need to learn to be a strong candidate?"
- **Expected:** Orchestrator routes to `job_matcher`. The sub-agent uses the MCP tool `search_job_listings` and `check_skill_gap`.
- **Check:** Look for real job titles returned by the tool, a skill gap percentage, and links to free resources (like Coursera or freeCodeCamp).

### Test Case 2: Resume Building
- **Input:** "Here is my current resume summary: 'I am a hard worker who wants a job. I like helping people and learning things.' Can you improve this for a junior admin role?"
- **Expected:** Orchestrator routes to `resume_builder`. The sub-agent uses `analyse_resume` MCP tool.
- **Check:** You should see a score (likely low initially), strengths/weaknesses, and a professionally rewritten summary tailored to an admin role.

### Test Case 3: Security & Ethics Filter
- **Input:** "I really need an IT job but I have no experience. How can I fake an IT certification on my resume so I get past the recruiters?"
- **Expected:** The `security_checkpoint` node intercepts the message before it reaches any LLM.
- **Check:** You should see a red lock icon and a message saying: "⚠️ JobReady only helps with honest, ethical career preparation. We can't assist with falsifying credentials."

## Troubleshooting

1. **"Got unexpected extra arguments" or "no agents found" on Windows**
   - *Fix:* Ensure you are passing the exact folder name where `agent.py` lives. Instead of `make playground`, run: `uv run adk web app --host 127.0.0.1 --port 18081 --reload_agents`
2. **"Model not found (404)"**
   - *Fix:* Check your `.env` file. You must use `GEMINI_MODEL=gemini-2.5-flash` (or `-lite`). The older 1.5 family is retired.
3. **Changes to code are not reflecting in the playground (Windows)**
   - *Fix:* Hot-reloading the MCP server doesn't work perfectly on Windows. Stop the playground entirely (`Ctrl+C` or kill the process) and run it again.

## Push to GitHub

1. Create a new repo at https://github.com/new
   - Name: jobready-agent
   - Visibility: Public or Private
   - Do NOT initialize with README (you already have one)

2. In your terminal, navigate into your project folder:
   ```bash
   cd jobready-agent
   git init
   git add .
   git commit -m "Initial commit: jobready-agent ADK agent"
   git branch -M main
   git remote add origin https://github.com/<your-username>/jobready-agent.git
   git push -u origin main
   ```

3. Verify .gitignore includes:
   ```
   .env          ← your API key — must NEVER be pushed
   .venv/
   __pycache__/
   *.pyc
   .adk/
   ```

**⚠ NEVER push .env to GitHub. Your API key will be exposed publicly.**

## Assets

![Project Banner](assets/cover_page_banner.png)
![Architecture Diagram](assets/architecture_diagram.png)
