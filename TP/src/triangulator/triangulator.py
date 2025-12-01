class Triangulator:
    """
    Classe responsable de la triangulation d'un ensemble de points.
    """
    def encode_pointset(self, points) -> bytes:
        """
        Encode un PointSet (liste de points) au format binaire.
        (Utilisé dans les tests)
        """
        raise NotImplementedError("Encodage non implémenté")

    def fetch_pointset(self, pointset_id: str) -> bytes:
        """
        Récupère le PointSet binaire depuis le PointSetManager.
        (Mocké dans les tests)
        """
        raise NotImplementedError("Fetching non implémenté")

    def decode_pointset(self, binary: bytes):
        """
        Décode le PointSet au format binaire → liste de points.
        """
        raise NotImplementedError("Décodage non implémenté")

    def triangulate(self, points):
        """
        Retourne une liste de triangles formés à partir d'une liste de points.
        """
        raise NotImplementedError("Triangulation non implémentée")

    def encode_triangles(self, points, triangles) -> bytes:
        """
        Encode la réponse Triangles au format binaire.
        """
        raise NotImplementedError("Encodage non implémenté")

    def decode_triangles(self, triangles):
        """
        Décode la réponse Triangles depuis le format binaire.
        (Utilisé dans les tests)
        """
        raise NotImplementedError("Décodage non implémenté")

    def triangulate_from_id(self, pointset_id: str):
        """
        Récupère un PointSet → le triangule → renvoie la structure resultante.
        (Pour les tests API)
        """
        binary = self.fetch_pointset(pointset_id)
        points = self.decode_pointset(binary)
        triangles = self.triangulate(points)
        return self.encode_triangles(points, triangles)
