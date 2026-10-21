Section A: Basics
- Object storage. Data is stored as objects (data + metadata + key) in buckets, not as blocks or a file system.
- There is no minimum. You can have zero buckets, and one is enough to start. Bucket names must be globally unique. The default limit is 10,000 general-purpose buckets per account (raisable), but check the current quota.

aws s3api create-bucket --bucket de-course-bucket --region us-east-1
# or the shorthand:
aws s3 mb s3://de-course-bucket

4. Upload file into bucket
   aws s3 cp data.csv s3://de-course-bucket/data.csv

- The object key is the object’s name within the bucket, including any “folder” prefix (e.g. raw/2026/data.csv). 
- The object URL is the full address built from the bucket, region, and key: https://de-course-bucket.s3.us-east-1.amazonaws.com/raw/2026/data.csv. 
The URL is only reachable if permissions allow it.

Obj Key- objects name (with folder)
Obj URL- full address

Section B: Core Operations

# 1. Create bucket (us-east-1 needs no LocationConstraint)
aws s3api create-bucket --bucket student-data-lake12345 --region us-east-1

# 2. Upload
aws s3 cp students.csv s3://student-data-lake12345/students.csv

# 3. Download
aws s3 cp s3://student-data-lake12345/students.csv ./students_downloaded.csv

# 4. Enable versioning, then upload the modified file under the same name
aws s3api put-bucket-versioning --bucket student-data-lake12345 --versioning-configuration Status=Enabled

aws s3 cp students.csv s3://student-data-lake12345/students.csv

# 5. Verify both versions
aws s3api list-object-versions --bucket student-data-lake12345 --prefix students.csv

- The output shows two entries under Versions with different VersionId values, and the newest has "IsLatest": true. 
- Versioning only applies to uploads made after you enable it, which is why step 4 enables it before the second upload.

Section C: Storage Classes & Lifecycle

1. Lifecycle policy

Save as lifecycle.json (using a file avoids PowerShell quoting problems):

json
{
  "Rules": [
    {
      "ID": "tier-down",
      "Status": "Enabled",
      "Filter": { "Prefix": "" },
      "Transitions": [
        { "Days": 30,  "StorageClass": "STANDARD_IA" },
        { "Days": 365, "StorageClass": "GLACIER" }
      ]
    }
  ]
}

aws s3api put-bucket-lifecycle-configuration --bucket student-data-lake12345 --lifecycle-configuration file://lifecycle.json

aws s3api get-bucket-lifecycle-configuration --bucket student-data-lake12345

2. Simulate the transition

Lifecycle rules run on object age and take days, so you can’t wait for them in a lab. 
- Instead, set the storage class yourself, which produces the same end state:


# Upload straight into Standard-IA (what the 30-day rule would do)
aws s3 cp logs.json s3://student-data-lake12345/logs/logs.json --storage-class STANDARD_IA

aws s3api head-object --bucket student-data-lake12345 --key logs/logs.json  
# shows "StorageClass": "STANDARD_IA"

# Move it to Glacier (what the 365-day rule would do)
aws s3api copy-object --bucket student-data-lake12345 --key logs/logs.json --copy-source student-data-lake12345/logs/logs.json --storage-class GLACIER
  
aws s3api head-object --bucket student-data-lake12345 --key logs/logs.json   
# now "GLACIER"

Notes: Standard-IA has a 30-day minimum before lifecycle can transition into it, and objects under 128 KB aren’t transitioned by default. Glacier objects must be restored (aws s3api restore-object) before you can read them.

3. Standard vs Intelligent-Tiering

	            Standard	                Intelligent-Tiering
Best for	    - Frequently accessed data	- Unknown or changing access patterns
How it works	- One tier, fixed price	    - Moves objects between access tiers
                                             automatically based on usage
Storage cost	- Higher per GB for cold 
                 data                       - Lower for data that goes unaccessed
Monitoring fee	- None	                    - Small per-object monthly fee
Retrieval fee	- None	                    - None
Small objects	- Normal	                - Under 128 KB aren’t 
                                            auto-tiered, so no benefit

Use Standard for hot, predictable data. Use Intelligent-Tiering when you can’t predict access and want savings without lifecycle rules.

Section D: Security

1. Public read policy

Block Public Access is on by default, so turn it off first, then apply the policy. Save as public-policy.json:

New bucket:   lock is ON  -> public policy gets rejected (Blocked)
You unlock:   lock is OFF -> public policy is allowed  (not blocked)

json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicRead",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::student-data-lake12345/*"
  }]
}

aws s3api put-public-access-block --bucket student-data-lake12345 --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=false

aws s3api put-bucket-policy --bucket student-data-lake12345 --policy file://public-policy.json

Do this only in a throwaway lab bucket, and remove it afterward. Public buckets are a classic source of data leaks.

this is how you remove the policy
aws s3api delete-bucket-policy --bucket student-data-lake12345

turn the lock back on
aws s3api put-public-access-block --bucket student-data-lake12345 --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

2. Restrict to one IAM role

Putting a new policy replaces the old one. Save as role-policy.json:

json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RoleReadWrite",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::<ACCOUNT_ID>:role/<ROLE_NAME>" },
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::student-data-lake/*"
    },
    {
      "Sid": "RoleList",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::<ACCOUNT_ID>:role/<ROLE_NAME>" },
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::student-data-lake"
    }
  ]
}

aws s3api put-bucket-policy --bucket student-data-lake12345 --policy file://role-policy.json

# Re-enable full public access blocking

aws s3api put-public-access-block --bucket student-data-lake --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

Note that ListBucket applies to the bucket ARN, while object actions apply to /*, which is why there are two statements.

3. Enable SSE-S3

Save as enc.json:

json
{
  "Rules": [
    { "ApplyServerSideEncryptionByDefault": { "SSEAlgorithm": "AES256" } }
  ]
}

aws s3api put-bucket-encryption --bucket student-data-lake --server-side-encryption-configuration file://enc.json
aws s3api get-bucket-encryption --bucket student-data-lake

Since January 2023, S3 encrypts all new objects with SSE-S3 by default, so this makes it explicit.

4. SSE-S3 vs SSE-KMS vs SSE-C

	                SSE-S3	        SSE-KMS	                        SSE-C
Who manages the key	AWS (S3-owned)	AWS KMS (AWS-managed or your own key)	You
Key storage	AWS	KMS	You store it, AWS never does
Setup	None, simplest	Pick a KMS key	Send the key with every request
Audit trail	Limited	Full key usage in CloudTrail	None from AWS for the key
Access control	Bucket permissions	Bucket permissions plus KMS key policy	Possession of the key
Extra cost / limits	Free	KMS request charges, possible throttling	None, but you must manage keys
Typical use	Default encryption	Compliance, key rotation, separation of duties	Strict requirement to hold your own keys

In short: SSE-S3 is automatic, SSE-KMS adds control and auditability, and SSE-C puts key custody entirely on you. If you lose an SSE-C key, the data is unrecoverable


4. SSE-S3 vs SSE-KMS vs SSE-C

WHO MANAGES THE KEY
  SSE-S3 : AWS (S3-owned)
  SSE-KMS: AWS KMS (AWS-managed or your own key)
  SSE-C  : You

KEY STORAGE
  SSE-S3 : AWS
  SSE-KMS: KMS
  SSE-C  : You store it, AWS never does

SETUP
  SSE-S3 : None, simplest
  SSE-KMS: Pick a KMS key
  SSE-C  : Send the key with every request

AUDIT TRAIL
  SSE-S3 : Limited
  SSE-KMS: Full key usage in CloudTrail
  SSE-C  : None from AWS for the key

ACCESS CONTROL
  SSE-S3 : Bucket permissions
  SSE-KMS: Bucket permissions plus KMS key policy
  SSE-C  : Possession of the key

EXTRA COST / LIMITS
  SSE-S3 : Free
  SSE-KMS: KMS request charges, possible throttling
  SSE-C  : None, but you must manage keys

TYPICAL USE
  SSE-S3 : Default encryption
  SSE-KMS: Compliance, key rotation, separation of duties
  SSE-C  : Strict requirement to hold your own keys

In short: SSE-S3 is automatic, SSE-KMS adds control and
auditability, and SSE-C puts key custody entirely on you.
If you lose an SSE-C key, the data is unrecoverable.

