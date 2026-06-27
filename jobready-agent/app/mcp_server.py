"""
JobReady MCP Server — stdio transport
Domain tools for job coaching: job search, resume scoring, interview Q&A,
skill-gap analysis, and salary insights.
"""

import json
import random
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("jobready-tools")


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1: Search Job Listings
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def search_job_listings(
    skills: str,
    location: str = "remote",
    experience_level: str = "entry",
) -> str:
    """Search for job listings that match a candidate's skills and location.

    Args:
        skills: Comma-separated list of skills (e.g. "Python, Excel, communication").
        location: City, country, or "remote". Default is "remote".
        experience_level: One of "entry", "junior", "mid", "senior". Default "entry".

    Returns:
        JSON string with a list of matching job listings.
    """
    skill_list = [s.strip().lower() for s in skills.split(",")]

    # Simulated job database keyed by common skill clusters
    job_pool = [
        {
            "title": "Junior Data Analyst",
            "company": "DataBridge Ltd",
            "location": location,
            "match_skills": ["excel", "data", "analysis", "python", "sql"],
            "apply_url": "https://example.com/jobs/junior-data-analyst",
            "salary_range": "$35,000–$50,000",
        },
        {
            "title": "Customer Support Specialist",
            "company": "HelpFirst Inc",
            "location": location,
            "match_skills": ["communication", "customer service", "problem solving"],
            "apply_url": "https://example.com/jobs/customer-support",
            "salary_range": "$28,000–$40,000",
        },
        {
            "title": "Social Media Coordinator",
            "company": "BrandWave",
            "location": location,
            "match_skills": ["social media", "content", "communication", "creativity"],
            "apply_url": "https://example.com/jobs/social-media-coordinator",
            "salary_range": "$30,000–$45,000",
        },
        {
            "title": "IT Support Technician",
            "company": "TechAssist Co",
            "location": location,
            "match_skills": ["it", "computer", "networking", "troubleshooting", "hardware"],
            "apply_url": "https://example.com/jobs/it-support-technician",
            "salary_range": "$32,000–$48,000",
        },
        {
            "title": "Administrative Assistant",
            "company": "Officeworks Group",
            "location": location,
            "match_skills": ["organisation", "word", "excel", "communication", "scheduling"],
            "apply_url": "https://example.com/jobs/admin-assistant",
            "salary_range": "$27,000–$38,000",
        },
        {
            "title": "Retail Sales Associate",
            "company": "ShopSmart",
            "location": location,
            "match_skills": ["sales", "customer service", "communication", "retail"],
            "apply_url": "https://example.com/jobs/retail-sales",
            "salary_range": "$25,000–$35,000",
        },
        {
            "title": "Junior Web Developer",
            "company": "WebCraft Agency",
            "location": location,
            "match_skills": ["html", "css", "javascript", "python", "web", "coding"],
            "apply_url": "https://example.com/jobs/junior-web-developer",
            "salary_range": "$40,000–$60,000",
        },
        {
            "title": "Community Outreach Worker",
            "company": "CareConnect NGO",
            "location": location,
            "match_skills": ["community", "communication", "volunteer", "social work"],
            "apply_url": "https://example.com/jobs/outreach-worker",
            "salary_range": "$28,000–$42,000",
        },
    ]

    # Score jobs by matching skills
    results = []
    for job in job_pool:
        score = sum(1 for sk in skill_list if any(sk in ms for ms in job["match_skills"]))
        if score > 0 or experience_level == "entry":
            job_copy = dict(job)
            job_copy["match_score"] = score
            results.append(job_copy)

    results.sort(key=lambda j: j["match_score"], reverse=True)
    top = results[:5]

    return json.dumps({"jobs_found": len(top), "listings": top}, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2: Analyse Resume
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def analyse_resume(resume_text: str, target_role: str = "") -> str:
    """Analyse a resume/CV text and return a score with improvement suggestions.

    Args:
        resume_text: The full text of the candidate's resume or CV.
        target_role: Optional. The job title or role the candidate is applying for.

    Returns:
        JSON string with score (0–100), strengths, and improvement suggestions.
    """
    text_lower = resume_text.lower()
    score = 40  # base score
    strengths = []
    suggestions = []

    # Check for key resume sections
    if any(kw in text_lower for kw in ["education", "degree", "school", "university", "college"]):
        score += 10
        strengths.append("Education section present")
    else:
        suggestions.append("Add an Education section listing your highest qualification")

    if any(kw in text_lower for kw in ["experience", "worked", "internship", "volunteer"]):
        score += 15
        strengths.append("Experience or work history included")
    else:
        suggestions.append("Include any work, volunteer, or informal experience you have")

    if any(kw in text_lower for kw in ["skills", "proficient", "competencies", "abilities"]):
        score += 10
        strengths.append("Skills section found")
    else:
        suggestions.append("Add a dedicated Skills section with specific competencies")

    if any(kw in text_lower for kw in ["achieved", "improved", "led", "created", "managed", "increased"]):
        score += 15
        strengths.append("Action verbs and achievements detected")
    else:
        suggestions.append("Use strong action verbs (achieved, led, improved) and quantify results")

    if len(resume_text) > 300:
        score += 5
        strengths.append("Resume has sufficient content")
    else:
        suggestions.append("Expand your resume — aim for at least one full page")

    if target_role:
        role_lower = target_role.lower()
        if role_lower in text_lower:
            score += 5
            strengths.append(f"Resume mentions the target role '{target_role}'")
        else:
            suggestions.append(
                f"Tailor your resume to mention '{target_role}' and related keywords"
            )

    score = min(score, 100)

    return json.dumps(
        {
            "score": score,
            "grade": "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D",
            "strengths": strengths,
            "suggestions": suggestions,
            "target_role": target_role or "not specified",
        },
        indent=2,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3: Get Interview Questions
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_interview_questions(role: str, question_type: str = "mixed") -> str:
    """Retrieve domain-specific interview questions for a given job role.

    Args:
        role: The job title or role (e.g. "customer support", "data analyst").
        question_type: One of "behavioral", "situational", "technical", or "mixed".

    Returns:
        JSON string with a list of interview questions and tips.
    """
    role_lower = role.lower()

    behavioral = [
        "Tell me about a time you dealt with a difficult person at work or school.",
        "Describe a situation where you had to learn something quickly.",
        "Give an example of a goal you set and how you achieved it.",
        "Tell me about a time you worked as part of a team to accomplish something.",
        "Describe a challenge you faced and how you overcame it.",
    ]

    situational = [
        "If you had two urgent tasks due at the same time, how would you prioritise?",
        "What would you do if a customer or colleague was unhappy with your work?",
        "If you discovered a mistake you had made, what steps would you take?",
        "How would you handle working with someone who has a very different working style?",
    ]

    # Role-specific technical questions
    technical_by_role: dict[str, list[str]] = {
        "data analyst": [
            "What is the difference between a JOIN and a UNION in SQL?",
            "How do you handle missing data in a dataset?",
            "Explain what a pivot table is and when you would use one.",
        ],
        "customer support": [
            "What does good customer service mean to you?",
            "How do you de-escalate an angry customer?",
            "Walk me through how you would handle a billing dispute.",
        ],
        "web developer": [
            "What is the difference between HTML, CSS, and JavaScript?",
            "Explain what responsive design means.",
            "What tools do you use to debug a website?",
        ],
        "it support": [
            "What steps do you take when a user cannot connect to the internet?",
            "What is Active Directory?",
            "How do you prioritise support tickets?",
        ],
        "admin": [
            "What software tools do you use to manage schedules and documents?",
            "How do you ensure accuracy when entering data?",
            "Describe how you would organise a large meeting or event.",
        ],
    }

    # Find best matching role category
    technical: list[str] = []
    for key, qs in technical_by_role.items():
        if key in role_lower or any(word in role_lower for word in key.split()):
            technical = qs
            break
    if not technical:
        technical = [
            f"What experience or training do you have relevant to {role}?",
            f"What do you think are the most important skills for a {role}?",
            "How do you keep your professional skills up to date?",
        ]

    if question_type == "behavioral":
        questions = behavioral
    elif question_type == "situational":
        questions = situational
    elif question_type == "technical":
        questions = technical
    else:
        # mixed
        questions = behavioral[:2] + situational[:2] + technical[:3]

    tips = [
        "Use the STAR method: Situation, Task, Action, Result.",
        "Research the company before the interview.",
        "Prepare 2–3 questions to ask the interviewer at the end.",
        "Arrive 10 minutes early or log in 5 minutes early for virtual interviews.",
        "Bring a printed copy of your resume and a notepad.",
    ]

    return json.dumps({"role": role, "questions": questions, "interview_tips": tips}, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4: Check Skill Gap
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def check_skill_gap(user_skills: str, target_role: str) -> str:
    """Compare a user's skills against typical requirements for a target job role.

    Args:
        user_skills: Comma-separated list of skills the user has.
        target_role: The job title or role the user is targeting.

    Returns:
        JSON string with matched skills, missing skills, and free learning resources.
    """
    user_skill_set = {s.strip().lower() for s in user_skills.split(",")}
    role_lower = target_role.lower()

    role_requirements: dict[str, dict] = {
        "data analyst": {
            "required": ["sql", "excel", "data visualisation", "python", "statistics"],
            "nice_to_have": ["power bi", "tableau", "r", "machine learning"],
        },
        "customer support": {
            "required": ["communication", "patience", "problem solving", "computer literacy"],
            "nice_to_have": ["crm software", "foreign language", "conflict resolution"],
        },
        "web developer": {
            "required": ["html", "css", "javascript", "git", "responsive design"],
            "nice_to_have": ["react", "nodejs", "typescript", "ux design"],
        },
        "it support": {
            "required": ["networking", "troubleshooting", "windows os", "hardware"],
            "nice_to_have": ["linux", "cloud", "cybersecurity", "active directory"],
        },
        "admin assistant": {
            "required": ["microsoft word", "excel", "email", "organisation", "scheduling"],
            "nice_to_have": ["google workspace", "project management", "bookkeeping"],
        },
    }

    # Find best matching role
    req_data: dict = {"required": [], "nice_to_have": []}
    for key, reqs in role_requirements.items():
        if key in role_lower or any(word in role_lower for word in key.split()):
            req_data = reqs
            break

    if not req_data["required"]:
        req_data = {
            "required": ["communication", "teamwork", "problem solving", "computer literacy"],
            "nice_to_have": ["time management", "leadership"],
        }

    matched = [r for r in req_data["required"] if any(r in us for us in user_skill_set)]
    missing = [r for r in req_data["required"] if r not in matched]

    free_resources = [
        {"skill": s, "resource": f"https://www.coursera.org/search?query={s.replace(' ', '+')}"}
        for s in missing[:3]
    ] + [
        {"name": "Google Career Certificates", "url": "https://grow.google/certificates/"},
        {"name": "freeCodeCamp", "url": "https://www.freecodecamp.org/"},
        {"name": "Khan Academy", "url": "https://www.khanacademy.org/"},
    ]

    gap_pct = round((len(missing) / max(len(req_data["required"]), 1)) * 100)

    return json.dumps(
        {
            "target_role": target_role,
            "skills_you_have": matched,
            "skills_to_develop": missing,
            "skill_gap_percentage": f"{gap_pct}%",
            "readiness": "High" if gap_pct < 30 else "Medium" if gap_pct < 60 else "Low",
            "free_learning_resources": free_resources,
        },
        indent=2,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tool 5: Get Salary Insights
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_salary_insights(role: str, location: str = "global", experience_years: int = 0) -> str:
    """Retrieve salary range and negotiation tips for a given role and location.

    Args:
        role: The job title (e.g. "data analyst", "customer support").
        location: Country or city name, or "global". Default "global".
        experience_years: Years of relevant experience. Default 0 (entry level).

    Returns:
        JSON string with salary range, median, negotiation tips, and benefits to ask for.
    """
    role_lower = role.lower()

    salary_db: dict[str, dict] = {
        "data analyst": {"entry": (35000, 50000), "mid": (55000, 75000), "senior": (80000, 110000)},
        "customer support": {"entry": (25000, 38000), "mid": (40000, 55000), "senior": (58000, 75000)},
        "web developer": {"entry": (40000, 60000), "mid": (65000, 90000), "senior": (95000, 140000)},
        "it support": {"entry": (30000, 48000), "mid": (50000, 70000), "senior": (72000, 95000)},
        "admin assistant": {"entry": (26000, 38000), "mid": (40000, 52000), "senior": (55000, 68000)},
        "social media": {"entry": (28000, 42000), "mid": (45000, 62000), "senior": (65000, 90000)},
    }

    level = "senior" if experience_years >= 5 else "mid" if experience_years >= 2 else "entry"

    # Find best match
    range_data = (30000, 45000)  # default
    for key, data in salary_db.items():
        if key in role_lower or any(word in role_lower for word in key.split()):
            range_data = data[level]
            break

    lo, hi = range_data
    median = (lo + hi) // 2

    # Simple location multiplier
    loc_lower = location.lower()
    multiplier = (
        1.4 if any(city in loc_lower for city in ["london", "new york", "san francisco", "sydney"])
        else 1.2 if any(city in loc_lower for city in ["toronto", "dubai", "singapore"])
        else 0.7 if any(city in loc_lower for city in ["india", "pakistan", "nigeria", "kenya"])
        else 1.0
    )

    lo_adj = int(lo * multiplier)
    hi_adj = int(hi * multiplier)
    median_adj = int(median * multiplier)

    currency = "USD"

    negotiation_tips = [
        "Research the market rate before negotiating — use Glassdoor and LinkedIn Salary.",
        "Don't give a number first; ask 'What is the budgeted range for this role?'",
        "Negotiate the full package: salary + benefits + remote flexibility.",
        "Be confident but grateful — frame it as 'I was hoping for X based on my research'.",
        "Practice your negotiation pitch out loud before the conversation.",
    ]

    benefits_to_ask = [
        "Remote or hybrid working options",
        "Professional development budget or course sponsorship",
        "Health insurance or wellness allowance",
        "Extra annual leave",
        "Performance review schedule",
    ]

    return json.dumps(
        {
            "role": role,
            "location": location,
            "experience_level": level,
            "salary_range": f"{currency} {lo_adj:,}–{hi_adj:,}",
            "median_salary": f"{currency} {median_adj:,}",
            "negotiation_tips": negotiation_tips,
            "benefits_to_negotiate": benefits_to_ask,
        },
        indent=2,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
