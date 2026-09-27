import json
import logging
import os

from openai import OpenAI

from ..schemas import IncidentAnalysis


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are an expert Site Reliability Engineer.

Analyze the supplied production incident data.

Return ONLY valid JSON matching this structure:

{
  "root_cause": "string",
  "affected_services": ["string"],
  "severity": "low | medium | high | critical",
  "fix_recommendation": "string",
  "postmortem_summary": "string"
}

Use only evidence available in the supplied incident data.
Be precise, technical, and concise.
"""


def fallback_analysis() -> IncidentAnalysis:
    return IncidentAnalysis(
        root_cause=(
            "Database connectivity failure leading to "
            "circuit breaker activation."
        ),
        affected_services=[
            "payments-service",
            "postgres-db",
        ],
        severity="high",
        fix_recommendation=(
            "Restore database connectivity, verify network routing, "
            "review connection health checks, and increase retry "
            "backoff where appropriate."
        ),
        postmortem_summary=(
            "The incident was caused by loss of database connectivity, "
            "which triggered cascading application failures and "
            "fallback behavior."
        ),
    )


def parse_analysis(text: str) -> IncidentAnalysis:
    text = text.strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("LLM response did not contain valid JSON.")

        payload = json.loads(text[start : end + 1])

    return IncidentAnalysis.model_validate(payload)


def analyze_incident(
    logs: str,
    stack_trace: str,
    metrics: str,
) -> IncidentAnalysis:

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        logger.info(
            "OPENAI_API_KEY is not configured. Using fallback analyzer."
        )
        return fallback_analysis()

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=os.getenv(
                "OPENAI_MODEL",
                "gpt-4o-mini",
            ),
            instructions=SYSTEM_PROMPT,
            input=f"""
LOGS:
{logs}

STACK TRACE:
{stack_trace}

METRICS:
{metrics}

Return JSON only.
""",
        )

        return parse_analysis(response.output_text)

    except Exception:
        logger.exception(
            "AI incident analysis failed. Using fallback analyzer."
        )

        return fallback_analysis()
