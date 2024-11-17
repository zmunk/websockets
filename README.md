## Setup

    $ tf apply

## Teardown

    $ tf destroy

## Testing websocket
```bash
export API_URL=$(tf output -raw websocket_api_endpoint)
uv run scripts/test_websocket.py

uv run scripts/client.py --url $(tf output -raw websocket_api_endpoint)

uv run scripts/test_recv.py
```
## View lambda logs
```bash
# view websocket connect logs
uv run --with zmunk-awslogs -m awslogs $(tf output -raw websocket_connect_lambda_log_group)
# view websocket disconnect logs
uv run --with zmunk-awslogs -m awslogs $(tf output -raw websocket_disconnect_lambda_log_group)
# view websocket sendmessage logs
uv run --with zmunk-awslogs -m awslogs $(tf output -raw websocket_sendmessage_lambda_log_group)
```
# Websocket Dialog Documentation

## Receiving user message from server
Note: If `sender` is `None`, user is anonymous.
```json
{
    "type": "user_message",
    "body": {
        "message": "Hello, friend.",
        "sender": "Elliot"
    }
}
```
## Receiving server message
```json
{
    "type": "server_message",
    "body": {
        "message": "Elliot has entered the chat."
    }
}
```

## Sending data to server
Note: `"action": "sendmessage"` needs to always be included in the object.

Sending message
```json
{
    "type": "message",
    "body": {
      "message": "Hello, friend."
    }
}
```
Updating username:
```json
{
    "type": "set_username",
    "body": {
      "username": "Elliot"
    }
}
```
