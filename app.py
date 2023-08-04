import json
import os
import platform
import sqlite3
import subprocess
from datetime import datetime, timedelta, timezone

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from wakeonlan import send_magic_packet

project_base_path = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = "dsafas5f41dsa65f1564635dfs"

db_path = os.path.join(project_base_path, "db/data.db")


def create_db():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='devices'"
    )

    if cursor.fetchone()[0] != 1:
        {
            cursor.execute(
                "CREATE TABLE devices (device_name text, username text, mac text, ip text)"
            )
        }

    cursor.execute(
        "INSERT INTO devices VALUES (?,?,?,?)", ["server", "pstet", "FF", "122"]
    )

    for row in cursor.execute("SELECT * FROM devices"):
        print(row)

    connection.close()


def has_mac_address(array, mac_address):
    for index, item in enumerate(array):
        if item["mac"] == mac_address:
            return index
    return -1


def ping_device(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]

    return subprocess.call(command) == 0


def shutdown_device(username, ip):
    ssh_param = f"{username}@{ip}"
    return subprocess.run(
        ["ssh", ssh_param, "sudo", "shutdown", "-h", "now"],
        capture_output=True,
        text=True,
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data["username"]
    password = data["password"]

    exp_delta_minutes = 10

    if username == "testuser" and password == "test":
        token = jwt.encode(
            {
                "username": username,
                "exp": datetime.utcnow() + timedelta(minutes=exp_delta_minutes),
            },
            app.config["SECRET_KEY"],
        )

        return jsonify({"token": token.decode(), "exp": exp_delta_minutes})

    return jsonify({"message": "Incorrect usename or password"})


@app.route("/sendWol", methods=["POST"])
def sendWol():
    data = request.get_json()
    mac_address = data["mac"]
    send_magic_packet(mac_address)

    return jsonify({"message": "Magic packet sent"})


@app.route("/shutdown", methods=["POST"])
def sendShutdown():
    data = request.get_json()

    username = data["username"]
    ip = data["ip"]

    output = shutdown_device(username, ip)
    lines = output.stderr.splitlines()
    print(lines)

    return jsonify({"status": lines[0]})


@app.route("/getDevices", methods=["GET"])
def getDevices():
    with open(os.path.join(project_base_path, "data/devices.json"), "r") as file:
        devices_json = file.read()

    create_db()

    return json.loads(devices_json)


@app.route("/addDevice", methods=["POST"])
def addDevice():
    data = request.get_json()
    with open(os.path.join(project_base_path, "data/devices.json"), "r") as file:
        devices_json = json.load(file)

    devices_json["devices"].append(data)

    with open(os.path.join(project_base_path, "data/devices.json"), "w") as file:
        json.dump(devices_json, file)
    print(devices_json)

    return jsonify({"devices": devices_json["devices"]})


@app.route("/rmDevice", methods=["POST"])
def rmDevice():
    data = request.get_json()
    mac = data["mac"]

    with open(os.path.join(project_base_path, "data/devices.json"), "r") as file:
        devices_json = json.load(file)

    device_index = has_mac_address(devices_json["devices"], mac)

    if device_index != -1:
        devices_json["devices"].remove(devices_json["devices"][device_index])
        with open(os.path.join(project_base_path, "data/devices.json"), "w") as file:
            json.dump(devices_json, file)
        return jsonify(devices_json)
    else:
        return jsonify({"status": "no valid device"})


@app.route("/ping", methods=["POST"])
def ping():
    data = request.get_json()
    ip = data["ip"]

    return jsonify({"status": ping_device(ip)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
