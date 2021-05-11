This SaaS template allows quickly test a web app idea without any investments into infrastructure with the help of AWS Free Tier 

It uses these serverless services:
- AWS Lambda + API Gateway to serve the app
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
- transactional email (registration activation, password reset, payment problems, trial period end) 
- admin page to show monthly recurrent revenue (MMR), monthly active users (MAU), churn rate
- easy setup with extensive Deploy Guide that also includes steps to tailor the app to your needs

## Change log:
11.05.2021
- Fetching prices and products from Stripe
- checkout session stripe hook and redirect

06.05.2021
- Basic Flask app
- Authentication blueprint for user registration, login, password reset


Contact me on [LinkedIn](https://www.linkedin.com/in/smirnovam/) if you are interested in using this template for your SaaS MVP


