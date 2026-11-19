terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configured with -backend-config=backend.hcl.example.
  # State belongs in MinIO, not on the student workstation.
  backend "s3" {}
}
