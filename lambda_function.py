import json
import boto3
import csv
import io
from datetime import datetime

s3 = boto3.client('s3')
ses = boto3.client('ses', region_name='YOUR_AWS_REGION')

SENDER_EMAIL = 'YOUR_VERIFIED_SENDER_EMAIL'
RECIPIENT_EMAIL = 'YOUR_VERIFIED_RECIPIENT_EMAIL'

REQUIRED_COLUMNS = {'shipment_id', 'supplier', 'destination', 'items', 'weight_kg', 'status', 'expected_delivery'}

def lambda_handler(event, context):
    try:
        # Extract bucket and file info from SQS message
        body = json.loads(event['Records'][0]['body'])
        s3_record = body['Records'][0]['s3']
        bucket = s3_record['bucket']['name']
        key = s3_record['object']['key']

        print(f"Processing file: s3://{bucket}/{key}")

        # Fetch CSV from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))

        # Validate columns
        actual_columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - actual_columns
        if missing:
            print(f"Validation failed. Missing columns: {missing}")
            return {'statusCode': 400, 'body': f'Missing columns: {missing}'}

        # Process rows
        rows = list(reader)
        total = len(rows)
        total_items = sum(int(r['items']) for r in rows)
        total_weight = sum(float(r['weight_kg']) for r in rows)

        today = datetime.utcnow().date()
        delayed = [
            r for r in rows
            if r['status'].strip().lower() == 'delayed'
            and datetime.strptime(r['expected_delivery'], '%Y-%m-%d').date() < today
        ]

        # Build email
        delayed_rows_html = ''.join(
            f"<tr><td>{r['shipment_id']}</td><td>{r['supplier']}</td><td>{r['destination']}</td><td>{r['expected_delivery']}</td></tr>"
            for r in delayed
        )

        html_body = f"""
        <html><body style="font-family:Arial,sans-serif;padding:20px;">
        <h2>📦 Shipment Manifest Summary</h2>
        <p><strong>File:</strong> {key}</p>
        <table border="1" cellpadding="8" cellspacing="0">
            <tr><td><strong>Total Shipments</strong></td><td>{total}</td></tr>
            <tr><td><strong>Total Items</strong></td><td>{total_items}</td></tr>
            <tr><td><strong>Total Weight</strong></td><td>{total_weight:.1f} kg</td></tr>
            <tr><td><strong>Delayed Shipments</strong></td><td>{len(delayed)}</td></tr>
        </table>

        {'<h3>⚠️ Flagged Delayed Shipments</h3><table border="1" cellpadding="8" cellspacing="0"><tr><th>ID</th><th>Supplier</th><th>Destination</th><th>Expected</th></tr>' + delayed_rows_html + '</table>' if delayed else '<p>✅ No delayed shipments.</p>'}

        </body></html>
        """

        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [RECIPIENT_EMAIL]},
            Message={
                'Subject': {'Data': f'Shipment Manifest Report — {key}'},
                'Body': {'Html': {'Data': html_body}}
            }
        )

        print("Email sent successfully.")
        return {'statusCode': 200, 'body': 'Done'}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise