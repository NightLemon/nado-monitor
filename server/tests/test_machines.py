from conftest import SAMPLE_PAYLOAD


def _ingest(client, machine_name="test-machine"):
    payload = {**SAMPLE_PAYLOAD, "machine_name": machine_name}
    client.post(
        "/api/telemetry",
        json=payload,
        headers={"X-API-Key": "test-api-key"},
    )


def test_list_machines(client):
    _ingest(client, "machine-a")
    _ingest(client, "machine-b")

    resp = client.get("/api/machines")
    assert resp.status_code == 200
    machines = resp.json()
    assert len(machines) == 2
    names = {m["machine_name"] for m in machines}
    assert names == {"machine-a", "machine-b"}


def test_get_machine(client):
    _ingest(client)
    resp = client.get("/api/machines")
    machine_id = resp.json()[0]["id"]

    resp = client.get(f"/api/machines/{machine_id}")
    assert resp.status_code == 200
    assert resp.json()["machine_name"] == "test-machine"
    assert resp.json()["is_online"] is True
    assert resp.json()["latest_metrics"] is not None


def test_get_machine_not_found(client):
    resp = client.get("/api/machines/999")
    assert resp.status_code == 404


def test_machine_history(client):
    _ingest(client)
    resp = client.get("/api/machines")
    machine_id = resp.json()[0]["id"]

    resp = client.get(f"/api/machines/{machine_id}/history?hours=1")
    assert resp.status_code == 200
    assert resp.json()["machine_name"] == "test-machine"
    assert len(resp.json()["data_points"]) >= 1


def test_today_tokens(client):
    payload = {
        **SAMPLE_PAYLOAD,
        "token_usage": [
            {
                "project_path": "proj",
                "session_id": "s1",
                "model": "claude-sonnet-4-6",
                "input_tokens": 5000,
                "output_tokens": 2000,
                "cache_creation_tokens": 0,
                "cache_read_tokens": 100,
            }
        ],
    }
    client.post(
        "/api/telemetry",
        json=payload,
        headers={"X-API-Key": "test-api-key"},
    )

    resp = client.get("/api/machines")
    m = resp.json()[0]
    assert m["today_tokens"]["input"] == 5000
    assert m["today_tokens"]["output"] == 2000
