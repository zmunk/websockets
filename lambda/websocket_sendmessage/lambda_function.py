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
        broadcast_message(endpoint, sender_name, conn_id, event_body["message"])

    elif event_type == "set_username":
        try:
            table.update_item(
                Key={"connection_id": conn_id},
                UpdateExpression="SET username = :username",
                ExpressionAttributeValues={":username": event_body["username"]},
            )
        except Exception as e:
            print(f"Error getting connection: {str(e)}")

    else:
        print(f"unknown event type: {event_type}")
        return {"statusCode": 500}

    return {}


def broadcast_message(endpoint, sender_name, sender_id, message):
    apigateway = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)

    # sender_name = "anonymous"
    if sender_name is None:
        sender_name = "anonymous"
    data = {
        "type": "message",
        "body": {
            "message": message,
            "sender": sender_name,
        },
    }
    for connection in get_connections():
        connection_id = connection["connection_id"]

        # Skip sender
        if connection_id == sender_id:
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
