"""
Exercise 1: S3 → Lambda (CSV validation)

Setup

Create the bucket, then upload customers.csv to the customers/ prefix.
Create the Lambda (validate-customers) with an execution role that allows s3:GetObject and s3:PutObject on the bucket, plus the basic CloudWatch Logs policy.
Add an S3 trigger: event type All object create events, prefix customers/, suffix .csv.

The prefix filter matters. Errors are written to errors/ in the same bucket, so without it the Lambda would trigger itself in a loop.


"""


import csv, io, urllib.parse
import boto3

s3 = boto3.client("s3")
REQUIRED = ["customer_id", "email"]

def lambda_handler(event, context):
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(body))

        bad_rows = []
        for row in reader:
            if any(not (row.get(col) or "").strip() for col in REQUIRED):
                bad_rows.append(row)

        if bad_rows:
            out = io.StringIO()
            writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(bad_rows)
            err_key = "errors/" + key.split("/")[-1].replace(".csv", "_errors.csv")
            s3.put_object(Bucket=bucket, Key=err_key, Body=out.getvalue())
            print(f"{len(bad_rows)} invalid rows -> s3://{bucket}/{err_key}")
        else:
            print("All rows valid")
    return {"status": "done"}
