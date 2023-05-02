// You can obtain these values by running:
// aws cloudformation describe-stacks --stack-name <YOUR STACK NAME> --query "Stacks[0].Outputs[]"

const config = {
  "aws_user_pools_web_client_id": "52aa1kjic2qov77lust8e083j1",     // CognitoClientID
  "api_base_url": "https://4co7f9mc5l.execute-api.eu-west-1.amazonaws.com/prod",                                     // TodoFunctionApi
  "cognito_hosted_domain": "mytodoappdemo-demo-dsarkisov.auth.eu-west-1.amazoncognito.com",                   // CognitoDomainName
  "redirect_url": "https://master.d11aett0uxdeod.amplifyapp.com"                                      // AmplifyURL
};

export default config;
