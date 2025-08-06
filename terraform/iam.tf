resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_secretsmanager_secret" "openai_api_key" {
  name = "aegis-ai/openai-api-key"
}

data "aws_iam_policy_document" "ecs_task_read_secrets" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      aws_secretsmanager_secret.db_password.arn,
      data.aws_secretsmanager_secret.openai_api_key.arn
    ]
  }
}

resource "aws_iam_policy" "ecs_task_read_secrets" {
  name   = "${var.project_name}-ecs-task-read-secrets-policy"
  policy = data.aws_iam_policy_document.ecs_task_read_secrets.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_read_secrets" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_task_read_secrets.arn
}

# --- ADD THIS BLOCK FOR GITHUB ACTIONS ---

# IAM Role that GitHub Actions will assume to deploy the application
resource "aws_iam_role" "github_actions_deploy_role" {
  name = "GitHubActionsDeployRole"

  # Policy that allows GitHub's OIDC provider to assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:*"
          }
        }
      }
    ]
  })
}

# Policy allowing the role to push to ECR and deploy to ECS
resource "aws_iam_policy" "github_actions_deploy_policy" {
  name = "GitHubActionsDeployPolicy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # 1. Allow getting the login token for the entire region
      {
        Effect   = "Allow"
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      # 2. Allow pushing images only to our specific repository
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:CompleteLayerUpload",
          "ecr:InitiateLayerUpload",
          "ecr:PutImage",
          "ecr:UploadLayerPart"
        ]
        Resource = aws_ecr_repository.api.arn
      },
      # 3. The ECS statement remains the same
      {
        Effect = "Allow"
        Action = [
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition",
          "ecs:UpdateService"
        ]
        Resource = "*" # Simplified for this project
      },
      # --- ADD THIS NEW STATEMENT ---
      # 4. Allow the deploy role to pass the task execution role to ECS
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = aws_iam_role.ecs_task_execution_role.arn
      }
      # ---
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_actions_deploy_attachment" {
  role       = aws_iam_role.github_actions_deploy_role.name
  policy_arn = aws_iam_policy.github_actions_deploy_policy.arn
}

data "aws_caller_identity" "current" {}

variable "github_repo" {
  description = "Your GitHub repository in user/repo format."
  type        = string
  default     = "zhu-weijie/aegis-ai"
}

data "aws_iam_policy_document" "ecs_exec_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "ecs_exec_policy" {
  name   = "${var.project_name}-ecs-exec-policy"
  policy = data.aws_iam_policy_document.ecs_exec_policy.json
}
