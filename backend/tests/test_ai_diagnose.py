"""Tests for AI diagnosis module."""
import asyncio
from pathlib import Path  # noqa: F401
from unittest.mock import AsyncMock, MagicMock, patch

from backend.ai.diagnose import (
    _build_user_prompt,
    _fallback_diagnosis,
    _get_client,
    _parse_llm_response,
    _post_process,
    ai_diagnose,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestClientDetection:
    def test_detect_deepseek(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        key, base, provider = _get_client()
        assert provider == "deepseek"
        assert key == "sk-test"

    def test_detect_openai(self, monkeypatch):
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        key, base, provider = _get_client()
        assert provider == "openai"
        assert key == "sk-test"

    def test_no_key(self, monkeypatch):
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        key, base, provider = _get_client()
        assert key is None
        assert provider == ""


class TestParseLLMResponse:
    def test_parse_valid_json(self):
        text = '[{"advice": "test", "severity": "high", "estimated_hours": 2, "confidence": 80}]'
        result = _parse_llm_response(text)
        assert len(result) == 1
        assert result[0]["advice"] == "test"

    def test_parse_with_markdown_fence(self):
        text = '```json\n[{"advice": "test", "severity": "high", "estimated_hours": 2, "confidence": 80}]\n```'
        result = _parse_llm_response(text)
        assert len(result) == 1

    def test_parse_invalid_json(self):
        text = 'not valid json at all'
        result = _parse_llm_response(text)
        assert result == []

    def test_parse_json_embedded_in_text(self):
        text = 'Some text before [{"advice": "test", "severity": "high", "estimated_hours": 2, "confidence": 80}] some after'
        result = _parse_llm_response(text)
        assert len(result) == 1


class TestPostProcess:
    def test_normalize_severity(self):
        suggestions = [{"advice": "test", "severity": "critical", "estimated_hours": 2, "confidence": 80}]
        result = _post_process(suggestions)
        assert result[0]["severity"] == "medium"

    def test_mark_low_confidence(self):
        suggestions = [
            {"advice": "a", "severity": "high", "estimated_hours": 2, "confidence": 65},
            {"advice": "b", "severity": "high", "estimated_hours": 4, "confidence": 85},
        ]
        result = _post_process(suggestions)
        # Sorted by severity then confidence desc: 85 first, 65 second
        assert result[0]["confidence"] == 85
        assert result[1]["confidence"] == 65
        assert result[0]["need_human_review"] is False  # confidence 85 >= 70
        assert result[1]["need_human_review"] is True   # confidence 65 < 70

    def test_sort_by_severity(self):
        suggestions = [
            {"advice": "low-sev", "severity": "low", "estimated_hours": 1, "confidence": 90},
            {"advice": "high-sev", "severity": "high", "estimated_hours": 8, "confidence": 90},
            {"advice": "mid-sev", "severity": "medium", "estimated_hours": 4, "confidence": 90},
        ]
        result = _post_process(suggestions)
        assert result[0]["advice"] == "high-sev"
        assert result[2]["advice"] == "low-sev"

    def test_limit_five(self):
        suggestions = [{"advice": f"s{i}", "severity": "medium", "estimated_hours": 2, "confidence": 80}
                       for i in range(10)]
        result = _post_process(suggestions)
        assert len(result) == 5

    def test_filter_empty_advice(self):
        suggestions = [
            {"advice": "", "severity": "high", "estimated_hours": 2, "confidence": 80},
            {"advice": "real", "severity": "medium", "estimated_hours": 4, "confidence": 80},
        ]
        result = _post_process(suggestions)
        assert len(result) == 1
        assert result[0]["advice"] == "real"


class TestFallback:
    def test_low_score_triggers_high(self):
        dims = [{"dimension": "code_quality", "score": 30, "issues": ["issue1"]}]
        result = _fallback_diagnosis(dims)
        assert len(result) >= 1
        assert any(s["severity"] == "high" for s in result)

    def test_medium_score_triggers_medium(self):
        dims = [{"dimension": "code_quality", "score": 55, "issues": []}]
        result = _fallback_diagnosis(dims)
        assert any(s["severity"] == "medium" for s in result)

    def test_all_good(self):
        dims = [{"dimension": "code_quality", "score": 90, "issues": []}]
        result = _fallback_diagnosis(dims)
        assert len(result) >= 1
        assert result[0]["severity"] == "low"


class TestBuildPrompt:
    def test_build_prompt(self):
        dims = [{"dimension": "code_quality", "score": 85, "issues": ["issue1", "issue2"]}]
        prompt = _build_user_prompt(dims, "https://github.com/a/b")
        assert "a/b" in prompt
        assert "code_quality" in prompt
        assert "85" in prompt
        assert "issue1" in prompt


class TestAsyncDiagnose:
    def test_fallback_when_no_key(self, monkeypatch):
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        result = asyncio.run(ai_diagnose(
            [{"dimension": "code_quality", "score": 30, "issues": []}],
            "https://github.com/a/b"
        ))
        assert len(result) >= 1
        assert all("advice" in s for s in result)
        assert all("severity" in s for s in result)
        assert all("confidence" in s for s in result)
        assert all("need_human_review" in s for s in result)

    @patch("backend.ai.diagnose.httpx.AsyncClient")
    def test_mock_llm_success(self, mock_client, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": '[{"advice": "Fix bugs", "severity": "high", "estimated_hours": 5, "confidence": 85}]'}}]
        }
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)

        result = asyncio.run(ai_diagnose(
            [{"dimension": "code_quality", "score": 50, "issues": []}],
            "https://github.com/a/b"
        ))
        assert len(result) == 1
        assert result[0]["advice"] == "Fix bugs"
        assert result[0]["severity"] == "high"
        assert result[0]["confidence"] == 85
        assert result[0]["need_human_review"] is False

    @patch("backend.ai.diagnose.httpx.AsyncClient")
    def test_mock_llm_timeout_fallback(self, mock_client, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=__import__("httpx").TimeoutException("timeout")
        )

        result = asyncio.run(ai_diagnose(
            [{"dimension": "code_quality", "score": 30, "issues": []}],
            "https://github.com/a/b"
        ))
        assert len(result) >= 1
