import json
import platform
import subprocess
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    unset_jwt_cookies,
)
from wakeonlan import send_magic_packet

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)


def has_mac_address(array, mac_address):
    for index, item in enumerate(array):
        if item["mac"] == mac_address:
            return index
    return -1


def ping_device(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]

    return subprocess.call(command) == 0


@app.route("/token", methods=["POST"])
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if username != "testuser" or password != "test":
        return {"msg": "Wrong email or password"}, 401

    access_token = create_access_token(identity=username)
    response = {"access_token": access_token}
    return response


@app.route("/sendWol", methods=["POST"])
def sendWol():
    data = request.get_json()
    mac_address = data["mac"]
    send_magic_packet(mac_address)

    return jsonify({"message": "Magic packet sent"})


@app.route("/getDevices", methods=["GET"])
def getDevices():
    with open("./data/devices.json") as file:
        devices_json = file.read()

    return json.loads(devices_json)


@app.route("/addDevice", methods=["POST"])
def addDevice():
    data = request.get_json()
    with open("./data/devices.json", "r") as file:
        devices_json = json.load(file)

    devices_json["devices"].append(data)

    with open("./data/devices.json", "w") as file:
        json.dump(devices_json, file)
    print(devices_json)

    return jsonify({"devices": devices_json["devices"]})


@app.route("/rmDevice", methods=["POST"])
def rmDevice():
    data = request.get_json()
    mac = data["mac"]

    with open("./data/devices.json", "r") as file:
        devices_json = json.load(file)

    device_index = has_mac_address(devices_json["devices"], mac)

    if device_index != -1:
        devices_json["devices"].remove(devices_json["devices"][device_index])
        with open("./data/devices.json", "w") as file:
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
    app.run(host="0.0.0.0")
