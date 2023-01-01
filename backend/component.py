from aws_cdk import (
    Stack
)
import os
import aws_cdk as cdk
from constructs import Construct

from backend.iot_kinesis_stream.infrastructure import IoTKinesisStream
from backend.database.infrastructure import DatabaseIoT
from backend.push_db_step_function.infrastructure import PushDatabaseStepFunction

class Backend(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        iot_kinesis_stream = IoTKinesisStream(self, "IoTKinesisStream",
            # If you don't specify 'env', this stack will be environment-agnostic.
            # Account/Region-dependent features and context lookups will not work,
            # but a single synthesized template can be deployed anywhere.

            # Uncomment the next line to specialize this stack for the AWS Account
            # and Region that are implied by the current CLI configuration.

            env = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
        )
        database = DatabaseIoT(self, "DatabaseIoT",
            # If you don't specify 'env', this stack will be environment-agnostic.
            # Account/Region-dependent features and context lookups will not work,
            # but a single synthesized template can be deployed anywhere.

            # Uncomment the next line to specialize this stack for the AWS Account
            # and Region that are implied by the current CLI configuration.

            env = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
        )
        PushDatabaseStepFunction(self, "PushDatabaseStepFunction",
            dynamodb_table = database.automotive_table,
            kinesis_stream = iot_kinesis_stream.stream,
            # If you don't specify 'env', this stack will be environment-agnostic.
            # Account/Region-dependent features and context lookups will not work,
            # but a single synthesized template can be deployed anywhere.

            # Uncomment the next line to specialize this stack for the AWS Account
            # and Region that are implied by the current CLI configuration.

            env = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
        )
