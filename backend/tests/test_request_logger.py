import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient

from middleware.request_logger import RequestLoggingMiddleware


def test_request_logging(caplog):
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"message": "ok"}

    client = TestClient(app)

    with caplog.at_level(logging.INFO):
        response = client.get("/test")

    assert response.status_code == 200

    logs = caplog.text
    assert "GET /test" in logs
    assert "200" in logs