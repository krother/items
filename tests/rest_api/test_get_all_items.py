import pytest
from fastapi.testclient import TestClient

from items.rest_api import app


@pytest.mark.num_items(3)
def test_items(items_db):
    client = TestClient(app)
    response = client.get("/items")
    assert response.status_code == 200
    j = response.json()
    assert len(j) == 3

