"""AI diagnosis engine: call LLM API to generate improvement suggestions."""
from __future__ import annotations

import json
import os
from typing import Any

import httpx

DEEPSEEK_BASE = "https://api.deepseek.com/v1"
OPENAI_BASE = "https://api.openai.com/v1"
TIMEOUT = 30.0

PROMPT_RULES = """Rules:
- severity: "high" for critical issues (score < 50), "medium" (50-70), "low" (>70)
- estimated_hours: realistic fix time (1-40 hours)
- confidence: your certainty in the suggestion (0-100)
- Suggestions must reference specific dimension scores
- Order by severity (high first)
- Output ONLY valid JSON array, no other text"""

SYSTEM_PROMPT = (
    "You are a code health expert. Based on the following six-dimension analysis of a "
    "GitHub repository, generate 3-5 specific, actionable improvement suggestions.\n\n"
    "Output MUST be a JSON array of objects with this exact schema:\n"
    '[{"advice":"suggestion (in Chinese)","severity":"high|medium|low",'
    '"estimated_hours":int,"confidence":int(0-100)}]\n\n' + PROMPT_RULES
)


def _get_client() -> tuple[str | None, str, str]:
    """Determine which LLM provider to use."""
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    if deepseek_key:
        return deepseek_key, DEEPSEEK_BASE, "deepseek"
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        return openai_key, OPENAI_BASE, "openai"
    return None, "", ""


def _build_user_prompt(dimensions: list[dict[str, Any]], repo_url: str) -> str:
    """Build the user prompt from dimension analysis results."""
    lines = [f"Repository: {repo_url}", ""]
    for dim in dimensions:
        name = dim.get("dimension", "unknown")
        score = dim.get("score", 0)
        issues = dim.get("issues", [])
        lines.append(f"- {name}: score={score}")
        if issues:
            for issue in issues[:3]:
                lines.append(f"  • {issue}")
    lines.append("")
    lines.append("Generate 3-5 improvement suggestions as JSON array.")
    return "\n".join(lines)


def _parse_llm_response(text: str) -> list[dict[str, Any]]:
    """Parse LLM JSON response, with fallback handling."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        suggestions = json.loads(text)
        if isinstance(suggestions, list):
            return suggestions
    except json.JSONDecodeError:
        import re
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return []


def _post_process(suggestions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate, normalize and mark low-confidence suggestions."""
    result = []
    for s in suggestions:
        advice = s.get("advice", "")
        if not advice:
            continue
        severity = s.get("severity", "medium")
        if severity not in ("high", "medium", "low"):
            severity = "medium"
        estimated_hours = s.get("estimated_hours", 0)
        try:
            estimated_hours = int(estimated_hours)
        except (ValueError, TypeError):
            estimated_hours = 0
        confidence = s.get("confidence", 50)
        try:
            confidence = int(confidence)
        except (ValueError, TypeError):
            confidence = 50
        confidence = max(0, min(100, confidence))
        result.append({
            "advice": advice,
            "severity": severity,
            "estimated_hours": max(1, estimated_hours),
            "confidence": confidence,
            "need_human_review": confidence < 70,
        })
    severity_order = {"high": 0, "medium": 1, "low": 2}
    result.sort(key=lambda x: (severity_order.get(x["severity"], 1), -x["confidence"]))
    return result[:5]


def _fallback_diagnosis(dimensions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate rule-based suggestions when LLM is unavailable."""
    suggestions = []
    for dim in dimensions:
        score = dim.get("score", 100)
        name = dim.get("dimension", "")
        if score < 40:
            suggestions.append({
                "advice": f"[{name}] 得分 {score}，需优先改进该维度",
                "severity": "high",
                "estimated_hours": 8,
                "confidence": 85,
                "need_human_review": False,
            })
        elif score < 60:
            suggestions.append({
                "advice": f"[{name}] 得分 {score}，建议查阅最佳实践并逐步改善",
                "severity": "medium",
                "estimated_hours": 4,
                "confidence": 70,
                "need_human_review": False,
            })
    if not suggestions:
        suggestions.append({
            "advice": "各项指标良好，保持现有代码质量并定期进行检查",
            "severity": "low",
            "estimated_hours": 1,
            "confidence": 90,
            "need_human_review": False,
        })
    return suggestions[:5]


async def ai_diagnose(
    dimensions: list[dict[str, Any]], repo_url: str
) -> list[dict[str, Any]]:
    """Generate AI-powered improvement suggestions."""
    api_key, base_url, provider = _get_client()
    if not api_key:
        return _fallback_diagnosis(dimensions)

    user_prompt = _build_user_prompt(dimensions, repo_url)
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat" if provider == "deepseek" else "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1024,
                },
            )
        if resp.status_code != 200:
            return _fallback_diagnosis(dimensions)
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        suggestions = _parse_llm_response(content)
        if not suggestions:
            return _fallback_diagnosis(dimensions)
        return _post_process(suggestions)
    except (httpx.TimeoutException, httpx.RequestError, Exception):
        return _fallback_diagnosis(dimensions)
