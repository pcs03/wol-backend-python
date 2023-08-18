import json
import os
import platform
import subprocess
from datetime import datetime, timedelta, timezone

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from wakeonlan import send_magic_packet

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = "key"

project_base_path = os.path.dirname(os.path.realpath(__file__))


def has_mac_address(array, mac_address):
    for index, item in enumerate(array):
        if item["mac"] == mac_address:
            return index
    return -1


def ping_device(host):
    response = os.system("ping -c 1 -w 1 " + host)

    if response == 0:
        return True
    else:
        return False


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

    if lines:
        status = lines[0]
    else:
        status = "No response from device"

    return jsonify({"status": status})


@app.route("/getDevices", methods=["GET"])
def getDevices():
    with open(os.path.join(project_base_path, "data/devices.json"), "r") as file:
        devices_json = file.read()

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
