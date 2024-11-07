def lambda_handler(event, context):
    conn_id = event["requestContext"]["connectionId"]
    print(f"{conn_id = }")

    return {}
