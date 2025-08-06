# This resource establishes the one-time trust relationship between your AWS account
# and GitHub's OpenID Connect (OIDC) provider.
# It is a prerequisite for any IAM role that uses GitHub for federated identity.
resource "aws_iam_openid_connect_provider" "github" {
  # The URL of the OIDC identity provider. For GitHub Actions, this is always the same.
  url = "https://token.actions.githubusercontent.com"

  # The audience value for the OIDC provider. For AWS, this is always the same.
  client_id_list = ["sts.amazonaws.com"]

  # The SHA1 thumbprint of the OIDC provider's root CA certificate.
  # This is a security measure to verify the provider's identity.
  # This value can be found in the AWS documentation for IAM OIDC providers.
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}