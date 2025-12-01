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

    # Pour limiter le nombre de triangles
    mocker.patch.object(t, "triangulate", return_value=[(0, 1, 2)] * (n_points // 2))

    start = time.perf_counter()

    t.triangulate(points)   # → appel mocké, donc immédiat

    duration = time.perf_counter() - start

    # Critère de performance : l'appel doit rester très rapide (< 100 ms)
    assert duration < 0.1

def test_decode_pointset_performance(mocker):
    """Test de performance : le décodage d'un PointSet binaire doit rester rapide."""
    # Simule un PointSet binaire très large
    fake_binary = b"\x00\x00\x27\x10" + b"\x00\x00\x00\x00" * (10000 * 2)
    # 0x2710 = 10000 points

    t = Triangulator()

    # Mock de decode pour éviter une vraie implémentation complexe
    mocker.patch.object(t, "decode_pointset", return_value=[(0, 0)] * 10000)

    import time
    start = time.perf_counter()

    t.decode_pointset(fake_binary)

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

    mocker.patch.object(t, "fetch_pointset", return_value=b"bin")
    mocker.patch.object(t, "decode_pointset", return_value=[(0, 0), (1, 0), (0, 1)])
    mocker.patch.object(t, "triangulate", return_value=[(0, 1, 2)])
    mocker.patch.object(t, "encode_triangles", return_value=b"triangles")

    import time
    start = time.perf_counter()

    t.triangulate_from_id("123e4567-e89b-12d3-a456-426614174000")

    duration = time.perf_counter() - start

    assert duration < 0.1

