# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "websockets",
# ]
# ///
import os
import time
import json
import websockets.sync.client

API_URL = os.environ["API_URL"]

socket = websockets.sync.client.connect(API_URL)
print("successfully connected")
time.sleep(1)

socket.send(
    json.dumps(
        {
            "action": "sendmessage",
            "message": "hello",
        }
    )
)

socket.close()
print("successfully disconnected")
