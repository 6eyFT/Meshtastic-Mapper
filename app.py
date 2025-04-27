from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import shutil
import json
from perform_parse_data import parse_csv_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
SAVED_MAPS_FOLDER = "saved_maps"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SAVED_MAPS_FOLDER"] = SAVED_MAPS_FOLDER

app.secret_key = "super_secret_key_change_me"  # TODO: Replace with key

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAVED_MAPS_FOLDER, exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    saved_maps = {}
    for root, dirs, files in os.walk(SAVED_MAPS_FOLDER):
        rel_root = os.path.relpath(root, SAVED_MAPS_FOLDER)
        rel_root = rel_root.replace("\\", "/")  # Windows fix

        if rel_root == ".":
            rel_root = "root"

        for file in files:
            if file.endswith(".json"):
                if rel_root not in saved_maps:
                    saved_maps[rel_root] = []
                saved_maps[rel_root].append(file)

    return render_template("index.html", saved_maps=saved_maps)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    upload_name = request.form.get("upload_name")

    if not file or not upload_name:
        return "File and upload name are required.", 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    points = parse_csv_file(filepath)

    save_path = os.path.join(app.config["SAVED_MAPS_FOLDER"], upload_name)
    save_dir = os.path.dirname(save_path)
    os.makedirs(save_dir, exist_ok=True)

    with open(save_path + ".json", "w") as f:
        json.dump(points, f)

    flash("Upload successful! Map saved and ready to view.")
    return redirect(url_for("index"))


@app.route("/load_map/<path:map_name>", methods=["GET"])
def load_map(map_name):
    safe_map_path = os.path.join(app.config["SAVED_MAPS_FOLDER"], map_name)
    if not safe_map_path.endswith(".json"):
        safe_map_path += ".json"

    if not os.path.isfile(safe_map_path):
        return "Map not found.", 404

    with open(safe_map_path, "r") as f:
        points = json.load(f)

    return jsonify(points)


@app.route("/delete_map/<path:map_name>", methods=["DELETE"])
def delete_map(map_name):
    safe_path = os.path.join(app.config["SAVED_MAPS_FOLDER"], map_name)
    if not safe_path.endswith(".json"):
        safe_path += ".json"

    if os.path.isfile(safe_path):
        os.remove(safe_path)
        return '', 204
    else:
        return "Map not found.", 404


@app.route("/rename_map/<path:map_name>", methods=["POST"])
def rename_map(map_name):
    data = request.get_json()
    new_name = data.get('new_name')

    if not new_name:
        return "New name is required.", 400

    old_path = os.path.join(app.config["SAVED_MAPS_FOLDER"], map_name)
    if not old_path.endswith(".json"):
        old_path += ".json"

    if not new_name.endswith(".json"):
        new_name += ".json"

    new_path = os.path.join(app.config["SAVED_MAPS_FOLDER"], new_name)

    os.makedirs(os.path.dirname(new_path), exist_ok=True)

    if os.path.isfile(old_path):
        shutil.move(old_path, new_path)
        return '', 204
    else:
        return "Original map not found.", 404


if __name__ == "__main__":
    app.run(debug=True)
