from flask import Flask, request, jsonify, send_file, Response, send_from_directory, Blueprint
import sqlite3
import json
import requests
from flask_cors import CORS
from whitenoise import WhiteNoise
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os


from utils import diff_file_structures

ENABLE_AUTH = os.environ.get('ENABLE_AUTH', 'false').lower() == 'true'
AUTH_USER = os.environ.get('AUTH_USER', 'admin')
AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD', 'secret')
DB = os.environ.get('DB_PATH', "snapshots.db")

STATIC_FOLDER = '../renderer'
print(f"Authorization enabled: {ENABLE_AUTH}")
print(f"Database: {DB}")

app = Flask(__name__, static_folder=STATIC_FOLDER)
CORS(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root=f'{STATIC_FOLDER}/', index_file=False, autorefresh=False)
auth = HTTPBasicAuth()

api_blueprint = Blueprint("api_v1", __name__, url_prefix="/ssmm_api")

USERS = {
    AUTH_USER: generate_password_hash(AUTH_PASSWORD)
}

@auth.verify_password
def verify_password(username, password):
    if username in USERS and check_password_hash(USERS.get(username), password):
        return username
    return None

@app.before_request
def protect_all():
    if not ENABLE_AUTH or request.path.startswith("/proxy/"):
        return
    return auth.login_required(lambda: None)()



# Latest snapshot
@api_blueprint.route("/snapshot/<system_id>/latest")
def latest_snapshot(system_id):
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT filepath FROM snapshots WHERE system_id=? ORDER BY time DESC LIMIT 1",
        (system_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {"error": "not found"}, 404
    return send_file(row[0])

# Time range query
@api_blueprint.route("/snapshot/<system_id>/<date>")
def range_query(system_id, date):
   
    conn = sqlite3.connect(DB)
    cursor = conn.execute(
        "SELECT filepath FROM snapshots WHERE system_id=? AND time <= ? ORDER BY time DESC LIMIT 1",
        (system_id, date)
    )

    row = cursor.fetchone()
    if not row:
        return [], 200
    else:
        with open(row[0]) as f:
            result = json.load(f)
    conn.close()
    return jsonify(result)


def to_utc(timestamp):
    return timestamp[0:4] + "-" + timestamp[4:6] + "-" + timestamp[6:8] + "T" + timestamp[8:10] + ":" + timestamp[10:12] + ":" + timestamp[12:14] + "Z"


@api_blueprint.route("/snapshot/<system_id>/times")
def snapshot_times(system_id):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT time, system_id
        FROM snapshots
        WHERE system_id=?
        ORDER BY time
        """,
        (system_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify([])

    times = [
        {
            "timestamp": to_utc(r[0]),
            "event": r[1]
        }
        for r in rows
    ]

    return jsonify(times)


@api_blueprint.route("/snapshot/times")
def all_times():

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT time, system_id 
        FROM snapshots 
        WHERE system_id != 'RealTimeDownlink'
        ORDER BY time"""
    )

    rows = cursor.fetchall()
    conn.close()

    times = [
        {
            "timestamp": to_utc(r[0]),
            "event": r[1]
        }
        for r in rows
    ]

    return jsonify(times)


@api_blueprint.route("/snapshot/<system_id>/diff/<date1>/<date2>")
def query_diff(system_id, date1, date2):
   
    conn = sqlite3.connect(DB)
    
    downlink = []
    
    # Retrieve donwlinks
    cursor = conn.execute(
        "SELECT filepath, time FROM snapshots WHERE system_id=? AND time <= ? ORDER BY time DESC LIMIT 1",
        ('DirectoryDownlink', date1)
    )
    prev = cursor.fetchone()
    if prev:
        downlink.append({"time": prev[1], "filepath": prev[0]}) 

    cursor = conn.execute(
        "SELECT filepath, time FROM snapshots WHERE system_id=? AND time >= ? AND time <= ? ORDER BY time ASC",
        ('DirectoryDownlink', date1, date2)
    )
    for step in cursor.fetchall():
        downlink.append({"time": step[1], "filepath": step[0]}) 

    cursor = conn.execute(
        "SELECT filepath, time FROM snapshots WHERE system_id=? AND time >= ? AND time <= ? ORDER BY time ASC",
        (system_id, date1, date2)
    )

    all_added_files = []
    all_removed_files = []

    for current, nxt in iterate_with_next(cursor):
        current_json = read_json(current[0])
        nxt_json = read_json(nxt[0])

        downlink_state = search_active_downlink(downlink, current[1])
        added_files, removed_files = diff_file_structures(downlink_state.get("data") if downlink_state else None, current_json.get("data"), nxt_json.get("data"))
        step = {
            "source": current_json["timestamp"],
            "target": nxt_json["timestamp"]
        } 

        all_added_files.extend([{ **f, "step": step} for f in added_files])
        all_removed_files.extend([{ **f, "step": step} for f in removed_files])

    result = {
        "origin": date1,
        "target": date2,
        "added": all_added_files,
        "removed": all_removed_files
    }

    conn.close()
    return jsonify(result)


def iterate_with_next(cursor):
    current = cursor.fetchone()
    if current is None:
        return

    while True:
        nxt = cursor.fetchone()
        if nxt is None:
            break

        yield current, nxt
        current = nxt



def read_json(filepath):
    with open(filepath) as f:
        return json.load(f)


def search_active_downlink(downlink, time):
    file_path = None
    for slot in downlink:
        if time < slot.get('time'):
            break
        file_path = slot.get('filepath')
    
    if file_path:
        return read_json(file_path)
    return None

@api_blueprint.route("/downloads/<date1>/<date2>")
def query_downloads(date1, date2):
    conn = sqlite3.connect(DB)
    
    x_band = {}
    ka_band = {}

    cursor = conn.execute(
        "SELECT filepath, time FROM snapshots WHERE system_id=? AND time >= ? AND time <= ? ORDER BY time ASC",
        ('RealTimeDownlink', date1, date2)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify([])

    for row in rows:
        timestamp = row[1]
        current_json = read_json(row[0])

        file_id = (
            current_json.get("data", {})
                .get("x", {})
                .get("transmitting", {})
                .get("file_id")
        )
        if file_id:
            x_band[file_id] = { 'file_id' : file_id, 'timestamp': timestamp}

    return x_band


# Change this to the API you want to proxy
TARGET_BASE = "http://opsweb.esoc.esa.int/"

# Optional: restrict allowed methods
ALLOWED_METHODS = ["GET", "OPTIONS"]


@api_blueprint.route("/proxy/<path:path>", methods=ALLOWED_METHODS)
def proxy(path):
    # Construct full target URL
    target_url = f"{TARGET_BASE}/{path}"

    # Forward headers (excluding Host)
    headers = {
        key: value
        for key, value in request.headers
        if key.lower() != "host"
    }

    # Forward request to target
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers=headers,
        params=request.args,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    # Build response
    excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
    response_headers = [
        (name, value)
        for name, value in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    response = Response(resp.content, resp.status_code, response_headers)

    return response


@app.route('/')
def home():
    return send_from_directory(STATIC_FOLDER, 'index.html')

# 4. Manejador de rutas (Catch-all) para React Router protegido
# @app.errorhandler(404)
# def route_404(e):
#     return send_from_directory(STATIC_FOLDER, 'index.html')

app.register_blueprint(api_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
