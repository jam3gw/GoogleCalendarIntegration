# Google Calendar Integration - AWS CDK Deployment Guide

This guide provides detailed instructions for deploying the Google Calendar Integration application to AWS Lambda using the AWS Cloud Development Kit (CDK) with TypeScript.

## Overview

The CDK project in this repository defines the following AWS resources:

1. **Lambda Function**: Runs the Google Calendar integration code
2. **API Gateway**: Provides HTTP endpoints to trigger the Lambda function
3. **IAM Role**: Grants the Lambda function necessary permissions
4. **Parameter Store Parameters**: Securely stores Google OAuth credentials

## Prerequisites

Before you begin, ensure you have the following installed:

- [AWS CLI](https://aws.amazon.com/cli/) installed and configured with appropriate credentials
- [Node.js](https://nodejs.org/) (>= 14.x)
- [AWS CDK](https://aws.amazon.com/cdk/) installed globally (`npm install -g aws-cdk`)
- [TypeScript](https://www.typescriptlang.org/) installed globally (`npm install -g typescript`)
- Python 3.9 or later

## Step 1: Initialize the Project Structure

Run the setup script to create the necessary directory structure:

```bash
./setup_cdk_project.sh
```

This script will:
- Create the required directories for the CDK project
- Copy the Lambda function files to the `lambda-package` directory
- Make the Lambda package creation script executable

## Step 2: Prepare the Lambda Package

Create the Lambda deployment package by running:

```bash
./create_lambda_package.sh
```

This will:
- Create a virtual environment
- Install the required Python dependencies
- Package everything into the `lambda-package` directory

## Step 3: Set Up the CDK Project

Navigate to the CDK project directory and install dependencies:

```bash
cd cdk
npm install
```

## Step 4: Build the TypeScript Code

Compile the TypeScript code to JavaScript:

```bash
npm run build
```

## Step 5: Bootstrap Your AWS Environment

If you haven't already bootstrapped your AWS environment for CDK, run:

```bash
cdk bootstrap
```

This command creates the necessary resources in your AWS account to deploy CDK stacks.

## Step 6: Deploy the Stack

Deploy the CDK stack to your AWS account:

```bash
cdk deploy
```

During deployment, you'll be prompted to confirm the creation of IAM resources. Review the changes and approve them.

After successful deployment, the CDK will output:
- The API Gateway URL
- The Lambda function name

## Step 7: Configure Google Calendar Credentials

Before using the deployed application, you need to store your Google Calendar credentials in AWS Parameter Store:

1. Store your Google OAuth tokens:

```bash
aws ssm put-parameter --name "/google-calendar-integration/token" --type "SecureString" --value "YOUR_TOKEN_JSON"
```

2. Store your Google client secrets:

```bash
aws ssm put-parameter --name "/google-calendar-integration/client_secrets" --type "SecureString" --value "YOUR_CLIENT_SECRETS_JSON"
```

Replace `YOUR_TOKEN_JSON` and `YOUR_CLIENT_SECRETS_JSON` with your actual Google OAuth token and client secrets JSON.

## Step 8: Test the Deployment

Test your deployed API using curl or a web browser:

```bash
curl https://xxxxxxxxxx.execute-api.region.amazonaws.com/prod/calendar/analyze
```

Replace the URL with the actual API Gateway URL from the CDK output.

## Modifying the Deployment

If you need to make changes to the deployment:

1. Edit the CDK code in the `cdk/lib/google-calendar-lambda-stack.ts` file
2. Rebuild the TypeScript code: `npm run build`
3. Deploy the updated stack: `cdk deploy`

## Cleaning Up

To remove all resources created by this CDK stack:

```bash
cdk destroy
```

## Troubleshooting

### Common Issues

1. **Lambda Function Errors**:
   - Check CloudWatch Logs for the Lambda function
   - Verify that the Google Calendar credentials are correctly stored in Parameter Store

2. **API Gateway Issues**:
   - Ensure the API Gateway is properly configured to integrate with the Lambda function
   - Check the API Gateway logs in CloudWatch

3. **Permission Issues**:
   - Verify that the Lambda function has the necessary IAM permissions
   - Check that the Parameter Store parameters are accessible to the Lambda function

### Useful Commands

* `npm run build` - Compile TypeScript to JavaScript
* `npm run watch` - Watch for changes and compile
* `npm run test` - Perform the Jest unit tests
* `cdk deploy` - Deploy the stack to your default AWS account/region
* `cdk diff` - Compare deployed stack with current state
* `cdk synth` - Emit the synthesized CloudFormation template

## Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
- [AWS Systems Manager Parameter Store Documentation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) 