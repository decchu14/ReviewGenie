# ReviewGenie

A Code Review Service that automatically analyzes code changes in a GitLab Merge Request (MR) using AI.

🧠 AI Code Review Service — Simple Architecture Overview
We have built a Code Review Service that automatically analyzes code changes in a GitLab Merge Request (MR) using AI. The system is made of 3 independent services, each doing a specific job:

🟡 1. GitLab Webhook Listener (Trigger Service)

    - This service is triggered when a Merge Request (MR) is created in GitLab.
    - We have set up a GitLab Webhook that sends MR details to an AWS Lambda function. - The Lambda function reads the incoming JSON and extracts:
        - MR ID
        - Project ID
        - Action (like open, reopen, update, or merge)
    - If the action is one of these four (open, reopen, update, merge), it sends a message to AWS SQS with this information.
    - Input: MR event from GitLab
    - Output: Message in AWS SQS queue with MR details
