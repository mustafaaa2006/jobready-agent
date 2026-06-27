# JobReady Agent — Submission Write-up

## Problem Statement
Youth unemployment remains a significant challenge globally. Many young job seekers — especially those without a university degree — struggle with the practical aspects of entering the workforce: writing a professional resume, understanding what skills they are missing, preparing for interviews, and finding entry-level roles that match their current abilities. Career counselors are often overworked or inaccessible. The JobReady agent provides free, personalized, 24/7 career coaching tailored specifically to youth entering the job market.

## Solution Architecture
*(See README.md for the visual architecture diagram)*

The system uses an ADK 2.0 graph-based workflow with an Orchestrator pattern.
1. The user enters the system via the **intake** node, which uses Human-in-the-Loop (HITL) to pause and collect their career context.
2. The input passes through a **security_checkpoint** node.
3. Safe requests flow to the **orchestrator** agent.
4. The orchestrator delegates the complex work to three specialists: **resume_builder**, **interview_coach**, and **job_matcher**.
5. These specialists are powered by the **JobReady MCP Server**, which provides ground-truth logic for job searches, skill gap analysis, and salary data.

## Concepts Used
- **ADK Workflow:** The entire agent runs as a graph defined in `app/agent.py` using `Workflow`, mapping nodes and edges explicitly.
- **LlmAgent:** Used for the orchestrator and the three specialist sub-agents.
- **AgentTool:** Enables the orchestrator to call the specialist agents directly.
- **MCP Server:** Implemented in `app/mcp_server.py` using `FastMCP` over `stdio`. It connects to the sub-agents via `MCPToolset`.
- **Security Checkpoint:** A custom Python function node placed *before* the LLM in the workflow graph, demonstrating defense-in-depth.
- **Agents CLI:** Scaffolded using `agents-cli`, run locally via the integrated playground.

## Security Design
The `security_checkpoint` node in `app/agent.py` implements three distinct controls:
1. **PII Scrubbing:** Automatically redacts phone numbers, SSNs, emails, national IDs, and dates of birth before they ever reach an LLM, returning them as `[EMAIL]`, `[PHONE]`, etc. This protects user privacy in a domain where people often paste their actual resumes.
2. **Prompt Injection Detection:** Scans for keywords ("ignore previous instructions", "jailbreak") and strictly blocks the execution by routing to a `SECURITY_EVENT` handler.
3. **Domain Ethics Filter:** Specific to the employment domain, it blocks requests asking how to falsify credentials, lie on a resume, or forge certificates.
4. **Audit Logging:** Every decision (PASS, WARNING, BLOCK) generates a structured JSON log for observability.

## MCP Server Design
The `mcp_server.py` implements five critical domain tools:
1. `search_job_listings`: Simulates querying a job board based on matched skills and experience level.
2. `analyse_resume`: A rule-based grading system that gives a 0-100 score and actionable feedback on resume text.
3. `get_interview_questions`: Pulls from a curated database of behavioral, situational, and role-specific technical questions.
4. `check_skill_gap`: Compares the user's skills against required skills for their target role, generating a "Readiness Score" and links to free Coursera/freeCodeCamp resources.
5. `get_salary_insights`: Provides realistic salary bands (adjusted by location modifier) and negotiation tips.

## HITL Flow
The `intake` node in `app/agent.py` uses ADK's `RequestInput` capability. When a user first connects, the workflow pauses before hitting any LLMs and explicitly asks for their educational background, experience, and goals. This ensures the orchestrator and sub-agents have high-quality context for all future turns, rather than relying on the user to guess what information they need to provide.

## Demo Walkthrough
1. **Intake:** The user launches the app and provides their background (e.g. "retail experience, looking for admin jobs").
2. **Analysis:** The user asks, "Find me a job and tell me what I'm missing."
3. **Delegation:** The orchestrator identifies the need for job matching and delegates to the `job_matcher` sub-agent.
4. **Tool Execution:** The sub-agent calls the MCP tools `search_job_listings` and `check_skill_gap`.
5. **Synthesis:** The user receives a list of real entry-level admin jobs, a note that they are missing "scheduling software" skills, and a link to a free course to learn it.

## Impact / Value Statement
JobReady democratizes access to professional career coaching. By combining compassionate LLM dialogue with rigid, rule-based career logic via MCP, it guides vulnerable young job seekers safely toward meaningful employment, ensuring they never have to face the job market alone.
