import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from wakeonlan import send_magic_packet

app = Flask(__name__)
CORS(app)


@app.route("/sendWol", methods=["POST"])
def sendWol():
    data = request.get_json()
    print(data)
    mac_address = data["mac-address"]
    send_magic_packet(mac_address)

    return jsonify({"message": "Magic packet sent"})


@app.route("/getDevices", methods=["GET"])
def getDevices():
    with open("./data/devices.json") as file:
        devices_json = file.read()

    print(devices_json)

    return json.loads(devices_json)


@app.route("/addDevice", methods=["POST"])
def addDevice():
    data = request.get_json()
    print(data)
    with open("./data/devices.json", "r") as file:
        devices_json = file.read()

    new_devices_json = devices_json.append(data)
    print(new_devices_json)

    with open("./data/devices.json", "w") as file:
        json.dump(new_devices_json, file)

    return json.loads(new_devices_json)


if __name__ == "__main__":
    app.run()
