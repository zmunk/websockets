import os
import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["CONNECTIONS_TABLE"])


def lambda_handler(event, context):
    conn_id = event["requestContext"]["connectionId"]
    domain_name = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    endpoint = f"https://{domain_name}/{stage}"

    print(f"{conn_id = }")
    print(f"{endpoint = }")

    username = get_username(conn_id)

    try:
        table.delete_item(Key={"connection_id": conn_id})
    except Exception as e:
        print(f"Error deleting connection: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(str(e))}

    # send disconnect message
    broadcast_server_message(endpoint, f"{username} has left the chat.")

    return {}


def get_username(conn_id: str) -> None | str:
    try:
        response = table.get_item(Key={"connection_id": conn_id})
        return response.get("Item", {}).get("username")
    except Exception as e:
        print(f"Error getting connection: {str(e)}")
        return None


def broadcast_server_message(endpoint, message, skip=[]):
    data = {
        "type": "server_message",
        "body": {"message": message},
    }
    broadcast_message(endpoint, data, skip=skip)


def get_connections():
    response = table.scan()
    yield from response["Items"]

    # Handle pagination if there are more items
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        yield from response["Items"]


def broadcast_message(endpoint, data, skip=[]):
    apigateway = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)

    for connection in get_connections():
        connection_id = connection["connection_id"]

        if connection_id in skip:
            continue

        try:
            apigateway.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(data),
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "GoneException":
                # Connection is no longer valid, delete it from the table
                table.delete_item(Key={"connection_id": connection_id})
            else:
                print(f"Error sending message to {connection_id}: {str(e)}")
