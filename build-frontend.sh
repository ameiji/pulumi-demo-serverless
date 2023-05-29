#!/bin/bash


set -eux

gpulumi="$HOME/Downloads/pulumi/pulumi"


# Create build dir
BUILD_DIR=/tmp/build
mkdir -p "$BUILD_DIR"
rm -rf frontend-src/build
cp -rv frontend-src "$BUILD_DIR"

# Get stack outputs
$gpulumi stack output -j > pulumi_stack_output.json

AWS_USER_POOLS_WEB_CLIENT_ID=$( cat pulumi_stack_output.json | jq '.aws_user_pools_web_client_id')
API_BASE_URL=$( cat pulumi_stack_output.json | jq '.backend_invoke_url')
STAGE_NAME_PARAM=$( cat pulumi_stack_output.json | jq '.stage_name')
COGNITO_HOSTED_DOMAIN=$( cat pulumi_stack_output.json | jq '.cognito_custom_domain')
REDIRECT_URL=$( cat pulumi_stack_output.json | jq '.website_url')

rm pulumi_stack_output.json

# Copy config
pushd "$BUILD_DIR/frontend-src"
cp -fv src/config.default.js src/config.js

# Build React app
npm install

if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' -e 's/AWS_USER_POOLS_WEB_CLIENT_ID/'"$AWS_USER_POOLS_WEB_CLIENT_ID"'/g' src/config.js
  sed -i '' -e 's/API_BASE_URL/'"${API_BASE_URL//\//\\/}"'/g' src/config.js
  sed -i '' -e 's/{StageNameParam}/'"$STAGE_NAME_PARAM"'/g' src/config.js
  sed -i '' -e 's/COGNITO_HOSTED_DOMAIN/'"$COGNITO_HOSTED_DOMAIN"'/g' src/config.js
  sed -i '' -e 's/REDIRECT_URL/'"${REDIRECT_URL//\//\\/}"'/g' src/config.js
else
  sed -i -e 's/AWS_USER_POOLS_WEB_CLIENT_ID/'"$AWS_USER_POOLS_WEB_CLIENT_ID"'/g' src/config.js
  sed -i -e 's/API_BASE_URL/'"${API_BASE_URL//\//\\/}"'/g' src/config.js
  sed -i -e 's/{StageNameParam}/'"$STAGE_NAME_PARAM"'/g' src/config.js
  sed -i -e 's/COGNITO_HOSTED_DOMAIN/'"$COGNITO_HOSTED_DOMAIN"'/g' src/config.js
  sed -i -e 's/REDIRECT_URL/'"${REDIRECT_URL//\//\\/}"'/g' src/config.js
fi

npm run build
popd

# Copy sources
cp -rv "$BUILD_DIR/frontend-src/build" frontend-src/

echo "=> Build complete"
echo "=> Now you can run 'pulumi up' to upload frontend app sources to S3."

