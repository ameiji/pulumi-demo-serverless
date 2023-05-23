// You can obtain these values by running:
// aws cloudformation describe-stacks --stack-name <YOUR STACK NAME> --query "Stacks[0].Outputs[]"

const config = {
  "aws_user_pools_web_client_id": "eu-west-1_GKAB5SLp1",     // CognitoClientID
  "api_base_url": "https://wei0nwxrn7.execute-api.eu-west-1.amazonaws.com/demo",                                     // TodoFunctionApi
  "cognito_hosted_domain": "mytodoappdemo-demo-dsarkisov.auth.eu-west-1.amazoncognito.com",                   // CognitoDomainName
  "redirect_url": "todoapifrontendbucket-0f1d5cc.s3-website-eu-west-1.amazonaws.com"                                      // AmplifyURL
};

export default config;
