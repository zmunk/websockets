## Setup

    $ tf apply

## Teardown

    $ tf destroy

## Testing websocket
```bash
export API_URL=$(tf output -raw websocket_api_endpoint)
uv run scripts/test_websocket.py

uv run scripts/client.py

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
## Websocket Dialog Documentation
Receiving message from server:
```json
{
    "type": "message",
    "body": {
        "message": "Hello, friend.",
        "sender": "Elliot"
    }
}
```
Sending message to server (Note: `"action": "sendmessage"` needs to always be included):
```json
{
    "action": "sendmessage",
    "type": "message",
    "body": {
      "message": "Hello, friend."
    }
}
```
