import os
import boto3
import json

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["CONNECTIONS_TABLE"])


def lambda_handler(event, context):
    conn_id = event["requestContext"]["connectionId"]

    print(f"{conn_id = }")

    try:
        table.put_item(
            Item={
                "connection_id": conn_id,
            }
        )
    except Exception as e:
        print(f"Error saving connection: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(str(e))}

    return {}
