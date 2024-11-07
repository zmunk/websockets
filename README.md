    ╷
    │ Error: creating API Gateway v2 Stage (prod): operation error ApiGatewayV2: CreateStage, https response error StatusCode: 400, RequestID: 284a02d1-2527-4651-a768-a6deb706dd69, BadRequestException: CloudWatch Logs role ARN must be set in account settings to enable logging
    │
    │   with module.api_gateway.aws_apigatewayv2_stage.this[0],
    │   on .terraform/modules/api_gateway/main.tf line 321, in resource "aws_apigatewayv2_stage" "this":
    │  321: resource "aws_apigatewayv2_stage" "this" {
    │
    ╵
