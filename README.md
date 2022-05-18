# AWS Lambda - AzureAD - User Check
A simple Lambda to check if a provided user exists in a configured AzureAD

AzureAD requirements:
* AppRegistration with the permission ```User.Read.All````
* ClientSecret

### Used AWS Services

* AWS Lambda

## Implementation guide

Please follow all the steps below to deploy the solution.

### Requirements

* Serverless (tested with version 3.17.0)
### Deployment

1. Create the AzureAD app registration with the permission ```User.Read.All```` (with permission type = application)
2. Create a ClientSecret in your app registration
2. Clone this repository
3. Edit the custom parameters in the serverless.yml
4. run ```sls deploy``` to deploy the solution

### Undeploy

1. run ```sls remove``` to remove the solution

### Local development

You can invoke your function locally by using the following command:

```bash
serverless invoke local --function user-check --data '{"username":"yourmail@provider.com"}'
```