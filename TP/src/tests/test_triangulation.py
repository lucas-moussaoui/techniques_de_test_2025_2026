"""Tests unitaires pour le module de triangulation."""

import struct
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

### Tests de triangulation ###

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