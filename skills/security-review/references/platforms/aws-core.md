# AWS core overlay

Use this overlay for IAM, VPC, Lambda, ECS, EKS, S3, Secrets Manager, KMS, CloudFront, and CloudWatch decisions.

## Checks

- prefer roles and federation; avoid long-lived IAM user keys
- resource-scoped IAM with explicit conditions where possible
- block public storage and review bucket policies separately from IAM
- log auth failures and admin actions to centralized immutable storage
- verify encryption keys, key policies, and rotation fit the data sensitivity
- restrict metadata service and egress for workloads that do not need broad internet access

## Common failure patterns

- wildcard IAM resources for convenience
- Lambda or ECS task role can read broad secrets namespace
- “private subnet” used as substitute for service authorization
