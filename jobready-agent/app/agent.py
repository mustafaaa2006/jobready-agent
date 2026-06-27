# ruff: noqa
# JobReady Agent — ADK 2.0 Workflow multi-agent implementation
# Coaches unemployed youth through resume building, interview prep, and job matching.

import json
import logging
import re
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.apps import App, ResumabilityConfig
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters
from google.adk.workflow import Workflow
from google.genai import types
from pydantic import BaseModel

from .config import config

logger = logging.getLogger(__name__)

# Configure MCP Server
import sys
from pathlib import Path
server_script = Path(__file__).parent / "mcp_server.py"
jobready_mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[str(server_script)],
        )
    )
)

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic output schemas
# ─────────────────────────────────────────────────────────────────────────────


class ResumeOutput(BaseModel):
    resume_content: str
    tips: list[str]


class InterviewOutput(BaseModel):
    questions: list[str]
    feedback: str


class JobMatchOutput(BaseModel):
    job_titles: list[str]
    strategy: str
    resources: list[str]


class OrchestratorOutput(BaseModel):
    response: str
    action_taken: str


# ─────────────────────────────────────────────────────────────────────────────
# Sub-agents (used via AgentTool by the orchestrator)
# ─────────────────────────────────────────────────────────────────────────────

resume_builder = LlmAgent(
    name="resume_builder",
    model=config.model,
    instruction="""You are an expert resume writer specializing in helping unemployed youth.
Given the user's background, skills, and target role, craft a compelling resume section or
provide specific improvement suggestions. Focus on transferable skills, volunteer work,
internships, and education. Always be encouraging and practical.

Return structured resume content with 3-5 actionable tips.""",
    tools=[jobready_mcp_toolset],
    output_schema=ResumeOutput,
    output_key="resume_result",
)

interview_coach = LlmAgent(
    name="interview_coach",
    model=config.model,
    instruction="""You are an expert interview coach helping youth enter the workforce.
Generate 5 role-specific interview questions (mix of behavioral, situational, and common)
along with model answer guidance and confidence-building coaching tips.

Return the questions list and practical feedback to help the user prepare.""",
    tools=[jobready_mcp_toolset],
    output_schema=InterviewOutput,
    output_key="interview_result",
)

job_matcher = LlmAgent(
    name="job_matcher",
    model=config.model,
    instruction="""You are a career counselor specializing in job placement for youth.
Match the user's skills and interests to 5 realistic job titles and roles.
Provide a step-by-step job search strategy and list 3-5 free resources
(platforms, programmes, or government schemes relevant to their situation).

Always consider entry-level positions, apprenticeships, and community programmes.""",
    tools=[jobready_mcp_toolset],
    output_schema=JobMatchOutput,
    output_key="job_match_result",
)

# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator — delegates to specialists via AgentTool
# ─────────────────────────────────────────────────────────────────────────────

orchestrator = LlmAgent(
    name="orchestrator",
    model=config.model,
    instruction="""You are the JobReady career coach orchestrator helping unemployed youth.
Analyse the user's request and delegate to the right specialist tool:

• resume_builder  — for resume writing, CV improvement, skills presentation
• interview_coach — for interview prep, practice questions, mock interviews
• job_matcher     — for finding jobs, career exploration, job search strategy

Always call at least one specialist. You may call more than one if the user needs multiple
types of help. After receiving specialist responses, synthesise a warm, encouraging, and
actionable summary that the user can act on today.""",
    tools=[
        AgentTool(agent=resume_builder),
        AgentTool(agent=interview_coach),
        AgentTool(agent=job_matcher),
    ],
    output_schema=OrchestratorOutput,
    output_key="orchestrator_result",
)

# ─────────────────────────────────────────────────────────────────────────────
# Workflow Function Nodes
# ─────────────────────────────────────────────────────────────────────────────


async def intake(ctx: Context, node_input: Any):
    """HITL intake — ask for career context on first run, then store in state."""
    if not ctx.resume_inputs:
        yield RequestInput(
            interrupt_id="career_context",
            message=(
                "👋 Welcome to JobReady!\n\n"
                "To give you the best guidance, please share:\n"
                "1. Your educational background (highest level, subjects)\n"
                "2. Any work, volunteer, or informal experience you have\n"
                "3. Skills you are confident in (e.g. language, computer, trade)\n"
                "4. The type of job or career you are aiming for\n"
                "5. What you need most help with: resume, interview prep, or finding jobs?\n\n"
                "Take your time — the more detail you share, the better I can help!"
            ),
        )
        return

    career_context = ctx.resume_inputs.get("career_context", "")

    # Extract text from the original user message (types.Content)
    original_msg = ""
    if hasattr(node_input, "parts"):
        original_msg = " ".join(
            p.text for p in node_input.parts if hasattr(p, "text") and p.text
        )

    combined = f"{original_msg}\n\nCareer Context provided by user:\n{career_context}".strip()

    yield Event(
        output=combined,
        state={"user_raw_input": combined, "career_context": career_context},
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(
                text="✅ Got it! Analysing your profile and connecting you with the right guidance..."
            )],
        ),
    )


def security_checkpoint(ctx: Context, node_input: Any) -> Event:
    """PII scrubbing, prompt injection detection, and structured audit logging."""
    # ── Extract plain text from node_input ──
    if hasattr(node_input, "parts"):
        text = " ".join(p.text for p in node_input.parts if hasattr(p, "text") and p.text)
    elif isinstance(node_input, str):
        text = node_input
    else:
        text = str(node_input)

    audit: dict[str, Any] = {
        "session_id": ctx.session.id,
        "node": "security_checkpoint",
        "original_length": len(text),
        "pii_detected": [],
        "injection_detected": False,
        "severity": "INFO",
        "action": "PASS",
    }

    # ── PII scrubbing — job-seeker domain ──
    if config.pii_redaction_enabled:
        pii_patterns = {
            "phone": (r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]"),
            "ssn": (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),
            "email": (r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", "[EMAIL]"),
            "national_id": (r"\b[A-Z]{1,2}\d{6,9}\b", "[ID]"),
            "dob": (
                r"\b(0?[1-9]|1[0-2])[\/\-](0?[1-9]|[12]\d|3[01])[\/\-](\d{2}|\d{4})\b",
                "[DOB]",
            ),
        }
        for pii_type, (pattern, replacement) in pii_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                audit["pii_detected"].append(pii_type)
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    if audit["pii_detected"]:
        audit["severity"] = "WARNING"

    # ── Prompt injection detection ──
    if config.injection_detection_enabled:
        injection_keywords = [
            "ignore previous instructions",
            "disregard your prompt",
            "you are now",
            "act as if",
            "jailbreak",
            "bypass safety",
            "forget you are",
            "new instructions:",
            "system prompt:",
            "reveal your instructions",
            "output your prompt",
            "pretend you have no restrictions",
        ]
        text_lower = text.lower()
        for kw in injection_keywords:
            if kw in text_lower:
                audit["injection_detected"] = True
                audit["severity"] = "CRITICAL"
                audit["action"] = "BLOCK"
                logger.warning(json.dumps(audit))
                return Event(
                    output="Security policy violation detected. Request blocked.",
                    route="SECURITY_EVENT",
                    state={"security_blocked": True, "audit_log": audit},
                    content=types.Content(
                        role="model",
                        parts=[types.Part.from_text(
                            text="⚠️ Your request was flagged by our security policy and cannot be processed."
                        )],
                    ),
                )

    # ── Domain rule: no advice on falsifying credentials ──
    ethics_violations = [
        "how to fake",
        "forge a certificate",
        "falsify",
        "lie on my resume",
        "fake experience",
        "counterfeit degree",
    ]
    for term in ethics_violations:
        if term in text.lower():
            audit["severity"] = "CRITICAL"
            audit["action"] = "BLOCK"
            logger.warning(json.dumps(audit))
            return Event(
                output="Request blocked: content violates ethical guidelines.",
                route="SECURITY_EVENT",
                state={"security_blocked": True, "audit_log": audit},
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(
                        text="⚠️ JobReady only helps with honest, ethical career preparation. "
                             "We can't assist with falsifying credentials."
                    )],
                ),
            )

    logger.info(json.dumps(audit))
    return Event(
        output=text,
        route="safe",
        state={"sanitized_input": text, "audit_log": audit},
    )


def security_blocked_output(ctx: Context, node_input: Any) -> Event:
    """Formats the security-blocked response for the UI."""
    msg = (
        node_input
        if isinstance(node_input, str)
        else "Your request was blocked by our security policy."
    )
    return Event(
        output=msg,
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=f"🔒 {msg}")],
        ),
    )


def final_output(ctx: Context, node_input: Any) -> Event:
    """Formats the orchestrator's response for the playground UI."""
    if isinstance(node_input, dict):
        response = node_input.get("response", str(node_input))
    elif hasattr(node_input, "parts"):
        response = " ".join(
            p.text for p in node_input.parts if hasattr(p, "text") and p.text
        )
    else:
        response = str(node_input)

    display = f"🎯 **JobReady Guidance**\n\n{response}"
    return Event(
        output=response,
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=display)],
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Workflow Graph
# ─────────────────────────────────────────────────────────────────────────────
# Edge rule enforced: only ONE edge between any (source, target) pair.
# Routes "safe" and "SECURITY_EVENT" go to DIFFERENT targets — no duplicates.

root_agent = Workflow(
    name="jobready_workflow",
    description=(
        "Coaches unemployed youth through resume building, interview prep, "
        "and job matching using a secure multi-agent workflow."
    ),
    edges=[
        # Entry: collect user profile via HITL
        ("START", intake),
        # Security gate: PII scrub + injection check
        (intake, security_checkpoint),
        # Route: "safe" → orchestrator, "SECURITY_EVENT" → blocked handler
        (security_checkpoint, {"safe": orchestrator, "SECURITY_EVENT": security_blocked_output}),
        # Both paths converge on final_output (different sources → no duplicate edge rule violation)
        (orchestrator, final_output),
        (security_blocked_output, final_output),
    ],
)

app = App(
    name="app",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
