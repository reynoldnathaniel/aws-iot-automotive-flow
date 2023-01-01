from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_stepfunctions as stepfunctions,
    aws_stepfunctions_tasks as tasks,
    aws_dynamodb as dynamodb,
    aws_logs as logs
)

class DatabaseIoT(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a DynamoDB table for IoT Automotive
        self.automotive_table = dynamodb.Table(self, "AutomotiveTable", table_name="AutomotiveTable",
            partition_key = dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.NUMBER),
            sort_key = dynamodb.Attribute(name="VIN", type=dynamodb.AttributeType.STRING),
            billing_mode = dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption = dynamodb.TableEncryption.AWS_MANAGED,
        )
        
        