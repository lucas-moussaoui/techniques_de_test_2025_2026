"""Application Flask pour la triangulation de points."""

import uuid

from flask import Flask, jsonify, Response

from .triangulator import Triangulator

app = Flask(__name__)

def is_valid_uuid(value: str) -> bool:
    """Vérifie si une chaîne est un UUID valide."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False

# Création de la route http pour la triangulation
@app.route("/triangulation/<pointset_id>", methods=["GET"])
def triangulate_endpoint(pointset_id):
    """Endpoint principal de triangulation."""
    # Vérification simple, pointset_id doit être un UUID valide
    if not is_valid_uuid(pointset_id):
        return jsonify({
            "code": "BAD_REQUEST", 
            "message": "Invalid ID format"
        }), 400

    t = Triangulator()
    try:
        result = t.triangulate_from_id(pointset_id)
        return Response(
            result,
            status=200,
            mimetype='application/octet-stream'
        )

    except FileNotFoundError:
        return jsonify({
            "code": "NOT_FOUND",
            "message": "PointSet not found"
        }), 404

    except ValueError as e:
        return jsonify({
            "code": "TRIANGULATION_FAILED",
            "message": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "code": "SERVICE_UNAVAILABLE",
            "message": f"Unexpected error: {e}"
        }), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)