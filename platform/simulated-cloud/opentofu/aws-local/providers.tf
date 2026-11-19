provider "aws" {
  region = var.region

  # LocalStack accepts synthetic credentials. Do not use real cloud keys here.
  access_key = "test"
  secret_key = "test"

  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  endpoints {
    iam            = var.localstack_endpoint
    sts            = var.localstack_endpoint
    s3             = var.localstack_endpoint
    secretsmanager = var.localstack_endpoint
    cloudtrail     = var.localstack_endpoint
    logs           = var.localstack_endpoint
  }
}
