"""End-to-end test: analyze our own repository."""
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.analyzer.aggregator import aggregate
from backend.ai.diagnose import ai_diagnose

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/user/repo-health-check"


async def main():
    print("=== Repo Health Check - E2E Test ===\n")
    start = time.time()

    # 1. Aggregate analysis
    print("1. Running 6-dimension analysis...")
    result = await aggregate(REPO_ROOT, REPO_URL)
    health_score = result["health_score"]
    badge = result["badge_level"]
    dims = result["dimensions"]

    print(f"   Health Score: {health_score}/100 ({badge})")
    for d in dims:
        filled = int(d["score"] // 10)
        bar = "=" * filled + "-" * (10 - filled)
        print(f"   [{d['dimension']:25s}] [{bar}] {d['score']}/100")

    assert 0 <= health_score <= 100, "Health score out of range"
    assert len(dims) == 6, f"Expected 6 dimensions, got {len(dims)}"
    assert badge in ("A", "B", "C", "D"), f"Invalid badge: {badge}"

    # 2. AI diagnosis
    print("\n2. Running AI diagnosis...")
    diagnosis = await ai_diagnose(dims, REPO_URL)
    print(f"   Generated {len(diagnosis)} suggestions:")
    for s in diagnosis:
        sev = s["severity"].upper()
        print(f"   [{sev:6s}] {s['advice'][:80]}... (confidence: {s['confidence']}%)")

    assert len(diagnosis) >= 1, "No diagnosis generated"

    # 3. Verify result format
    print("\n3. Verifying output format...")
    required_keys = ["repo_url", "health_score", "badge_level", "badge_color", "dimensions", "ai_diagnosis", "analyzed_at"]
    for k in required_keys:
        assert k in result, f"Missing key: {k}"
    print("   Format check: PASSED")

    elapsed = time.time() - start
    print(f"\n[OK] All checks passed in {elapsed:.1f}s")
    print(f"   Health: {health_score}/100 ({badge})")
    print(f"   Diagnosis: {len(diagnosis)} suggestions")

    # 4. Write report
    report_path = REPO_ROOT / "e2e_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n   Report saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
