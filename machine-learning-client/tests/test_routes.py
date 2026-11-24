"""Test routes"""


def test_health(client):
    """health route answers ok"""
    reply = client.get("/health")
    assert reply.status_code == 200
    assert reply.get_json() == {"status": "ok"}
