# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "websockets",
# ]
# ///
import os
import websockets.sync.client
import atexit


@atexit.register
def close_socket():
    socket.close()
    print("\nsuccessfully disconnected")


socket = websockets.sync.client.connect(os.environ["API_URL"])
print("successfully connected")

while True:
    print("checking for messages ...")
    try:
        message = socket.recv()
    except KeyboardInterrupt:
        break
    else:
        print(f"{message = }")
