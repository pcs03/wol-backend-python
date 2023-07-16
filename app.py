import json
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS
from wakeonlan import send_magic_packet

app = Flask(__name__)
CORS(app)


def has_mac_address(array, mac_address):
    for index, item in enumerate(array):
        if item["mac"] == mac_address:
            return index
    return -1


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

    # devices_json["devices"].append(data)

    # with open("./data/devices.json", "w") as file:
    #     json.dump(devices_json, file)

    # return jsonify(devices_json)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
