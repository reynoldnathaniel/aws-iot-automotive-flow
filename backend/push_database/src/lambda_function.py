import json
import base64

def handler(event, context):
    
    #print the event object received by Lambda
    print(json.dumps(event, sort_keys=True, indent=4))
    print()
    
    # decode the message received in base 64
    data_base64 = event["Records"][0]["kinesis"]["data"]
    decoded_data = base64.b64decode(data_base64)
    decoded_str = decoded_data.decode("ascii") 
    print(json.loads(decoded_str))

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }