output "websocket_api_endpoint" {
  description = "Websocket API url"
  value       = module.websocket_api.url
}

output "websocket_connect_lambda_log_group" {
  description = "Log group name of websocket connect function"
  value       = module.websocket_api.connect_lambda_log_group
}

output "websocket_disconnect_lambda_log_group" {
  description = "Log group name of websocket disconnect function"
  value       = module.websocket_api.disconnect_lambda_log_group
}

output "websocket_sendmessage_lambda_log_group" {
  description = "Log group name of websocket sendmessage function"
  value       = module.websocket_api.sendmessage_lambda_log_group
}
