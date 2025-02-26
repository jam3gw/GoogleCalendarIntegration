import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as GoogleCalendarLambda from '../lib/google-calendar-lambda-stack';

test('Lambda Function Created', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new GoogleCalendarLambda.GoogleCalendarLambdaStack(app, 'MyTestStack');
    // THEN
    const template = Template.fromStack(stack);

    template.hasResourceProperties('AWS::Lambda::Function', {
        Runtime: 'python3.9',
        Handler: 'lambda_function.lambda_handler',
    });
});

test('API Gateway Created', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new GoogleCalendarLambda.GoogleCalendarLambdaStack(app, 'MyTestStack');
    // THEN
    const template = Template.fromStack(stack);

    template.resourceCountIs('AWS::ApiGateway::RestApi', 1);
    template.resourceCountIs('AWS::ApiGateway::Method', 1);
}); 