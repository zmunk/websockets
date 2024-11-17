import os
import json
import uuid
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["CONNECTIONS_TABLE"])
apigateway = None


def lambda_handler(event, context):
    global apigateway

    conn_id = event["requestContext"]["connectionId"]
    domain_name = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    endpoint = f"https://{domain_name}/{stage}"
    apigateway = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)
    body = json.loads(event["body"])
    event_type = body["type"]
    event_body = body["body"]

    print(f"{conn_id = }")
    print(f"{endpoint = }")
    print(f"{body = }")

    if event_type == "message":
        try:
            response = table.get_item(Key={"connection_id": conn_id})
            item = response.get("Item", {})
            sender_name = item.get("username")
            sender_id = item["user_id"]
        except Exception as e:
            print(f"Error getting connection: {str(e)}")
            sender_name = None
        else:
            broadcast_user_message(
                event_body["message"],
                sender_name,
                sender_id,
                skip=[conn_id],
            )

    elif event_type == "set_username":
        username = event_body["username"]
        user_id = str(uuid.uuid4())
        try:
            table.update_item(
                Key={"connection_id": conn_id},
                UpdateExpression="SET username = :username, user_id = :user_id",
                ExpressionAttributeValues={
                    ":username": username,
                    ":user_id": user_id,
                },
            )
        except Exception as e:
            print(f"Error getting connection: {str(e)}")

        send_message(create_server_message(f"Welcome, {username}!"), conn_id)
        broadcast_server_message(f"{username} has entered the chat.", skip=[conn_id])

    else:
        print(f"unknown event type: {event_type}")
        return {"statusCode": 500}

    return {}


def broadcast_user_message(message, sender_name, sender_id, skip=[]):
    data = {
        "type": "user_message",
        "body": {
            "message": message,
            "sender": sender_name,
            "sender_id": sender_id,
        },
    }
    broadcast_message(data, skip=skip)


def create_server_message(message):
    return {
        "type": "server_message",
        "body": {"message": message},
    }


def broadcast_server_message(message, skip=[]):
    data = create_server_message(message)
    broadcast_message(data, skip=skip)


def broadcast_message(data, skip=[]):
    for connection in get_connections():
        connection_id = connection["connection_id"]

        if connection_id in skip:
            continue

        send_message(data, connection_id)


def send_message(data, connection_id):
    assert apigateway is not None

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
