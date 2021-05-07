This SaaS template allows quickly test an web app idea without any investments into infrastructure with the help of AWS Free Tier 

It uses these serverless services:
- AWS Lambda runtime
- API Gateway for HTTP(s) proxy
- DynamoDB in on-demand mode for storage
- AWS SES as email provider
- Stripe for payments
- Cloudformation and Codepipeline for infrastructure-as-a-code

It runs on:
- Python 3.8
- Flask
- Zappa (converts Flask to AWS Lambda)
- Bootstrap 4 for server-side rendered frontend

## Features:
- user management (registration, activation, password reset, login)
- transactional email (registration activation, password reset) 

## Change log:

06.05.2021
- Basic Flask app
- authentication blueprint for user registration, login, password reset

ToDo
- Cloudformation templates for AWS resources
- Cloudformation templates for Codepipeline CI/CD
- Stripe payments
- Convert project to cookie-cutter template
- admin space 
- Deploy guide

Contact me on [LinkedIn](https://www.linkedin.com/in/smirnovam/) if you are interested in using this template for your SaaS MVP


