locals {
  prefix = "s${var.student_id}"
}

resource "aws_s3_bucket" "patient_data" {
  bucket = "${local.prefix}-patient-data"
}

resource "aws_s3_bucket_versioning" "patient_data" {
  bucket = aws_s3_bucket.patient_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "patient_data" {
  bucket                  = aws_s3_bucket.patient_data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_user" "analyst" {
  name = "${local.prefix}-analyst"
}

# The lab starts with a deliberately broad policy. The learner replaces this
# with a scoped policy and proves the denied actions.
resource "aws_iam_policy" "analyst" {
  name        = "${local.prefix}-analyst-policy"
  description = "Simulated cloud lab policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = var.lab_mode ? ["s3:*"] : [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
        ]
        Resource = var.lab_mode ? ["*"] : [
          aws_s3_bucket.patient_data.arn,
          "${aws_s3_bucket.patient_data.arn}/*",
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "analyst" {
  user       = aws_iam_user.analyst.name
  policy_arn = aws_iam_policy.analyst.arn
}

resource "aws_iam_access_key" "analyst" {
  user = aws_iam_user.analyst.name
}

resource "aws_secretsmanager_secret" "app" {
  name = "${local.prefix}-app-secret"
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    username   = "svc-${var.student_id}"
    app_secret = "example-not-a-secret-${var.student_id}"
  })
}

output "bucket" {
  value = aws_s3_bucket.patient_data.bucket
}

output "analyst_user" {
  value = aws_iam_user.analyst.name
}

output "secret_name" {
  value = aws_secretsmanager_secret.app.name
}

output "access_key_id" {
  value     = aws_iam_access_key.analyst.id
  sensitive = true
}

output "secret_access_key" {
  value     = aws_iam_access_key.analyst.secret
  sensitive = true
}
