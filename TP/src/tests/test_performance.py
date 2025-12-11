"""Tests de performance pour le module de triangulation."""

import time

import pytest
from src.triangulator.triangulator import Triangulator


@pytest.mark.parametrize("n_points", [100, 1000, 10000])
def test_triangulation_perf_various_sizes(mocker, n_points):
    """vérifie la rapidité pour différentes tailles de PointSet."""
    # Génère un nuage de n_points ( a peu pres aléatoire grace au %)
    points = [(i, i % 50) for i in range(n_points)]

    t = Triangulator()

    start = time.perf_counter()

    t.triangulate(points)

    duration = time.perf_counter() - start

    # Critère de performance : l'appel doit rester très rapide (< 100 ms)
    assert duration < 0.1

def test_decode_pointset_performance(mocker):
    """Test de performance : le décodage d'un PointSet binaire doit rester rapide."""
    t = Triangulator()

    n_points = 10000
    # Header : N (unsigned long)
    binary_data = struct.pack('<I', n_points)
    # Body : N points (float, float)
    # On génère un gros bloc de bytes directement
    point_data = struct.pack('<ff', 1.0, 2.0) * n_points
    full_data = binary_data + point_data

    start = time.perf_counter()

    t.decode_pointset(full_data)

    duration = time.perf_counter() - start

    assert duration < 0.1

def test_encode_triangles_performance(mocker):
    """Test de performance : l'encodage des triangles doit être rapide."""
    points = [(0, 0)] * 5000
    triangles = [(0, 1, 2)] * 4000

    t = Triangulator()

    mocker.patch.object(t, "encode_triangles", return_value=b"ok")

    import time
    start = time.perf_counter()

    t.encode_triangles(points, triangles)

    duration = time.perf_counter() - start

    assert duration < 0.1

def test_full_pipeline_performance(mocker):
    """Test de performance : l'appel complet triangulate_from_id doit être rapide."""
    t = Triangulator()

    n_points = 1000
    fake_input_binary = struct.pack('<I', n_points) + (struct.pack('<ff', 0.0, 0.0) * n_points)
    
    mocker.patch.object(t, "fetch_pointset", return_value=fake_input_binary)

    start = time.perf_counter()

    t.triangulate_from_id("123e4567-e89b-12d3-a456-426614174000")

    duration = time.perf_counter() - start

    assert duration < 0.1

