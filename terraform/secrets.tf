resource "random_id" "secret_suffix" {
  byte_length = 4 # Creates an 8-character hex string
}

resource "random_password" "db_password" {
  length           = 20
  special          = true
  override_special = "!#$%&'()*+,-./:;<=>?@[]^_`{|}~"
}

resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.project_name}/db-password-${random_id.secret_suffix.hex}"

  tags = {
    Name = "${var.project_name}-db-password-secret"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}
