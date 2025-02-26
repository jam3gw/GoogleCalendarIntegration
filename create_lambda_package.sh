#!/bin/bash
# Script to create AWS Lambda deployment package

# Exit on error
set -e

echo "Creating AWS Lambda deployment package..."

# Create a temporary directory for the package
PACKAGE_DIR="lambda_package"
mkdir -p $PACKAGE_DIR

# Copy the necessary Python files
echo "Copying Python files..."
cp lambda_function.py $PACKAGE_DIR/
cp lambda_calendar_api.py $PACKAGE_DIR/
cp calendar_analysis_local.py $PACKAGE_DIR/

# Create a virtual environment for dependencies
echo "Creating virtual environment..."
python -m venv lambda_venv
source lambda_venv/bin/activate

# Install dependencies in the virtual environment
echo "Installing dependencies..."
pip install -r requirements.txt
pip install boto3  # AWS SDK for Python

# Copy the dependencies to the package directory
echo "Copying dependencies..."
cp -r lambda_venv/lib/python*/site-packages/* $PACKAGE_DIR/

# Create the ZIP file
echo "Creating ZIP file..."
cd $PACKAGE_DIR
zip -r ../lambda_deployment_package.zip .
cd ..

# Clean up
echo "Cleaning up..."
rm -rf $PACKAGE_DIR
rm -rf lambda_venv

echo "Deployment package created: lambda_deployment_package.zip"
echo "You can now upload this ZIP file to AWS Lambda."
echo ""
echo "IMPORTANT: Remember to set the following environment variables in your Lambda function:"
echo "- GOOGLE_CREDENTIALS_JSON: Base64-encoded credentials.json content"
echo "- GOOGLE_TOKEN_JSON: Base64-encoded token.json content (optional)"
echo "- TOKEN_PARAMETER_NAME: Name of the Parameter Store parameter for token storage (optional)" 