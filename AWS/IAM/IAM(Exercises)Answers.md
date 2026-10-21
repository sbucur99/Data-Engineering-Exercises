Section A: IAM Answers

1. User vs Group vs Role

- User: a permanent identity for one person or app, with long-term credentials 
(password, access keys).
- Group: a collection of users that share permissions. It can’t log in and can’t be nested. You attach policies to the group and every member inherits them.
- Role: an identity with no long-term credentials that is assumed temporarily by a user, service (EC2, Lambda), another account, or a federated identity. STS issues short-lived credentials.

2. Why IAM is global
IAM isn’t tied to a region. Users, groups, roles, and policies are created once and apply across all regions in the account. The data is replicated internally, and you manage it through a single global endpoint. This lets one identity work in every region without duplication. (Some pieces are partitioned, e.g. separate GovCloud and China partitions.)

3. AWS-managed vs customer-managed policies

- AWS-managed: created and updated by AWS (e.g. AmazonS3ReadOnlyAccess). Convenient, but broad, and you can’t edit them. AWS may change them as services evolve.
- Customer-managed: you write and own them, so you can scope them tightly, version them (up to 5 versions, with rollback), and reuse them across identities.

Use AWS-managed for quick starts, and customer-managed for least-privilege production access.

4. Why roles are safer than access keys

- Role credentials are temporary (minutes to hours) and rotate automatically, so a leak expires on its own.
- Access keys are long-lived. They get committed to Git, left in config files, and forgotten.
- With roles there are no secrets to store, rotate, or distribute. An EC2 instance profile or Lambda execution role just gets credentials from the environment.
- Role assumption is logged in CloudTrail with the session identity, so activity is easier to trace.

5. Least privilege
Grant only the permissions needed for the task, on only the resources needed, for only as long as needed. It limits blast radius if credentials are stolen or a mistake is made, helps meet compliance requirements, and reduces lateral movement for an attacker. In practice: start narrow, expand when needed, and use IAM Access Analyzer’s policy generation to trim permissions based on actual usage.

6. Policy JSON structure

json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadOrders",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"],
      "Condition": {
        "IpAddress": {"aws:SourceIp": "203.0.113.0/24"}
      }
    }
  ]
}
Version: policy language version (almost always 2012-10-17).
Statement: one or more permission rules.
Sid: optional label.
Effect: Allow or Deny. An explicit Deny always wins.
Action: the API operations.
Resource: the ARNs the action applies to.
Condition: optional rules (IP, MFA, tags, time).
Principal: used only in resource-based and trust policies, to say who it applies to.

7. Federation with Okta / Azure AD
Instead of creating IAM users, you trust an external identity provider.

- SAML 2.0: register the IdP in IAM as an identity provider. The user signs in at Okta/Azure AD, which returns a SAML assertion. AWS STS (AssumeRoleWithSAML) exchanges it for temporary credentials for a role mapped to that user’s group or attributes.
- OIDC: the same idea using tokens (AssumeRoleWithWebIdentity), common for GitHub Actions and Kubernetes.
- IAM Identity Center (SSO): the modern recommended approach. Connect it to Okta or Azure AD (with SCIM for user provisioning), then assign permission sets across accounts.

Benefits: central user management, MFA and offboarding handled in one place, and no long-lived AWS credentials.

8. Limits (default quotas, many adjustable)

5,000 IAM users per account
300 groups per account (a user can belong to 10)
1,000 roles per account
1,500 customer-managed policies per account
10 managed policies attached per user/group/role by default (raisable to 20)
Managed policy size: 6,144 characters
2 access keys per user
Role session duration: 1 to 12 hours

Quotas change, so check the current Service Quotas page before relying on exact numbers. These limits are one reason large organizations use federation or Identity Center rather than thousands of IAM users.

9. When to use inline policies
Use them when the policy must be strictly tied to one identity: it’s created with the identity and deleted when the identity is deleted. That guarantees the permissions can’t be accidentally attached to anyone else. They suit one-off, unique permissions. Otherwise, prefer managed policies because they’re reusable, versioned, and easier to audit.

10. Auditing tools

- CloudTrail: records API calls (who did what, when, from where). The primary audit log.
- IAM Access Analyzer: finds resources shared externally, unused access, and generates least-privilege policies.
- IAM credential report: account-wide CSV of users, password age, MFA status, key age.
- IAM “last accessed” data: shows when services and actions were last used, to remove unused permissions.
- AWS Config: tracks IAM configuration changes and evaluates compliance rules.
- Security Hub / GuardDuty: flags risky IAM configurations and suspicious activity.
- CloudWatch + EventBridge: alerts on events like root logins or policy changes.