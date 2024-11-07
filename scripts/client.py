# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "websockets",
# ]
# ///
import os
import json
import websockets.sync.client
import atexit

API_URL = os.environ["API_URL"]


@atexit.register
def close_socket():
    socket.close()
    print("\rsuccessfully disconnected")


socket = websockets.sync.client.connect(API_URL)
print("successfully connected")

while True:
    try:
        inp = input("> ")
    except KeyboardInterrupt:
        break
    socket.send(
        json.dumps(
            {
                "action": "sendmessage",
                "message": inp,
            }
        )
    )
