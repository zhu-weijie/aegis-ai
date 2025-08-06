resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project_name}-api"
  retention_in_days = 7 # Good practice to set a retention period

  tags = {
    Name = "${var.project_name}-api-log-group"
  }
}
