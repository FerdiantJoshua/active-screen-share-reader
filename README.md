# Active Screen-Share Reader

A Python-based server to receive sent WEBP image from the client counterpart of Golang Active Screen-share.

## Requirements

Python 3.10

```sh
python -m venv venv
# Windows
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Usage

1. Copy the `config.example.json` into `config.json`, adjust the value.  
with the `screenshotURLSend` pointing to this server's `/screenshot` endpoint.

2. Start the server

### Development Mode

```sh
python main.py
```

### Production Mode

```sh
waitress-serve --host 0.0.0.0 --port 5000 main:app
```

Access the server in `localhost:5000`.

### Available Endpoints

1. `/` (root)  
    For health check, and other metadata

2. `/getConfig`  
    Return the activation state & poll interval for configurting the Go active screen-share.

3. `/screenshot` (POST)  
    Endpoint to receive the screenshot data. Will be stored in this server's memory.

4. `/getLatestScreenshot`  
    Return the screenshot stored in the server's memory.

5. `/clearScreenshot`
    Clear the screenshot memory.

6. `/viewer`  
    The GUI version, to help polling the screenshot periodically, and also support partial screenshot.

7. `/shutdown`
    Terminate the server gracefully.

## Author

Ferdiant Joshua Muis

_P.S. this app is mostly created by Claude. I just modify some part of it._
