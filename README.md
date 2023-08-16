# Wake on LAN Backend

## Overview

Backend for a web-based wake on lan application, that utilizes a Python Flask backend and a React frontend.

## Installation instructions

- Clone the repository
- Create a virtual environement

```
python -m venv ./venv
```

- Activate the virtual environment

```
source ./venv/bin/activate
```

- Install the requirements

```
pip install -r requirements.txt
```

## Production server with gunicorn

```
/srv/wol/wolBackend/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
