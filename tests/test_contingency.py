"""
Contingency mode tests — fallback when vLLM is unavailable.
"""
import pytest
from backend.inference.contingency import ContingencyFallback
from backend.core.config import settings


def test_contingency_returns_safe_output():
    cf = ContingencyFallback()
    result = cf.load_case("nonexistent_case")
    assert result["esi_level"] == 3
    assert result["flag"] == "CONTINGENCY_MODE_ACTIVE"
    assert "manual assessment required" in result["suggested_actions"][0]


def test_contingency_warm_and_load(tmp_path):
    cf = ContingencyFallback(cache_dir=tmp_path)
    test_data = {
        "esi_level": 1,
        "esi_description": "Immediate",
        "findings": [{"finding": "pneumonia"}],
        "differential": ["Pneumonia"],
        "suggested_actions": ["Antibiotics"],
    }
    cf.warm("demo_001", test_data)
    assert cf.is_available("demo_001")

    loaded = cf.load_case("demo_001")
    assert loaded["esi_level"] == 1


def test_missing_cache_dir_graceful():
    """Missing cache directory should not crash."""
    cf = ContingencyFallback(cache_dir=settings.base_dir / "nonexistent_dir")
    result = cf.load_case("test")
    assert result["esi_level"] == 3
    assert result["flag"] == "CONTINGENCY_MODE_ACTIVE"
