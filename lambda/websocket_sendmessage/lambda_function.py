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

    print(f"{conn_id = }")

    endpoint = f"https://{domain_name}/{stage}"
    print(f"{endpoint = }")

    body = json.loads(event["body"])
    print(f"{body = }")

    event_type = body["type"]
    event_body = body["body"]

    if event_type == "message":
        try:
            response = table.get_item(Key={"connection_id": conn_id})
            sender_name = response.get("Item", {}).get("username")
        except Exception as e:
            print(f"Error getting connection: {str(e)}")
            sender_name = None
        broadcast_user_message(
            endpoint,
            event_body["message"],
            sender_name,
            skip=[conn_id],
        )

    elif event_type == "set_username":
        username = event_body["username"]
        try:
            table.update_item(
                Key={"connection_id": conn_id},
                UpdateExpression="SET username = :username",
                ExpressionAttributeValues={":username": username},
            )
        except Exception as e:
            print(f"Error getting connection: {str(e)}")

        broadcast_server_message(
            endpoint,
            f"{username} has entered the chat.",
            skip=[conn_id],
        )

    else:
        print(f"unknown event type: {event_type}")
        return {"statusCode": 500}

    return {}


def broadcast_user_message(endpoint, message, sender_name, skip=[]):
    data = {
        "type": "user_message",
        "body": {
            "message": message,
            "sender": sender_name,
        },
    }
    broadcast_message(endpoint, data, skip=skip)


def broadcast_server_message(endpoint, message, skip=[]):
    data = {
        "type": "server_message",
        "body": {"message": message},
    }
    broadcast_message(endpoint, data, skip=skip)


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


def get_connections():
    response = table.scan()
    yield from response["Items"]

    # Handle pagination if there are more items
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        yield from response["Items"]
