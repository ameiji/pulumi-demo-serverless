
#  Pulumi serverless demo workshop
The repo contains practical part for Pulumi serverless demo workshop. The work shop is authored by Dmitry Sarkisov and Pavel Salnikov

### How to setup environment
Please consider, this project was developed on MacOS and never been intended to run on Windows. However you can try to use WSL subsystem and try to run the code in windows environment on your own risk
Also consider the project was developed for demonstration purposes. So we decided to use a local stack for it. Please use a reliable stack storage like s3 or pulumi cloud for production environment

 1. Setup pulumi. You can use any package manager of your choice (eg brew), but it is recommended to use [binary download](https://www.pulumi.com/docs/install/)
	 -  Decompress the archive
	 - Set PULUMI_PATH environment variable. Otherwise your system pulumi installation will be used
```export PULUMI_PATH=/your/path/to/pulumi/binary```
2. Please change values in a stack config file (Pulumi.aws-serverless-app.yaml):
	- aws:region. Set your aws region
	- aws:profile. Set your AWS profile. We are assume you have set up your AWS profile credentials already
	- aws:allowedAccountIds. This is the list of allowed AWS accounts. It is used to prevent accidental deployment of the code to a wrong AWS account. Place your AWS account Id here
	- aws:defaultTags. Change the "Owner" field
    - cognitoDomain: for Cognito auth to work we need to define an unique domain name. Modify this string if you recieve errors from pulumi regarding Cognito auth pool domain.
	- If you are using DefaultBoundaryPolicy for the account then set your account id in the policy's ARN. Comment the policy statement otherwise

### Deploy the project

#### Makefile
Initialize the project
```
    make stack-init
```

Build backend and frontend code and run pulumi up using:
```
    make all
```

#### Step-by-step
```
cd ./aws-serverless-app
```

For your convenience we have prepared a couple of scripts to deploy stack and destroy it.
```
./stack-up.sh
./stack-down.sh
```

Under the hood, general deployment workflow sequence is:
1. Login to local environment
```
	pulumi logout && pulumi login --local
```
2. Init and select stack
```
	pulumi stack init
	pulumi stack select aws-serverless-app
```
3. Preview deployment
```
pulumi preview
```
4. Build backend
```
	./build-backend.sh
```
5. Deploy project
```
	pulumi up
```
6. Build frontend
```
	./build-frontend.sh
```
7. Deploy project
```
	pulumi up
```
8. Go to the web ui of the application (available in outputs)

### Clean up
To clean up provisioned cloud resources use:
```
    make destroy
```
or 
```
    cd aws-serverless-app
    pulumi destroy
```