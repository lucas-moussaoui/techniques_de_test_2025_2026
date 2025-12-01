"""Tests pour l'API Flask de triangulation."""

import pytest
from src.triangulator.app import app


@pytest.fixture
def client():
    """Client de test Flask."""
    with app.test_client() as client:
        yield client

def test_valid_request_returns_200(client, mocker):
    """Cas 200 OK."""
    # Mock de la méthode triangulate_from_id
    # C'est a dire qu'on remplace ce que renvoi
    # la méthode triangulate_from_id par les valeur (0, 1, 2)
    mocker.patch("src.triangulator.triangulator.Triangulator.triangulate_from_id",
                 return_value=[(0, 1, 2)])
    valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/triangulate/{valid_uuid}")
    assert response.status_code == 200
    assert "triangles" in response.get_json()

def test_invalid_id_returns_400(client):
    """Cas 400 Bad Request."""
    response = client.get("/triangulate/invalid-uuid")
    assert response.status_code == 400

def test_pointset_not_found_returns_404(client, mocker):
    """Cas 404 Not Found."""
    mocker.patch("src.triangulator.triangulator.Triangulator.triangulate_from_id",
                 side_effect=FileNotFoundError)
    uuid_not_found = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    response = client.get(f"/triangulate/{uuid_not_found}")
    assert response.status_code == 404

def test_internal_error_returns_500(client, mocker):
    """Cas 500 Internal Server Error."""
    mocker.patch("src.triangulator.triangulator.Triangulator.triangulate_from_id",
                 side_effect=ValueError("Failed triangulation"))
    uuid_error = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    response = client.get(f"/triangulate/{uuid_error}")
    assert response.status_code == 500

def test_service_unavailable_returns_503(client, mocker):
    """Cas 503 Service Unavailable."""
    mocker.patch("src.triangulator.triangulator.Triangulator.triangulate_from_id",
                 side_effect=Exception("PSM down"))
    uuid_fail = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    response = client.get(f"/triangulate/{uuid_fail}")
    assert response.status_code == 503
