"""
Exercise 2: SQS → Lambda → S3

Setup

Create a standard SQS queue etl-queue, and a bucket etl-output.
Create the Lambda (process-etl-messages). Its role needs 
AWSLambdaSQSQueueExecutionRole (managed policy) plus s3:GetObject and 
s3:PutObject on etl-output/*.
Add an SQS trigger on etl-queue with batch size 10.
Set the queue’s visibility timeout to at least 6× the Lambda timeout.

S3 has no append operation, so this version writes each batch as its own
 object. That avoids race conditions between concurrent Lambda invocations.


"""


python
import json, uuid
import boto3
from datetime import datetime, timezone

s3 = boto3.client("s3")
BUCKET = "etl-output"

def lambda_handler(event, context):
    valid, failures = [], []

    for record in event["Records"]:
        try:
            valid.append(json.loads(record["body"]))
        except json.JSONDecodeError:
            failures.append({"itemIdentifier": record["messageId"]})

    if valid:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        key = f"valid_records/{ts}_{uuid.uuid4().hex[:8]}.json"
        s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(valid))

    # Requires "Report batch item failures" enabled on the trigger
    return {"batchItemFailures": failures}


"""

If your exercise strictly requires a single valid_records.json, 
read the existing file, extend the list, and write it back. 
Set the function’s reserved concurrency to 1 so two invocations 
can’t overwrite each other.

Test:
aws sqs send-message --queue-url <queue-url> --message-body '{"id":1,"name":"Ada"}'
"""