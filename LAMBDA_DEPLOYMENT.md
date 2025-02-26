# Deploying Google Calendar Integration to AWS Lambda

This guide provides step-by-step instructions for deploying the Google Calendar Integration application to AWS Lambda.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Python 3.9+ installed
4. Google Calendar API credentials (credentials.json)
5. Valid Google Calendar API token (token.json)

## Preparation Steps

### 1. Authenticate with Google Calendar API Locally First

Before deploying to Lambda, you need to authenticate with Google Calendar API locally to generate a valid token:

```bash
# Run the local version of the application
python calendar_api.py
```

This will open a browser window for authentication and generate a `token.json` file.

### 2. Encode Credentials and Token

Lambda requires the credentials and token to be stored as environment variables. Encode them as Base64:

```bash
# Encode credentials.json
base64 -i credentials.json | tr -d '\n' > credentials_base64.txt

# Encode token.json
base64 -i token.json | tr -d '\n' > token_base64.txt
```

## Deployment Options

### Option 1: Manual Deployment via AWS Console

1. Create the deployment package:

```bash
# Make the script executable
chmod +x create_lambda_package.sh

# Run the script
./create_lambda_package.sh
```

2. In the AWS Console:
   - Go to Lambda service
   - Create a new function
   - Choose "Author from scratch"
   - Name: `GoogleCalendarAnalysis`
   - Runtime: Python 3.9
   - Architecture: x86_64
   - Click "Create function"

3. Upload the deployment package:
   - In the "Code" tab, click "Upload from" and select ".zip file"
   - Upload the `lambda_deployment_package.zip` file
   - Click "Save"

4. Configure environment variables:
   - In the "Configuration" tab, select "Environment variables"
   - Add the following variables:
     - `GOOGLE_CREDENTIALS_JSON`: Paste the content from credentials_base64.txt
     - `GOOGLE_TOKEN_JSON`: Paste the content from token_base64.txt
     - `TOKEN_PARAMETER_NAME`: (Optional) Name of the Parameter Store parameter for token storage

5. Configure function settings:
   - Timeout: 30 seconds (or more if needed)
   - Memory: 256 MB (increase if needed)

6. Configure permissions:
   - If using Parameter Store, add the `AmazonSSMReadOnlyAccess` policy to the Lambda execution role
   - If writing back to Parameter Store, add the `AmazonSSMFullAccess` policy

### Option 2: Deployment via AWS CLI

1. Create the deployment package:

```bash
./create_lambda_package.sh
```

2. Create the Lambda function:

```bash
aws lambda create-function \
  --function-name GoogleCalendarAnalysis \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_deployment_package.zip \
  --role arn:aws:iam::<YOUR_ACCOUNT_ID>:role/<YOUR_LAMBDA_ROLE> \
  --timeout 30 \
  --memory-size 256 \
  --environment "Variables={GOOGLE_CREDENTIALS_JSON=$(cat credentials_base64.txt),GOOGLE_TOKEN_JSON=$(cat token_base64.txt)}"
```

Replace `<YOUR_ACCOUNT_ID>` and `<YOUR_LAMBDA_ROLE>` with your AWS account ID and Lambda execution role.

## Setting Up API Gateway

To expose your Lambda function as an API:

1. In the AWS Console, go to API Gateway
2. Create a new REST API
3. Create a new resource (e.g., `/calendar-analysis`)
4. Create a GET method for the resource
5. Set the Integration type to "Lambda Function"
6. Select your Lambda function
7. Deploy the API to a stage (e.g., "prod")

## Testing the Deployment

You can test your Lambda function using the AWS Console or by making an HTTP request to your API Gateway endpoint:

```bash
curl "https://<API_ID>.execute-api.<REGION>.amazonaws.com/<STAGE>/calendar-analysis?days=7"
```

Replace `<API_ID>`, `<REGION>`, and `<STAGE>` with your API Gateway details.

## Troubleshooting

1. **Authentication Issues**: If you encounter authentication errors, ensure that:
   - The credentials and token are correctly encoded
   - The token is valid and not expired
   - The Lambda function has permission to access Parameter Store if used

2. **Timeout Errors**: If the function times out:
   - Increase the Lambda timeout setting
   - Optimize the code to reduce execution time

3. **Memory Issues**: If you encounter memory errors:
   - Increase the Lambda memory allocation

4. **Permission Issues**: If the function cannot access AWS services:
   - Check the Lambda execution role permissions
   - Ensure the role has the necessary policies attached

## Maintenance

1. **Token Refresh**: The Google Calendar API token may expire. Options for refreshing:
   - Store the token in Parameter Store and update it when refreshed
   - Periodically redeploy with a fresh token

2. **Monitoring**: Set up CloudWatch Alarms to monitor:
   - Error rates
   - Execution duration
   - Invocation count

3. **Logging**: Review CloudWatch Logs for detailed error information

## Security Considerations

1. **Credentials Protection**:
   - Use AWS Secrets Manager for more secure credential storage
   - Rotate credentials periodically

2. **API Access Control**:
   - Add authentication to your API Gateway (e.g., API keys, Cognito, Lambda authorizers)
   - Implement IP restrictions if appropriate

3. **Data Protection**:
   - Ensure sensitive calendar data is handled securely
   - Consider encrypting data at rest and in transit 