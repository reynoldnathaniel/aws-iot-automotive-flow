from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_stepfunctions as stepfunctions,
    aws_stepfunctions_tasks as tasks,
    aws_logs as logs,
    aws_lambda as _lambda,
    aws_kinesis as kinesis,
    aws_dynamodb as dynamodb,
    aws_iam as iam
)

import aws_cdk.aws_lambda_event_sources as LambdaEventSources


memory_size = 128
lambda_timeout = Duration.seconds(10)

class PushDatabaseStepFunction(Stack):

    def __init__(self, scope: Construct, construct_id: str, dynamodb_table: dynamodb.Table, kinesis_stream: kinesis.Stream, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define a cloudwatch log group for Step Function logs
        step_function_log_group = logs.LogGroup(self, "StepFunctionLogGroup", log_group_name="PushDatabaseExpressStepFunction" )
        
        # Define a Stepfunction task for calling DynamoDB PutItem API
        dynamo_put_item_task = tasks.DynamoPutItem(self, "DynamoDB Put Item Task",
            item={
                    "timestamp": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.timestamp")),
                    "VIN" : tasks.DynamoAttributeValue.from_string(stepfunctions.JsonPath.string_at("$.VIN")),
                    "tripId": tasks.DynamoAttributeValue.from_string(stepfunctions.JsonPath.string_at("$.trip_id")),
                    "brake": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.brake")),
                    "steeringWheelAngle": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.steeringWheelAngle")),
                    "torqueAtTransmission": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.torqueAtTransmission")),
                    "engineSpeed": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.engineSpeed")),
                    "vehicleSpeed": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.vehicleSpeed")),
                    "acceleration": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.acceleration")),
                    "parkingBrakeStatus": tasks.DynamoAttributeValue.from_string(stepfunctions.JsonPath.string_at("$.parkingBrakeStatus")),
                    "brakePedalStatus": tasks.DynamoAttributeValue.from_string(stepfunctions.JsonPath.string_at("$.brakePedalStatus")),
                    "transmissionGearPosition": tasks.DynamoAttributeValue.from_string(stepfunctions.JsonPath.string_at("$.transmissionGearPosition")),
                    "gearLeverPosition": tasks.DynamoAttributeValue.from_string(stepfunctions.JsonPath.string_at("$.gearLeverPosition")),
                    "odometer":  tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.odometer")),
                    "ignitionStatus": tasks.DynamoAttributeValue.from_string(stepfunctions.JsonPath.string_at("$.ignitionStatus")),
                    "fuelLevel": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.fuelLevel")),
                    "fuelConsumedSinceRestart": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.fuelConsumedSinceRestart")),
                    "oilTemp": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.oilTemp")),
                    "latitude": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.latitude")),
                    "longitude": tasks.DynamoAttributeValue.number_from_string(stepfunctions.JsonPath.string_at("$.longitude")),

                },
            table=dynamodb_table
        )

        # A state machine definition that has a Choice state inside to make a desision base of input 
        state_machine_definition = stepfunctions.Choice(self, "Choice for pushing database").\
        when(stepfunctions.Condition.is_not_null("$"), dynamo_put_item_task)

        # Define Express Step function that is exceuted when Rest api endpoint are called
        state_machine = stepfunctions.StateMachine(self, "StateMachine",
            state_machine_name="push_database_execution_state_machine",
            definition=state_machine_definition,
            state_machine_type=stepfunctions.StateMachineType.EXPRESS,
            tracing_enabled=True,
            logs=stepfunctions.LogOptions(
                destination=step_function_log_group,
                level=stepfunctions.LogLevel.ALL,
                include_execution_data=True)
            )
        # Lambda function 
        push_dynamodb_lambda = _lambda.Function(
            self, 
            id='IoTInsertDatabaseFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('backend/push_db_step_function/src/push_dynamodb'),
            handler='lambda_function.handler',
            architecture= _lambda.Architecture.ARM_64,
            timeout = lambda_timeout,
            tracing = _lambda.Tracing.ACTIVE,
            memory_size = memory_size

        )
        

        step_function_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[state_machine.state_machine_arn],
            actions=["states:StartExecution", "states:StartSyncExecution"]
        )
        push_dynamodb_lambda.add_to_role_policy(step_function_policy)

        push_dynamodb_lambda.add_environment('step_function_arn', state_machine.state_machine_arn)

        push_dynamodb_lambda.add_event_source(LambdaEventSources.KinesisEventSource(kinesis_stream,
            batch_size=100, 
            starting_position=_lambda.StartingPosition.TRIM_HORIZON
        ))