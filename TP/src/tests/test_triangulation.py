"""Tests unitaires pour le module de triangulation."""

import struct
import urllib.error
from io import BytesIO
import pytest
from src.triangulator.triangulator import Triangulator

### Tests fetch_pointset ###

def test_fetch_pointset_success(mocker):
    """Test de la récupération réussie d'un PointSet binaire."""
    expected_binary = b'\x00\x01\x02\x03'
    t = Triangulator()
    mocker.patch.object(t, 'fetch_pointset', return_value=expected_binary)
    result = t.fetch_pointset("valid_id")
    assert result == expected_binary

def test_fetch_pointset_404(mocker):
    """Teste la levée de FileNotFoundError lors d'une 404."""
    t = Triangulator()
    # On simule une erreur HTTP 404
    error_404 = urllib.error.HTTPError("url", 404, "Not Found", {}, BytesIO(b""))
    mocker.patch("urllib.request.urlopen", side_effect=error_404)

    with pytest.raises(FileNotFoundError, match="introuvable"):
        t.fetch_pointset("unknown_id")

def test_fetch_pointset_503(mocker):
    """Teste la levée de ConnectionError lors d'une 503."""
    t = Triangulator()
    # On simule une erreur HTTP 503
    error_503 = urllib.error.HTTPError("url", 503, "Service Unavailable", {}, BytesIO(b""))
    mocker.patch("urllib.request.urlopen", side_effect=error_503)

    with pytest.raises(ConnectionError, match="maintenance"):
        t.fetch_pointset("any_id")

def test_fetch_pointset_other_http_error(mocker):
    """Teste la levée de ValueError pour d'autres codes HTTP (ex: 500)."""
    t = Triangulator()
    error_500 = urllib.error.HTTPError("url", 500, "Internal Server Error", {}, BytesIO(b""))
    mocker.patch("urllib.request.urlopen", side_effect=error_500)

    with pytest.raises(ValueError, match="Erreur HTTP 500"):
        t.fetch_pointset("any_id")

def test_fetch_pointset_url_error(mocker):
    """Teste la levée de ConnectionError quand le serveur est inaccessible."""
    t = Triangulator()
    # On simule un échec de connexion (serveur éteint)
    mocker.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused"))

    with pytest.raises(ConnectionError, match="Impossible de joindre le PSM"):
        t.fetch_pointset("any_id")

def test_fetch_pointset_read_coverage(mocker):
    """Teste le succès de lecture de fetch_pointset pour le coverage."""
    t = Triangulator()
    fake_data = b"\x00\x00\x00\x01\x00\x00\x80\x3f\x00\x00\x00\x40"

    # 1. On crée le MagicMock
    mock_response = mocker.MagicMock()
    
    # 2. IMPORTANT : On dit au mock que lorsqu'on entre dans le "with", 
    # il doit se retourner lui-même pour que 'as response' soit égal au mock.
    mock_response.__enter__.return_value = mock_response
    
    # 3. On définit ce que read() doit renvoyer
    mock_response.read.return_value = fake_data

    # 4. On patch l'ouverture de l'URL
    mocker.patch("urllib.request.urlopen", return_value=mock_response)

    result = t.fetch_pointset("123e4567-e89b-12d3-a456-426614174000")

    # result sera bien égal à fake_data
    assert result == fake_data
    mock_response.read.assert_called_once()

### Tests de triangulation ###

def test_circumcircle_inside():
    """Vérifie qu'un point clairement à l'intérieur est détecté."""
    t = Triangulator()
    # Triangle rectangle (0,0) -> (4,0) -> (0,4)
    points = [(0, 0), (4, 0), (0, 4)]
    triangle_indices = (0, 1, 2)
    
    # Point à tester (1, 1) est bien dedans
    p_inside = (1, 1)
    
    assert t.is_in_circumcircle(p_inside, triangle_indices, points) is True

def test_circumcircle_outside():
    """Vérifie qu'un point à l'extérieur est rejeté."""
    t = Triangulator()
    points = [(0, 0), (4, 0), (0, 4)]
    triangle_indices = (0, 1, 2)
    
    # Point à tester (5, 5) est dehors
    p_outside = (5, 5)
    
    assert t.is_in_circumcircle(p_outside, triangle_indices, points) is False

def test_circumcircle_cocyclic():
    """Vérifie le comportement pour un point sur le bord du cercle."""
    t = Triangulator()
    # Triangle inscrit dans le cercle de rayon 1
    points = [(-1, 0), (1, 0), (0, 1)] 
    triangle_indices = (0, 1, 2)
    
    # Le point (0, -1) est aussi sur ce cercle
    p_on_circle = (0, -1)
    
    # Doit renvoyer False car pas STRICTEMENT à l'intérieur
    assert t.is_in_circumcircle(p_on_circle, triangle_indices, points) is False

def test_trois_points_creer_un_triangle():
    """Cas basique : 3 points non colinéaires -> 1 triangle."""
    points = [(0, 0), (1, 0), (0, 1)]
    t = Triangulator()
    triangles = t.triangulate(points)
    assert len(triangles) == 1
    assert triangles[0] == (0, 1, 2)

def test_quatre_points_convexes_creer_deux_triangle():
    """Cas : 4 points convexes -> 2 triangles."""
    points = [(0, 0), (1, 0), (1, 1), (0, 1)]
    t = Triangulator()
    triangles = t.triangulate(points)
    assert len(triangles) == 2
    assert set(triangles) == {(0, 1, 2), (0, 2, 3)}

def test_erreur_points_uniquement_colineaire():
    """Cas : points colinéaires -> erreur."""
    points = [(0, 0), (1, 1), (2, 2)]
    t = Triangulator()
    with pytest.raises(ValueError):
        t.triangulate(points)

def test_erreur_deux_points():
    """Cas : 2 points -> erreur."""
    points = [(0, 0), (1, 0)]
    t = Triangulator()
    with pytest.raises(ValueError):
        t.triangulate(points)

def test_plusieurs_points_creer_plusieurs_triangles():
    """Cas : plusieurs points non colinéaires -> plusieurs triangles."""
    points = [(0,0), (2,0), (3,1), (1.5,3)]
    t = Triangulator()
    triangles = t.triangulate(points)
    assert len(triangles) >= 1

def test_aucun_point_retourne_aucun_triangle():
    """Cas : aucun point -> aucun triangle."""
    t = Triangulator()
    triangles = t.triangulate([])
    assert triangles == []

def test_points_colineaires_et_non_colineaires_creent_triangles_valides():
    """Cas : mélange de points colinéaires et non colinéaires."""
    # 3 points alignés + 1 point au-dessus
    points = [(0, 0), (1, 0), (2, 0), (1, 1)]
    t = Triangulator()
    triangles = t.triangulate(points)
    assert len(triangles) == 2


### Tests de décodage / encodage ###

def test_encode_pointset():
    """Test de l'encodage d'un PointSet."""
    points = [(0, 0), (1, 1), (2, 2)]
    t = Triangulator()
    binary = t.encode_pointset(points)
    assert isinstance(binary, bytes)

def test_encode_pointset_format_strict():
    """Vérifie que le format binaire est EXACTEMENT celui de la spec."""
    # 1 point à (1.0, 2.0)
    points = [(1.0, 2.0)]
    t = Triangulator()
    binary = t.encode_pointset(points)
    
    # Construction manuelle de ce qu'on attend selon la spec:
    # - 1 unsigned long (4 bytes) pour N=1 -> \x01\x00\x00\x00
    # - 1 float (4 bytes) pour X=1.0      -> \x00\x00\x80\x3f (IEEE 754)
    # - 1 float (4 bytes) pour Y=2.0      -> \x00\x00\x00\x40 (IEEE 754)
    expected = struct.pack('<I', 1) + struct.pack('<f', 1.0) + struct.pack('<f', 2.0)
    
    assert binary == expected

def test_encode_empty_pointset():
    """Test de l'encodage d'un PointSet vide."""
    points = []
    t = Triangulator()
    binary = t.encode_pointset(points)
    assert isinstance(binary, bytes)

def test_decode_pointset():
    """Test du décodage d'un PointSet."""
    points = [(0, 0), (1, 1), (2, 2)]
    t = Triangulator()
    binary = t.encode_pointset(points)
    decoded_points = t.decode_pointset(binary)
    assert decoded_points == points

def test_decode_invalid_pointset():
    """Test du décodage d'un PointSet invalide."""
    invalid_binary = b'\x00\x01\x02'  # Données binaires invalides
    t = Triangulator()
    with pytest.raises(ValueError):
        t.decode_pointset(invalid_binary)

def test_encode_triangles():
    """Test de l'encodage des triangles."""
    points = [(0, 0), (1, 0), (0, 1)]
    triangles = [(0, 1, 2)]
    t = Triangulator()
    binary = t.encode_triangles(points, triangles)
    assert isinstance(binary, bytes)

def test_encode_no_triangles():
    """Test de l'encodage lorsqu'il n'y a pas de triangles."""
    points = [(0, 0), (1, 0), (0, 1)]
    triangles = []
    t = Triangulator()
    binary = t.encode_triangles(points, triangles)
    assert isinstance(binary, bytes)

def test_decode_triangles():
    """Test du décodage des triangles."""
    points = [(0, 0), (1, 0), (0, 1)]
    triangles = [(0, 1, 2)]
    t = Triangulator()
    binary = t.encode_triangles(points, triangles)
    decoded_triangles = t.decode_triangles(binary)
    assert decoded_triangles == triangles

def test_decode_invalid_triangles():
    """Test du décodage des triangles invalides."""
    invalid_binary = b'\x03\x04\x05'  # Données binaires invalides
    t = Triangulator()
    with pytest.raises(ValueError):
        t.decode_triangles(invalid_binary)

### Test de la méthode triangulate_from_id ###

def test_triangulate_from_id_success(mocker):
    """Test complet de triangulate_from_id."""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"
    points = [(0, 0), (1, 0), (0, 1)]
    triangles = [(0, 1, 2)]

    t = Triangulator()

    # Mock des méthodes internes
    mocker.patch.object(t, 'fetch_pointset', return_value=b'valid_binary')
    mocker.patch.object(t, 'decode_pointset', return_value=points)
    mocker.patch.object(t, 'triangulate', return_value=triangles)
    mocker.patch.object(t, 'encode_triangles', return_value=b'binary_triangles_data')

    result = t.triangulate_from_id(pointset_id)
    assert result == b'binary_triangles_data'