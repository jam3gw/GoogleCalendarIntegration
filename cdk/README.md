# Google Calendar Integration CDK

This project contains the AWS CDK infrastructure code for deploying the Google Calendar Integration application to AWS Lambda with API Gateway.

## Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) installed and configured
- [Node.js](https://nodejs.org/) (>= 14.x)
- [AWS CDK](https://aws.amazon.com/cdk/) installed (`npm install -g aws-cdk`)
- [TypeScript](https://www.typescriptlang.org/) installed (`npm install -g typescript`)
- Python 3.9 or later

## Setup

1. Install dependencies:

```bash
npm install
```

2. Build the TypeScript code:

```bash
npm run build
```

3. Prepare your Lambda package:

Before deploying, you need to create a Lambda deployment package. Run the `create_lambda_package.sh` script from the root directory:

```bash
cd ..
./create_lambda_package.sh
cd cdk
```

This will create a `lambda-package` directory in the root of your project with all the necessary files for the Lambda function.

## Deployment

1. Bootstrap your AWS environment (if you haven't already):

```bash
cdk bootstrap
```

2. Deploy the stack:

```bash
cdk deploy
```

3. After deployment, the CDK will output:
   - The API Gateway URL
   - The Lambda function name

## Configuration

Before using the deployed application, you need to store your Google Calendar credentials in AWS Parameter Store:

1. Store your Google OAuth tokens in Parameter Store:

```bash
aws ssm put-parameter --name "/google-calendar-integration/token" --type "SecureString" --value "YOUR_TOKEN_JSON"
```

2. Store your Google client secrets in Parameter Store:

```bash
aws ssm put-parameter --name "/google-calendar-integration/client_secrets" --type "SecureString" --value "YOUR_CLIENT_SECRETS_JSON"
```

## Usage

Once deployed, you can access your API at the URL provided in the CDK output:

```
https://xxxxxxxxxx.execute-api.region.amazonaws.com/prod/calendar/analyze
```

## Cleanup

To remove all resources created by this CDK stack:

```bash
cdk destroy
```

## Useful Commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template 