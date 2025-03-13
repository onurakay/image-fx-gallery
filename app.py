from flask import Flask, render_template, request, url_for, jsonify
import json
import os
import shutil

app = Flask(__name__)

def load_data():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    query = request.args.get('q', '').strip().lower()
    tag_query = request.args.get('tag', '').strip().lower()
    data = load_data()

    if tag_query:
        data = [item for item in data if 'tags' in item and any(t.lower() == tag_query for t in item['tags'])]
    elif query:
        data = [item for item in data if query in item['prompt'].lower()]

    tags = set()
    for item in data:
        if 'tags' in item:
            tags.update(item['tags'])

    return render_template('index.html', images=list(reversed(data)), query=query, tags=sorted(tags))

@app.route('/add_tag', methods=['POST'])
def add_tag():
    image_file = request.form.get('image_file')
    tag = request.form.get('tag', '').strip()
    if not image_file or not tag:
        return jsonify({"status": "error", "message": "Missing image_file or tag"}), 400

    data = load_data()
    updated = False
    for record in data:
        if record.get('image_file') == image_file:
            if 'tags' not in record:
                record['tags'] = []
            if tag not in record['tags']:
                record['tags'].append(tag)
            updated = True
            break

    if updated:
        with open('database.json', 'w') as f:
            json.dump(data, f, indent=4)
        return jsonify({"status": "success", "tag": tag})
    else:
        return jsonify({"status": "error", "message": "Image not found"}), 404

@app.route('/delete_tag', methods=['POST'])
def delete_tag():
    image_file = request.form.get('image_file')
    tag = request.form.get('tag', '').strip()
    if not image_file or not tag:
        return jsonify({"status": "error", "message": "Missing image_file or tag"}), 400

    data = load_data()
    updated = False
    for record in data:
        if record.get('image_file') == image_file:
            if 'tags' in record and tag in record['tags']:
                record['tags'].remove(tag)
                updated = True
                break

    if updated:
        with open('database.json', 'w') as f:
            json.dump(data, f, indent=4)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Tag not found"}), 404

if __name__ == '__main__':
    # datavase backup
    if os.path.exists("database.json"):
        shutil.copy("database.json", "database_backup_1.json")
    app.run(debug=True, host='0.0.0.0', port=9595)
