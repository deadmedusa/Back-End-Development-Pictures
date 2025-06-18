from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa: F401

# Load the picture data
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")

try:
    with open(json_url) as f:
        data: list = json.load(f)
except Exception:
    data = []

######################################################################
# RETURN HEALTH OF THE APP
######################################################################
@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################
@app.route("/count")
def count():
    """Return length of data"""
    if data:
        return jsonify(length=len(data)), 200
    return jsonify({"message": "Internal server error"}), 500

######################################################################
# CHECK JSON IS NOT EMPTY
######################################################################
@app.route("/check_json_not_empty", methods=["GET"])
def check_json_not_empty():
    """Sanity check route (for test_pictures_json_is_not_empty)"""
    return jsonify({"not_empty": bool(data)}), 200

######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    """Return all picture data"""
    return jsonify(data), 200

######################################################################
# GET A PICTURE BY ID
######################################################################
@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    """Return picture by ID"""
    picture = next((item for item in data if item.get("id") == id), None)
    if picture:
        return jsonify(picture), 200
    return jsonify({"error": "Picture not found"}), 404

######################################################################
# POST A NEW PICTURE (WITHOUT SPECIFIC ID)
######################################################################
@app.route("/picture", methods=["POST"])
def create_picture_placeholder():
    """Create new picture with auto-generated ID"""
    picture = request.get_json()
    if not picture:
        return jsonify({"error": "Invalid or missing JSON"}), 400
    
    # Check if ID was provided in request
    if 'id' in picture:
        # If ID was provided, check for duplicates
        if any(p.get('id') == picture['id'] for p in data):
            return jsonify({"Message": f"picture with id {picture['id']} already present"}), 302
    else:
        # Generate new ID if none provided
        picture['id'] = max(p['id'] for p in data) + 1 if data else 1
    
    data.append(picture)
    return jsonify(picture), 201

######################################################################
# POST A NEW PICTURE WITH SPECIFIC ID
######################################################################
@app.route("/picture/<int:id>", methods=["POST"])
def create_picture(id):
    """Create new picture with specific ID"""
    if any(p.get('id') == id for p in data):
        return jsonify({"Message": f"picture with id {id} already present"}), 302

    picture = request.get_json()
    if not picture:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    picture['id'] = id
    data.append(picture)
    return jsonify(picture), 201

######################################################################
# UPDATE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    """Update an existing picture"""
    # Get the picture data from request
    new_picture_data = request.get_json()
    if not new_picture_data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    # Find the picture to update
    for i, picture in enumerate(data):
        if picture["id"] == id:
            # Update all fields while preserving the ID
            updated_picture = {**picture, **new_picture_data}
            updated_picture["id"] = id  # Ensure ID remains the same
            data[i] = updated_picture
            return jsonify(updated_picture), 200
    
    # If picture not found
    return jsonify({"message": "picture not found"}), 404

######################################################################
# DELETE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    """Delete a picture by ID"""
    # Find the index of the picture with matching ID
    for i, picture in enumerate(data):
        if picture["id"] == id:
            # Remove the picture from the list
            del data[i]
            # Return empty response with 204 status
            return "", 204
    
    # If picture not found
    return jsonify({"message": "picture not found"}), 404
