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
    try:
        socket.close()
    except NameError:
        pass
    else:
        print("\rsuccessfully disconnected")


try:
    socket = websockets.sync.client.connect(API_URL)
except Exception as e:
    print(e)
    print("failed to connect")
    print(f"{API_URL = }")
    print("make sure the API_URL is correct")
    exit(1)
print("successfully connected")

while True:
    try:
        inp = input("> ")
    except KeyboardInterrupt:
        break
    socket.send(
        json.dumps(
            {
                "action": "sendmessage",  # required
                "type": "message",
                "body": {
                    "message": inp,
                },
            }
        )
    )
