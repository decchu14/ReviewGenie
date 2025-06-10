FROM public.ecr.aws/lambda/python:3.12

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY . .

# Set the Lambda handler
CMD ["lambda_function.lambda_handler"]
