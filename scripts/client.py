# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "websockets",
# ]
# ///
import os
import json
import asyncio
import builtins
import sys
import tty
import termios
import argparse
import websockets
from websockets.exceptions import ConnectionClosedOK

DEBUGGING = False


async def send_socket_message(socket, event_type, body):
    await socket.send(
        json.dumps(
            {
                "action": "sendmessage",  # required
                "type": event_type,
                "body": body,
            }
        )
    )


async def set_username(socket):
    inp = input("Please enter your username: ")
    await send_socket_message(socket, "set_username", {"username": inp})


def println(x):
    builtins.print("\r" + str(x), end="", flush=True)
    builtins.print("\r")


def print(x):
    builtins.print("\r" + str(x), end="")


def grey(s):
    return f"\033[2;37m{s}\033[0m"


async def receiver(socket, queue):
    """
    If receives message, adds to queue.
    """

    def println(x):
        builtins.print(x, end="", flush=True)
        builtins.print("\r")

    while True:
        try:
            raw_message = await socket.recv()
            message = json.loads(raw_message)
            message_type = message["type"]
            body = message["body"]
            match message_type:
                case "user_message":
                    username = body["sender"]
                    if username is None:
                        username = grey("anonymous")
                    display = f"{username}: {body['message']}"
                case "server_message":
                    display = body["message"]
                case _:
                    raise RuntimeError(f"invalid type: {message_type}")
            await queue.put({"type": "message", "value": display})
        except (KeyboardInterrupt, ConnectionClosedOK):
            break
        except Exception as e:
            print(f"Error in receiver: {e}")
            break


async def mainloop(socket, queue):
    """
    Reads from queue, if message from server, prints message, if keypress from user, prints  keypress.
    """

    def clear():
        print(" " * len(display))

    prompt = "> "
    display = prompt
    user_input = ""
    print(display)
    while True:
        msg = await queue.get()

        if DEBUGGING:
            println(msg)
            continue

        if msg["type"] == "event_key":
            if msg["value"] == EventKey.DELETE:
                # Handle delete
                clear()
                user_input = user_input[:-1]
            elif msg["value"] == EventKey.ENTER:
                # Handle submit
                print("\n")
                await send_socket_message(socket, "message", {"message": user_input})
                user_input = ""
        elif msg["type"] == "character":
            user_input += msg["value"]  # Append character to display
        elif msg["type"] == "message":
            clear()
            println(msg["value"])
        else:
            continue
        display = prompt + user_input
        print(display)


def _getch():
    """Get one character from user"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


class EventKey:
    DELETE = "delete"
    ENTER = "enter"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"

    ALL = {DELETE, ENTER, LEFT, RIGHT, UP, DOWN}


async def getch():
    loop = asyncio.get_running_loop()
    ch = await loop.run_in_executor(None, _getch)
    if ch == "\x1b":
        code = ""
        for _ in range(2):
            code += await loop.run_in_executor(None, _getch)
        if code == "[D":
            return EventKey.LEFT
        elif code == "[C":
            return EventKey.RIGHT
        elif code == "[A":
            return EventKey.UP
        elif code == "[B":
            return EventKey.DOWN
        else:
            raise RuntimeError(f"code: {code}")
    if ch == "\x03":
        raise KeyboardInterrupt
    if ch == "\x7f":
        return EventKey.DELETE
    if ch == "\r":
        return EventKey.ENTER
    return ch


async def user_interaction(queue):
    """
    Checks for user interaction, if user presses a key, adds keypress to queue.
    """
    while True:
        ch = await getch()

        if ch in EventKey.ALL:
            await queue.put({"type": "event_key", "value": ch})
        else:
            await queue.put({"type": "character", "value": ch})


async def main(url):
    queue = asyncio.Queue()

    try:
        async with websockets.connect(url) as socket:
            await set_username(socket)
            await asyncio.gather(
                mainloop(socket, queue),
                user_interaction(queue),
                receiver(socket, queue),
            )
    except KeyboardInterrupt:
        print("\nShutting down...")
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="api url", required=True)
    args = parser.parse_args()
    try:
        asyncio.run(main(args.url))
    except KeyboardInterrupt:
        pass
