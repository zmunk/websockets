terraform {
  required_version = ">= 1.9.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.32"
    }
  }
}

provider "aws" {
  profile = "website"
  region  = "us-east-1"
}

module "websocket_api" {
  source  = "zmunk/websocket-api/aws"
  version = "~> 1.0.0"

  api_name                  = "WebsocketAPI"
  connect_function_path     = "./lambda/websocket_connect"
  disconnect_function_path  = "./lambda/websocket_disconnect"
  sendmessage_function_path = "./lambda/websocket_sendmessage"
}
