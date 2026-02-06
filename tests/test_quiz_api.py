import requests

BASE_URL = "http://127.0.0.1:8799"

def test_quiz_random():
    r = requests.get(f"{BASE_URL}/api/quiz/random?unit_id=1")
    assert r.status_code == 200
    data = r.json()
    assert "question_id" in data
    assert "question" in data
    assert "choices" in data
    assert "context" in data
