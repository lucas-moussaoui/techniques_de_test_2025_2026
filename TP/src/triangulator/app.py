import uuid
from flask import Flask, jsonify
from .triangulator import Triangulator

app = Flask(__name__)

def is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False

# Création de la route http pour la triangulation
@app.route("/triangulate/<pointset_id>", methods=["GET"])
def triangulate_endpoint(pointset_id):
    """
    Endpoint principal de triangulation
    """
    # Vérification simple, pointset_id doit être un UUID valide
    if not is_valid_uuid(pointset_id):
        return jsonify({"error": "Invalid ID"}), 400

    t = Triangulator()
    try:
        result = t.triangulate_from_id(pointset_id)
        return jsonify({"triangles": result}), 200

    except FileNotFoundError:
        return jsonify({"error": "PointSet not found"}), 404

    except ValueError as e:
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 503
