variable "student_id" {
  description = "Short learner identifier used to prefix every resource"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{2,12}$", var.student_id))
    error_message = "Use 2-12 lowercase letters or digits."
  }
}

variable "region" {
  description = "Synthetic region"
  type        = string
  default     = "us-east-1"
}

variable "localstack_endpoint" {
  description = "LocalStack edge endpoint"
  type        = string
  default     = "http://localhost:4566"
}

variable "lab_mode" {
  description = "When true, create the intentionally weak IAM policy the learner must fix"
  type        = bool
  default     = true
}
