from conftest import SAMPLE_PAYLOAD


def test_ingest_telemetry(client):
    resp = client.post(
        "/api/telemetry",
        json=SAMPLE_PAYLOAD,
        headers={"X-API-Key": "test-api-key"},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "ok"


def test_ingest_telemetry_bad_key(client):
    resp = client.post(
        "/api/telemetry",
        json=SAMPLE_PAYLOAD,
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401


def test_ingest_with_tokens(client):
    payload = {
        **SAMPLE_PAYLOAD,
        "token_usage": [
            {
                "project_path": "test-project",
                "session_id": "sess-1",
                "model": "claude-sonnet-4-6",
                "input_tokens": 1000,
                "output_tokens": 500,
                "cache_creation_tokens": 0,
                "cache_read_tokens": 200,
            }
        ],
    }
    resp = client.post(
        "/api/telemetry",
        json=payload,
        headers={"X-API-Key": "test-api-key"},
    )
    assert resp.status_code == 201


def test_ingest_with_sessions(client):
    payload = {
        **SAMPLE_PAYLOAD,
        "session_status": [
            {
                "project_path": "test-project",
                "session_id": "sess-1",
                "status": "running",
                "model": "claude-opus-4-6",
                "last_activity": "2026-04-08T10:00:00Z",
                "slug": "test-slug",
            }
        ],
    }
    resp = client.post(
        "/api/telemetry",
        json=payload,
        headers={"X-API-Key": "test-api-key"},
    )
    assert resp.status_code == 201


def test_duplicate_machine(client):
    """Sending from same machine twice should update, not duplicate."""
    headers = {"X-API-Key": "test-api-key"}
    client.post("/api/telemetry", json=SAMPLE_PAYLOAD, headers=headers)
    client.post("/api/telemetry", json=SAMPLE_PAYLOAD, headers=headers)

    resp = client.get("/api/machines")
    machines = resp.json()
    assert len(machines) == 1
    assert machines[0]["machine_name"] == "test-machine"
