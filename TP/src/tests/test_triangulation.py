import pytest
from src.triangulator.triangulator import Triangulator

def test_trois_points_creer_un_triangle():
    """
        Cas basique : 3 points non colinéaires -> 1 triangle
    """
    points = [(0, 0), (1, 0), (0, 1)]
    t = Triangulator()
    triangles = t.triangulate(points)
    assert len(triangles) == 1
    assert triangles[0] == (0, 1, 2)

def test_quatre_points_convexes_creer_deux_triangle():
    """
        Cas : 4 points convexes -> 2 triangles
    """
    points = [(0, 0), (1, 0), (1, 1), (0, 1)]
    t = Triangulator()
    triangles = t.triangulate(points)
    assert len(triangles) == 2

def test_erreur_points_uniquement_colineaire():
    """
        Cas : points colinéaires -> erreur
    """
    points = [(0, 0), (1, 1), (2, 2)]
    t = Triangulator()
    with pytest.raises(ValueError):
        t.triangulate(points)

def test_erreur_deux_points():
    """
        Cas : 2 points -> erreur
    """
    points = [(0, 0), (1, 0)]
    t = Triangulator()
    with pytest.raises(ValueError):
        t.triangulate(points)

def test_plusieurs_points_creer_plusieurs_triangles():
    """
        Cas : plusieurs points non colinéaires -> plusieurs triangles
    """
    points = [(0, 0), (1, 0), (2, 0), (1, 1)]
    t = Triangulator()
    triangles = t.triangulate(points)
    assert len(triangles) >= 1
