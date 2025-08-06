resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
  tags = {
    Name = "${var.project_name}-cluster"
  }
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project_name}-api-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  # This is the definition for our container
  container_definitions = jsonencode([
    {
      name      = "${var.project_name}-api-container"
      image     = "nginx:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000,
          hostPort      = 8000
        }
      ],
      # --- ADD THIS ENTIRE BLOCK ---
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api.name,
          "awslogs-region"        = var.aws_region,
          "awslogs-stream-prefix" = "ecs"
        }
      },
      # ---
      secrets = [
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = aws_secretsmanager_secret.db_password.arn
        }
      ],
      environment = [
        {
          name  = "POSTGRES_USER"
          value = "aegis"
        },
        {
          name  = "POSTGRES_DB"
          value = "aegis"
        },
        {
          name  = "POSTGRES_SERVER"
          value = aws_db_instance.main.address
        },
        {
          name      = "OPENAI_API_KEY",
          valueFrom = "arn:aws:secretsmanager:ap-southeast-1:215288576473:secret:OPENAI_API_KEY-i2wK1a"
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "api" {
  name            = "${var.project_name}-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs_service.id]
    assign_public_ip = true
  }

  depends_on = [aws_nat_gateway.main]
}
