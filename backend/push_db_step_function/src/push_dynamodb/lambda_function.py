import json
import base64
import os
import boto3
step_function_client = boto3.client('stepfunctions')

    
def handler(event, context):
    step_function_push_db_arn = os.environ['step_function_arn']
    #print the event object received by Lambda
    print(json.dumps(event, sort_keys=True, indent=4))
    print()
    
    # decode the message received in base 64
    
    for record in event["Records"]:
        data_base64 = record["kinesis"]["data"]
        decoded_data = base64.b64decode(data_base64)
        decoded_str = decoded_data.decode("ascii")
        json_decoded_str = json.loads(decoded_str)
        json_decoded_str['timestamp'] = str(record["kinesis"]["approximateArrivalTimestamp"])
        
        # Process location
        json_decoded_str['latitude'] = str(json_decoded_str['location']['latitude'])
        json_decoded_str['longitude'] = str(json_decoded_str['location']['longitude'])
        print(json_decoded_str)

        # Set all to string
        for key in json_decoded_str:
            if type(json_decoded_str[key]) is not str:
                json_decoded_str[key] = str(json_decoded_str[key])

    
        # Invoke Step Function
        response = step_function_client.start_execution(
            stateMachineArn = step_function_push_db_arn,
            input = json.dumps(json_decoded_str)
        )
    print('Successfully processed {} records.'.format(len(event['Records'])))
    return 'Successfully processed {} records.'.format(len(event['Records']))