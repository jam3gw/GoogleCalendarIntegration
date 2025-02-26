#!/bin/bash

# Create directories
mkdir -p cdk/bin cdk/lib cdk/test lambda-package

# Copy Lambda files to lambda-package
cp lambda_function.py lambda_calendar_api.py lambda-package/

# Make sure the script is executable
chmod +x create_lambda_package.sh

echo "CDK project structure initialized!"
echo "Next steps:"
echo "1. cd cdk"
echo "2. npm install"
echo "3. npm run build"
echo "4. Run ../create_lambda_package.sh to prepare the Lambda package"
echo "5. cdk bootstrap (if not already bootstrapped)"
echo "6. cdk deploy" 