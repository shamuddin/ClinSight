"""
API-level tests for demo endpoints.
Covers: GET /demo/cases, GET /demo/analyze/{case_id},
        POST /demo/analyze/{case_id}/override,
        GET /demo/analyze/{case_id}/stream (SSE).
Uses ASGI transport so no real server is needed.
"""
import json
import pytest
from httpx import AsyncClient, ASGITransport

from backend.api.main import app

FIRST_CASE = "CS-2024-001"
ALL_CASE_IDS = [
    "CS-2024-001", "CS-2024-002", "CS-2024-003",
    "CS-2024-004", "CS-2024-005", "CS-2024-006",
]

# ─── /demo/cases ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_cases_returns_all_six():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/demo/cases")
    assert resp.status_code == 200
    cases = resp.json()
    assert len(cases) == 6
    returned_ids = {c["case_id"] for c in cases}
    assert returned_ids == set(ALL_CASE_IDS)


@pytest.mark.asyncio
async def test_list_cases_shape():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/demo/cases")
    assert resp.status_code == 200
    for c in resp.json():
        assert "case_id" in c
        assert "patient_age" in c
        assert "patient_sex" in c
        assert "chief_complaint" in c
        assert "triage_note" in c
        assert "vitals" in c


# ─── /demo/analyze/{case_id} ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analyze_returns_safety_subcounts():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(f"/demo/analyze/{FIRST_CASE}")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["contradictions_count"], int)
    assert isinstance(data["hallucination_count"], int)
    assert isinstance(data["bias_count"], int)
    assert data["contradictions_count"] >= 0
    assert data["hallucination_count"] >= 0
    assert data["bias_count"] >= 0


@pytest.mark.asyncio
async def test_analyze_required_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(f"/demo/analyze/{FIRST_CASE}")
    assert resp.status_code == 200
    data = resp.json()
    required = [
        "case_id", "esi_level", "esi_description", "findings", "lab_alerts",
        "differential", "suggested_actions", "safety_flags", "report",
        "audit_log", "quality_gate", "pediatric_gate", "lab_patterns",
        "attention_regions", "vitals", "triage_note", "patient_age",
        "patient_sex", "patient_race", "chief_complaint", "lab_values",
        "lab_units", "total_time_ms", "contradictions_count",
        "hallucination_count", "bias_count",
    ]
    for field in required:
        assert field in data, f"Missing field in response: {field}"


@pytest.mark.asyncio
async def test_analyze_esi_valid_range():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(f"/demo/analyze/{FIRST_CASE}")
    assert resp.status_code == 200
    assert resp.json()["esi_level"] in (1, 2, 3, 4, 5)


@pytest.mark.asyncio
async def test_analyze_404_for_unknown_case():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/demo/analyze/UNKNOWN-CASE-999")
    assert resp.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("case_id", ALL_CASE_IDS)
async def test_all_cases_produce_valid_esi(case_id: str):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get(f"/demo/analyze/{case_id}")
    assert resp.status_code == 200
    assert resp.json()["esi_level"] in (1, 2, 3, 4, 5)


# ─── /demo/analyze/{case_id}/override ────────────────────────────────────────

@pytest.mark.asyncio
async def test_override_applies_lab_changes():
    payload = {
        "lab_overrides": {"troponin_i": 99.9},
        "vitals_overrides": {},
        "scenario_name": "high_troponin",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(f"/demo/analyze/{FIRST_CASE}/override", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_name"] == "high_troponin"
    assert data["base_case_id"] == FIRST_CASE
    assert data["applied_overrides"]["lab_overrides"]["troponin_i"] == 99.9
    assert data["lab_values"]["troponin_i"] == 99.9


@pytest.mark.asyncio
async def test_override_applies_vitals_changes():
    payload = {
        "lab_overrides": {},
        "vitals_overrides": {"hr": 145, "spo2": 82},
        "scenario_name": "tachycardia_hypoxia",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(f"/demo/analyze/{FIRST_CASE}/override", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["vitals"]["hr"] == 145
    assert data["vitals"]["spo2"] == 82


@pytest.mark.asyncio
async def test_override_returns_safety_subcounts():
    payload = {"lab_overrides": {}, "vitals_overrides": {}, "scenario_name": "baseline"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(f"/demo/analyze/{FIRST_CASE}/override", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "contradictions_count" in data
    assert "hallucination_count" in data
    assert "bias_count" in data


@pytest.mark.asyncio
async def test_override_default_scenario_name():
    """Omitting scenario_name should default to 'custom'."""
    payload = {"lab_overrides": {"wbc": 25.0}, "vitals_overrides": {}}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(f"/demo/analyze/{FIRST_CASE}/override", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario_name"] == "custom"
    assert f"{FIRST_CASE}::custom" in data["case_id"]


@pytest.mark.asyncio
async def test_override_404_for_unknown_case():
    payload = {"lab_overrides": {}, "vitals_overrides": {}}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/demo/analyze/UNKNOWN-CASE-999/override", json=payload)
    assert resp.status_code == 404


# ─── /demo/analyze/{case_id}/stream (SSE) ────────────────────────────────────

@pytest.mark.asyncio
async def test_stream_content_type_is_sse():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        async with ac.stream("GET", f"/demo/analyze/{FIRST_CASE}/stream") as resp:
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers["content-type"]
            # Consume enough to confirm it's streaming
            async for line in resp.aiter_lines():
                if line.startswith("data:"):
                    break


@pytest.mark.asyncio
async def test_stream_emits_pipeline_nodes_and_done():
    """Every pipeline stage plus __done__ must appear in the SSE stream."""
    events: list[dict] = []
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        async with ac.stream("GET", f"/demo/analyze/{FIRST_CASE}/stream") as resp:
            assert resp.status_code == 200
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = json.loads(line[6:])
                events.append(payload)
                if payload.get("agent") == "__done__":
                    break

    agent_names = {e["agent"] for e in events}
    # All LangGraph nodes must have fired
    assert "__done__" in agent_names
    expected_nodes = {"coordinator", "analysis", "safety", "documenter"}
    assert expected_nodes.issubset(agent_names), (
        f"Missing nodes in SSE stream: {expected_nodes - agent_names}"
    )


@pytest.mark.asyncio
async def test_stream_done_event_has_result_shape():
    """The __done__ event must carry a full result with safety subcounts."""
    done_event: dict = {}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        async with ac.stream("GET", f"/demo/analyze/{FIRST_CASE}/stream") as resp:
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = json.loads(line[6:])
                if payload.get("agent") == "__done__":
                    done_event = payload
                    break

    assert done_event, "Stream closed without __done__ event"
    result = done_event["result"]
    assert result["esi_level"] in (1, 2, 3, 4, 5)
    assert "contradictions_count" in result
    assert "hallucination_count" in result
    assert "bias_count" in result
    assert "differential" in result
    assert "suggested_actions" in result


@pytest.mark.asyncio
async def test_stream_node_payloads_have_timestamps():
    """Each SSE event must include agent, timestamp, elapsed_ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        async with ac.stream("GET", f"/demo/analyze/{FIRST_CASE}/stream") as resp:
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = json.loads(line[6:])
                if payload.get("agent") == "__done__":
                    break
                assert "agent" in payload
                assert "timestamp" in payload
                assert "elapsed_ms" in payload


@pytest.mark.asyncio
async def test_stream_404_for_unknown_case():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/demo/analyze/UNKNOWN-CASE-999/stream")
    assert resp.status_code == 404
