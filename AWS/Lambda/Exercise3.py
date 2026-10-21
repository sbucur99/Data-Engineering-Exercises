
"""

Exercise 3: S3 → Lambda → Glue job

Setup

- Create the Glue job transform_raw_data (Glue Studio → Script editor, 
or Visual). It needs an IAM role with AWSGlueServiceRole plus S3 access 
to your raw and output locations.

- Create the Lambda (trigger-glue-job) with glue:StartJobRun on the job’s
ARN.

- Add an S3 trigger on the raw bucket with a prefix such as raw/. 
Keep the Glue output on a different prefix or bucket, or it will 
re-trigger.
"""

import urllib.parse
import boto3

glue = boto3.client("glue")
JOB_NAME = "transform_raw_data"

def lambda_handler(event, context):
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        response = glue.start_job_run(
            JobName=JOB_NAME,
            Arguments={"--input_path": f"s3://{bucket}/{key}"},
        )
        print(f"Started {JOB_NAME}: {response['JobRunId']}")
    return {"status": "started"}

Inside the Glue script, read the argument with getResolvedOptions(sys.argv, ["JOB_NAME", "input_path"]). If many files arrive at once, you may hit the job’s max concurrent runs limit (default 1). Raise it under the job’s details, or Glue will throw ConcurrentRunsExceededException.
