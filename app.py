from flask import Flask, jsonify, request
from flask_cors import CORS
from wakeonlan import send_magic_packet

app = Flask(__name__)
CORS(app)


@app.route("/wol", methods=["POST"])
def hello():
    data = request.get_json()
    print(data)
    mac_address = data["mac-address"]
    send_magic_packet(mac_address)

    return jsonify({"message": "Magic packet sent"})


if __name__ == "__main__":
    app.run()
