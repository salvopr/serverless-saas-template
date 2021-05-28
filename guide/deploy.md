Deploy
1. Register domain with Route 53
   its simpler down the road
   

1. S3 bucket for ENV variables (and secrets)

aws s3 mb s3://mysaas-env

>> Note about globality of S3 bucket names

2. Get key from stripe (screenshots)

3. Set up Stripe payment plans

3. Generate secret key for your app
   

4. Create JSON file with ENV variables and STRIPE keys

{
"USERS_TABLE": "mysaas-users-prod",
"AUTH_TOKENS_TABLE": "mysaas-tokens-prod",
"EVENT_TABLE": "mysaas-events-prod",
"DOMAIN": "demo.easysaasboilerplate.com",
"STRIPE_PUB_KEY": "pk_test_123",
"STRIPE_SEC_KEY": "sk_test_123",
"STRIPE_ENDPOINT_KEY": "whsec_123",
"SECRET_KEY": "WV++++"
}

>> Note about storing secrect separate from the code

5. Put JSON files on S3 with secrets
   aws s3 cp prod.json s3://mysaas-env

6. Change the params in zappa_settings.json
   
   remote_env to "s3://mysaas-env/prod.json",
   s3_bucket
   aws_region
   and environment_variables -> AWS_REGION

7. Tables

aws cloudformation create-stack --template-body file://./aws/tables.yaml --stack-name mysaas-tables-prod --region us-east-1 --parameters ParameterKey=Name,ParameterValue=mysaas ParameterKey=Env,ParameterValue=prod


8. Create virtual env

9. Install dependencies

10. Deploy
 zappa deploy prod
    
11. Create certificate

11 Connect domain 

13. Connect SES

14. Register your self and setup yourself as a platform admin



