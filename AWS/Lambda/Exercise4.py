"""
Exercise 4: Scheduled Lambda → SNS alert

Setup

- Create an SNS topic etl-alerts and subscribe your email 
(confirm the subscription).

- Create the Lambda (check-daily-data) with s3:ListBucket on the bucket 
and sns:Publish on the topic. Add environment variables BUCKET, PREFIX, 
and TOPIC_ARN.

- Create an EventBridge rule with schedule cron(0 0 * * ? *) and target 
the Lambda. In EventBridge Scheduler you can also set your time zone.
Rules use UTC, so midnight UTC is 8 PM Eastern in summer.
"""
import os
import boto3
from datetime import datetime, timezone, timedelta

s3 = boto3.client("s3")
sns = boto3.client("sns")

BUCKET = os.environ["BUCKET"]
PREFIX = os.environ.get("PREFIX", "")
TOPIC_ARN = os.environ["TOPIC_ARN"]

def lambda_handler(event, context):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    found = False

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
        for obj in page.get("Contents", []):
            if obj["LastModified"] >= cutoff and not obj["Key"].endswith("/"):
                found = True
                break
        if found:
            break

    if not found:
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject="ETL Alert: no new data",
            Message=f"No new files in s3://{BUCKET}/{PREFIX} in the last 24 hours.",
        )
        return {"status": "alert_sent"}

    return {"status": "data_present"}

"""
Common gotchas
- Permissions: most “it didn’t trigger” problems are missing IAM permissions.
 Check CloudWatch Logs for the function first.
- Timeouts: the default Lambda timeout is 3 seconds. Raise it to 30-60 
seconds for CSV processing.
- Large CSVs: for files over a few hundred MB, stream with iter_lines() 
on the S3 body instead of reading it all into memory.
- Testing: use the console’s Test tab with a sample S3 event (the s3-put
 template) to debug before wiring up the real trigger.

I can also write these as CloudFormation/SAM templates or CLI scripts, 
or expand any one into a more production-style version (DLQs, retries, 
tests).
"""