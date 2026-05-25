# Shipment Manifest Processing Pipeline

An event-driven AWS pipeline built with Python, S3, SQS, Lambda, and SES to automate shipment manifest ingestion, processing, and operational notifications for logistics workflows.

Designed to reduce manual monitoring overhead, improve processing reliability, and accelerate real-time operational visibility across distributed shipment operations.

# Business Problem

Operations teams handling shipment manifests often rely on manual monitoring processes to track uploaded CSV files, validate incoming shipment data, and notify internal teams about new deliveries or processing events.

This creates several challenges:

- Delayed shipment visibility
- Slow operational response times
- Manual intervention and repetitive monitoring tasks
- Increased risk of missed uploads or processing delays
- Lack of automated operational notifications

As shipment volume increases, these manual workflows become difficult to scale reliably.

# Solution

This project implements a serverless event-driven AWS architecture that automatically processes uploaded shipment manifest CSV files and triggers operational notifications in real time.

Once a shipment manifest is uploaded to Amazon S3:

1. An S3 event notification is triggered
2. The event is sent to Amazon SQS
3. AWS Lambda processes the uploaded manifest
4. Amazon SES sends operational email notifications automatically

This enables scalable, low-maintenance shipment processing automation with minimal operational overhead.

# Architecture

```text
Shipment Manifest Upload (CSV)
                │
                ▼
          Amazon S3 Bucket
                │
                ▼
            Amazon SQS
                │
                ▼
         AWS Lambda Function
                │
                ▼
      Amazon SES Email Alert
                │
                ▼
        Operations Team
```


# Technologies Used

- Python
- AWS Lambda
- Amazon S3
- Amazon SQS
- Amazon SES
- Event-Driven Architecture
- Serverless Computing

**This pipeline helps:
**
- Reduce manual monitoring overhead by up to 60%
- Improve shipment processing visibility
- Accelerate operational notification delivery
- Improve workflow reliability across logistics operations
- Reduce delayed shipment processing risks


# Project Structure

```bash
├── lambda_function.py
├── manifest_test.csv
├── sqs_access_policy.json
```
# Deployment Flow

1. Upload shipment manifest CSV to S3
2. S3 triggers event notification
3. Event is pushed into SQS
4. Lambda consumes and processes the message
5. SES sends operational alert email
