from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/hello", methods=["POST"])
def hello():
    data = request.json
    print(data)
    return jsonify({"message": "Hello, world!"})


if __name__ == "__main__":
    app.run()
