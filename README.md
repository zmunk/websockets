## Setup

    $ tf apply

## Teardown

    $ tf destroy

## Testing websocket
```bash
export API_URL=$(tf output -raw websocket_api_endpoint)
uv run scripts/test_websocket.py
# view websocket connect logs
uv run --with zmunk-awslogs -m awslogs $(tf output -raw websocket_connect_lambda_log_group)
# view websocket disconnect logs
uv run --with zmunk-awslogs -m awslogs $(tf output -raw websocket_disconnect_lambda_log_group)
# view websocket sendmessage logs
uv run --with zmunk-awslogs -m awslogs $(tf output -raw websocket_sendmessage_lambda_log_group)
```
