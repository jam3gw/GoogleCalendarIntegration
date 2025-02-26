import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as path from 'path';

export class GoogleCalendarLambdaStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Create a role for the Lambda function with permissions to access SSM Parameter Store
        const lambdaRole = new iam.Role(this, 'GoogleCalendarLambdaRole', {
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
                iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMReadOnlyAccess')
            ]
        });

        // Define the Lambda function
        const calendarLambda = new lambda.Function(this, 'GoogleCalendarFunction', {
            runtime: lambda.Runtime.PYTHON_3_9,
            handler: 'lambda_function.lambda_handler',
            code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda-package')), // Path to your Lambda package
            timeout: cdk.Duration.seconds(30),
            memorySize: 256,
            role: lambdaRole,
            environment: {
                // Environment variables for the Lambda function
                'PARAMETER_STORE_PREFIX': '/google-calendar-integration/'
            }
        });

        // Create an API Gateway REST API
        const api = new apigateway.RestApi(this, 'GoogleCalendarApi', {
            restApiName: 'Google Calendar Integration API',
            description: 'API for Google Calendar Integration',
            deployOptions: {
                stageName: 'prod'
            }
        });

        // Add a resource and method to the API
        const calendarResource = api.root.addResource('calendar');
        const analyzeResource = calendarResource.addResource('analyze');

        // Add GET method to the analyze resource
        analyzeResource.addMethod('GET', new apigateway.LambdaIntegration(calendarLambda, {
            proxy: true
        }));

        // Output the API Gateway URL
        new cdk.CfnOutput(this, 'ApiUrl', {
            value: api.url,
            description: 'URL of the API Gateway endpoint'
        });

        // Output the Lambda function name
        new cdk.CfnOutput(this, 'LambdaFunctionName', {
            value: calendarLambda.functionName,
            description: 'Name of the Lambda function'
        });
    }
} 