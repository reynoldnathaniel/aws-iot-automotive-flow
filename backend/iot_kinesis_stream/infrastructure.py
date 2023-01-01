from constructs import Construct
from aws_cdk import (
    Stack,
    aws_kinesis as kinesis,
    aws_lambda as _lambda,
    Duration
)

import aws_cdk.aws_iot_alpha as iot
import aws_cdk.aws_iot_actions_alpha as actions
import aws_cdk.aws_lambda_event_sources as LambdaEventSources

memory_size = 128
lambda_timeout = Duration.seconds(10)

class IoTKinesisStream(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Kinesis Data Stream
        self.stream = kinesis.Stream(self, "IotKinesisLambdaCdkStream")

        # IoT Rule with Kinesis Data Stream action
        topic_rule = iot.TopicRule(self, "IotKinesisLambdaCdkRule",
            sql=iot.IotSql.from_string_as_ver20160323("SELECT * FROM 'automotive-01'"),
            actions=[
                actions.KinesisPutRecordAction(self.stream,
                    partition_key="VIN"
                )
            ]
        )
        
        # Lambda function 
        iot_kinesis_lambda_sample = _lambda.Function(
            self, 
            id='IotKinesisLambdaSample',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('backend/iot_kinesis_stream/src'),
            handler='lambda_function.handler',
            architecture= _lambda.Architecture.ARM_64,
            timeout = lambda_timeout,
            tracing = _lambda.Tracing.ACTIVE,
            memory_size = memory_size

        )

        # Lambda Kinesis event source
        iot_kinesis_lambda_sample.add_event_source(LambdaEventSources.KinesisEventSource(self.stream,
            batch_size=100, 
            starting_position=_lambda.StartingPosition.TRIM_HORIZON
        ))