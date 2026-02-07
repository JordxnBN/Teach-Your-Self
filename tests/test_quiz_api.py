from fastapi.testclient import TestClient

from app.server import app

client = TestClient(app)


def test_quiz_random():
    r = client.get("/api/quiz/random?unit_id=1")
    assert r.status_code == 200
    data = r.json()
    assert "question_id" in data
    assert "question" in data
    assert "choices" in data
    assert "context" in data
