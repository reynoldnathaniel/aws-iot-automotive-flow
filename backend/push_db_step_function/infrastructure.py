from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_stepfunctions as stepfunctions,
    aws_stepfunctions_tasks as tasks,
    aws_dynamodb as dynamodb,
    aws_logs as logs
)

memory_size = 128
lambda_timeout = Duration.seconds(10)

class PushDatabaseStepFunction(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define a cloudwatch log group for Step Function logs
        step_function_log_group = logs.LogGroup(self, "StepFunctionLogGroup", log_group_name="PushDatabaseExpressStepFunction" )
        