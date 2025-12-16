"""Module de triangulation."""
import math
import struct
import urllib.error
import urllib.request


class Triangulator:
    """Classe responsable de la triangulation d'un ensemble de points."""

    def encode_pointset(self, points) -> bytes:
        """Encode un PointSet au format binaire."""
        N = len(points)

        # I signifie unsigned long (4 octets)
        # f signifie float (4 octets)
        # < signifie little-endian (le moins significatif est stocké en premier)
        # > signifie big-endian (le plus significatif est stocké en premier)
        
        # Le but ici est d'écrire le header 
        # ( qui est censer représenter le nombre de points)
        # struct.pack('<I', N) va créer 4 octets représentant cet espace et y ajouter N
        binary_pointSet = struct.pack('<I', N)
        
        # Ici on boucle pour écrire les points dans binary_pointSet
        for point in points:
            # On s'assure que ce sont des floats (x, y)
            x, y = point
            # struct.pack('<ff', float(x), float(y)) 
            # va créer 8 octets représentant cet espace et y ajouter x et y
            binary_pointSet += struct.pack('<ff', float(x), float(y))
            
        return binary_pointSet

    def fetch_pointset(self, pointset_id: str) -> bytes:
        """Récupère le PointSet binaire depuis le PointSetManager."""
        # 1. On construit l'URL (ex: /pointset/123-abc...)
        url = f"http://localhost:8080/pointset/{pointset_id}"
        
        try:
            # 2. On ouvre la connexion
            with urllib.request.urlopen(url) as response:
                # 3. Si ça marche (code 200), on lit tout le contenu binaire
                return response.read() # Ceci retourne des 'bytes'

        except urllib.error.HTTPError as e:
            # Le serveur a répondu, mais avec une erreur (404, 500...)
            if e.code == 404:
                raise FileNotFoundError(f"PointSet {pointset_id} introuvable") from e
            elif e.code == 503:
                raise ConnectionError("PointSetManager en maintenance") from e
            else:
                raise ValueError(f"Erreur HTTP {e.code}: {e.reason}") from e
                
        except urllib.error.URLError as e:
            # Le serveur n'est même pas accessible (éteint, pas de wifi...)
            # Ton app.py attrapera cette exception générique et renverra une 503.
            raise ConnectionError(f"Impossible de joindre le PSM: {e.reason}") from e

    def decode_pointset(self, binary: bytes):
        """Décode le PointSet au format binaire → liste de points."""
        # Vérification minimale de la taille (4 bytes pour N)
        if len(binary) < 4:
            raise ValueError("Données binaires invalides ou incomplètes")

        # Ici on va lire N
        try:
            N = struct.unpack('<I', binary[:4])[0]
        except struct.error as e:
            raise ValueError("Impossible de lire le nombre de points") from e

        # Vérification de la cohérence de la taille totale
        # 4 bytes (header) + N * 8 bytes (corps : 2 floats de 4 bytes par point)
        expected_size = 4 + (N * 8)
        if len(binary) < expected_size:
            raise ValueError(
                f"Taille incorrecte : attendu {expected_size}, reçu {len(binary)}"
            )

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

    def is_in_circumcircle(self, point, triangle, points):
        """Vérifie si un point est dans le cercle circonscrit d'un triangle."""
        # 1. On récupère les 3 sommets du triangle
        a = points[triangle[0]]
        b = points[triangle[1]]
        c = points[triangle[2]]

        # 2. On simplifie en ramenant 'p' à l'origine (0,0)
        ax, ay = a[0] - point[0], a[1] - point[1]
        bx, by = b[0] - point[0], b[1] - point[1]
        cx, cy = c[0] - point[0], c[1] - point[1]

        # 3. On calcule le déterminant
        det = ( (ax*ax + ay*ay) * (bx*cy - cx*by) -
                (bx*bx + by*by) * (ax*cy - cx*ay) +
                (cx*cx + cy*cy) * (ax*by - bx*ay) )
                
        # 4. On retourne True si le déterminant est positif
        return det > 0

    def triangulate(self, points):
        """Triangulation d'un nuage de points en triangles (Bowyer-Watson)."""
        # ETAPE 1 : VERIFICATIONS DE BASE
        
        # Si la liste est vide, on ne peut rien faire
        if not points:
            return []
        
        # On récupère le nombre de points
        n_points = len(points)
        
        # Il faut au moins 3 points pour faire un triangle
        if n_points < 3:
            raise ValueError("Impossible de trianguler moins de 3 points")

        # ETAPE 2 : ANALYSE DES DONNEES (BOUNDING BOX)

        # On extrait toutes les coordonnées X et Y pour trouver les limites
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        min_x, max_x = min(x), max(x)
        min_y, max_y = min(y), max(y)

        # Vérification de la colinéarité
        if math.isclose(min_x, max_x) or math.isclose(min_y, max_y):
             raise ValueError("Points colinéaires ou confondus")

        # ETAPE 3 : CREATION DU SUPER-TRIANGLE

        # On calcule les dimensions de la zone
        dx = max_x - min_x
        dy = max_y - min_y
        # On prend la plus grande dimension pour faire un triangle assez grand
        delta_max = max(dx, dy) if max(dx, dy) > 0 else 1.0
        
        # On calcule le centre du nuage de points
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        # On crée 3 points virtuels géants qui englobent tout le nuage
        # La multiplication par 20 permet d'être sur qu'il englobe tout le nuage
        p1 = (mid_x - 20 * delta_max, mid_y - delta_max)
        p2 = (mid_x, mid_y + 20 * delta_max)
        p3 = (mid_x + 20 * delta_max, mid_y - delta_max)

        # On crée une liste de travail qui contient
        # les vrais points + les 3 points virtuels
        working_points = points + [p1, p2, p3]
        
        # Les indices des points du Super-Triangle sont à la fin de la liste
        st1 = n_points
        st2 = n_points + 1
        st3 = n_points + 2

        # On initialise la liste des triangles avec ce Super-Triangle unique
        triangles = [(st1, st3, st2)]

        # ETAPE 4 : LA BOUCLE PRINCIPALE (INCREMENTALE)

        # On insère chaque point un par un dans la triangulation existante
        for i, point in enumerate(points):
            
            # Liste des triangles qui ne respectent
            # plus la condition de Delaunay (à supprimer)
            bad_triangles = []
            
            # Liste temporaire pour garder les bons triangles
            temp_triangles = []

            # Identification des mauvais triangles
            for tri in triangles:
                # Si le nouveau point est dans le cercle circonscrit de ce triangle
                if self.is_in_circumcircle(point, tri, working_points):
                    # alors ce triangle est a enlever
                    bad_triangles.append(tri)
                else:
                    # sinon, on le garde pour la prochaine étape
                    temp_triangles.append(tri)
            
            # On met à jour la liste principale en ne gardant que les bons
            triangles = temp_triangles

            # Calcul du Polygone de Bowyer-Watson ( un gros trou )
            # Le but est de trouver le contour extérieur du trou
            # formé par les bad_triangles.
            # On doit trouver une arête interne est partagée par 2 bad_triangles.
            # Une arête frontière n'appartient qu'à 1 seul bad_triangle.
            boundary_edges = set()
            
            for tri in bad_triangles:
                # On liste les 3 arêtes du triangle : (A,B), (B,C), (C,A)
                edges = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])]
                
                for edge in edges:
                    # On calcule l'arête inverse (B,A)
                    reversed_edge = (edge[1], edge[0])
                    
                    # Si l'inverse est déjà dans le set, c'est que l'arête est partagée
                    if reversed_edge in boundary_edges:
                        # Donc c'est une arête interne, on la supprime
                        # (elles s'annulent)
                        boundary_edges.remove(reversed_edge)
                    else:
                        # Sinon, c'est potentiellement une frontière, on l'ajoute
                        boundary_edges.add(edge)

            # Re-bouchage du trou
            # Pour chaque arête du contour,
            # on crée un nouveau triangle avec le point 'i'
            for edge in boundary_edges:
                # On forme le triangle (Point1, Point2, NouveauPoint)
                new_tri = (edge[0], edge[1], i)
                # On l'ajoute à la liste principale
                triangles.append(new_tri)

        # Nettoyage final
        
        final_triangles = []
        
        # On parcourt tous les triangles créés
        for tri in triangles:
            # Si indice sommets >= n_points, c'est un sommet du Super-Triangle
            if tri[0] >= n_points or tri[1] >= n_points or tri[2] >= n_points:
                # On ne garde pas ce triangle car il est connecté à rien
                continue
            
            # Sinon, c'est un triangle valide
            final_triangles.append(tri)

        # sécurité finale
        
        # cas d'une ligne droite
        if not final_triangles and n_points >= 3:
             raise ValueError("Erreur triangulation (potentiellement colinéaires)")

        # On retourne la liste finale
        return final_triangles

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
