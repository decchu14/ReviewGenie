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

🟢 2. Gen-AI Review Service (Code Analyzer)

    - This service runs as an AWS Lambda with a Docker image, which includes all AI-related dependencies and the Lambda handler.
    - It listens to SQS messages (produced by the first service).
    - When a new message arrives:
        - If the action is open, reopen, or update:
            -  Calls the GitLab API to fetch the MR code diffs (the files changed and the diff content).
            -  Passes each file’s diff through a Retrieval-Augmented Generation (RAG) pipeline:
            -  This pipeline uses a FAISS vector index of the default branch codebase (pre-built by embedding all source code files into vector embeddings via OpenAI embeddings).
            -  For each diff, the pipeline retrieves relevant code snippets from the indexed default branch code.
            -  It generates a detailed AI-powered code review that includes high-level analysis, security issue detection, code smells, suggestions for improvement, and future risk assessment.
        - If the action is merge:
            -  After the Merge Request is successfully merged into the default branch:
                -  Only the code that changed as part of the merge is identified.
                -  These changed files are re-embedded (i.e., reprocessed into vector representations using OpenAI embeddings).
                -  The updated embeddings are used to update the existing FAISS index:
                    - Old embeddings for changed files are removed or replaced.
                    - New chunks and their vectors are added to the FAISS index.
                - This ensures that the retrieval context used in future code reviews reflects the latest version of the codebase post-merge.
                - This process avoids full re-indexing and focuses only on what was modified in the merge, improving efficiency.
    - The final result is saved in DynamoDB, with:
        - MR ID
        - Project ID
        - Analysis – (AI-generated review text)
    - Input: Message from SQS
    - Output: Code review stored in DynamoDB under MRAnalysisResults table
