"""Module de triangulation."""
import struct

class Triangulator:
    """Classe responsable de la triangulation d'un ensemble de points."""

    def encode_pointset(self, points) -> bytes:
        """Encode un PointSet au format binaire."""
        N = len(points)

        # I signifie unsigned long (4 octets)
        # f signifie float (4 octets)
        # < signifie little-endian (le moins significatif est stocké en premier)
        # > signifie big-endian (le plus significatif est stocké en premier)
        
        # Le but ici est d'écrire le header ( qui est censer représenter le nombre de points)
        # struct.pack('<I', N) va créer 4 octets représentant cet espace et y ajouter N
        binary_pointSet = struct.pack('<I', N)
        
        # Ici on boucle pour écrire les points dans binary_pointSet
        for point in points:
            # On s'assure que ce sont des floats (x, y)
            x, y = point
            # struct.pack('<ff', float(x), float(y)) va créer 8 octets représentant cet espace et y ajouter x et y
            binary_pointSet += struct.pack('<ff', float(x), float(y))
            
        return binary_pointSet
    
    def fetch_pointset(self, pointset_id: str) -> bytes:
        """Récupère le PointSet binaire depuis le PointSetManager."""
        raise NotImplementedError("Fetching non implémenté")

    def decode_pointset(self, binary: bytes):
        """Décode le PointSet au format binaire → liste de points."""
        # Vérification minimale de la taille (4 bytes pour N)
        if len(binary) < 4:
            raise ValueError("Données binaires invalides ou incomplètes")

        # Ici on va lire N
        try:
            N = struct.unpack('<I', binary[:4])[0]
        except struct.error:
            raise ValueError("Impossible de lire le nombre de points")

        # Vérification de la cohérence de la taille totale
        # 4 bytes (header) + N * 8 bytes (corps : 2 floats de 4 bytes par point)
        expected_size = 4 + (N * 8)
        if len(binary) < expected_size:
            raise ValueError(f"Taille incorrecte : attendu {expected_size}, reçu {len(binary)}")

        points = []
        position = 4
        
        # Ici on va lire les points
        for _ in range(N):
            # on va prendre 8 octets
            chunk = binary[position : position + 8]
            x, y = struct.unpack('<ff', chunk)
            points.append((x, y))
            position += 8

        return points

    def triangulate(self, points):
        """Retourne une liste de triangles formés à partir d'une liste de points."""
        raise NotImplementedError("Triangulation non implémentée")

    def encode_triangles(self, points, triangles) -> bytes:
        """Encode la réponse Triangles au format binaire."""
        # On réutilise l'encodeur de points
        pointSet = self.encode_pointset(points)

        # On encode la partie triangles
        T = len(triangles)
        
        nombreDeTriangle = struct.pack('<I', T)
        
        trianglesEncodees = bytearray()
        for t in triangles:
            # Chaque triangle est un tuple (i1, i2, i3)
            # On encode 3 unsigned int ('<III') soit 12 octets
            trianglesEncodees += struct.pack('<III', t[0], t[1], t[2])

        # On colle tout ensemble
        return pointSet + nombreDeTriangle + trianglesEncodees

    def decode_triangles(self, binary: bytes):
        """Décode réponse Triangles depuis format binaire."""
        # On lit les points
        points = self.decode_pointset(binary)
        
        # On calcule où la partie Triangles commence
        # Taille partie 1 = 4 bytes (N) + N * 8 bytes
        N = len(points)
        position = 4 + (N * 8)
        
        # Vérification qu'on a bien la suite (au moins le nombre T)
        if len(binary) < position + 4:
             raise ValueError("Données binaires incomplètes pour les triangles")
             
        # Lecture du nombre de triangles T
        T = struct.unpack('<I', binary[position : position + 4])[0]
        position += 4
        
        triangles = []
        for _ in range(T):
            if len(binary) < position + 12:
                raise ValueError("Données corrompues dans les triangles")
                
            # Lecture du triplet d'indices (3 * 4 bytes)
            chunk = binary[position : position + 12]
            i1, i2, i3 = struct.unpack('<III', chunk)
            triangles.append((i1, i2, i3))
            position += 12
            
        return triangles
    
    def triangulate_from_id(self, pointset_id: str):
        """Récupère un PointSet → le triangule → renvoie la structure resultante."""
        binary = self.fetch_pointset(pointset_id)
        points = self.decode_pointset(binary)
        triangles = self.triangulate(points)
        return self.encode_triangles(points, triangles)
