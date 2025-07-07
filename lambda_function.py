import boto3
import os
import http.client
import base64
import ast

MWAA_ENV_NAME = os.environ['MWAA_ENV_NAME']
MWAA_DAG_MAPPING = {
    'rba/': 'partners_rba_v2',
    'endurance/': 'partners_endurance'
    # add more mappings
}
mwaa_cli_command = 'dags trigger'

client = boto3.client('mwaa')


def lambda_handler(event, context):
    
    #raise Exception("Intentional test failure for CloudWatch Alarm") #test case for cloudwatch alarm
    
    try:
        # Extract bucket + key
        s3_record = event['Records'][0]['s3']
        key = s3_record['object']['key']
        
        # Identify client folder
        for prefix, dag_id in MWAA_DAG_MAPPING.items():
            if key.startswith(prefix):
                trigger_dag(dag_id)
                print(f"status: DAG {dag_id} was triggered")
            else:
                print(f"status: DAG {dag_id} was not triggered this time")
    
    except Exception as e:
        print("Error triggering DAG:", str(e))

def trigger_dag(dag_id):
    # get web token
    mwaa_cli_token = client.create_cli_token(
        Name=MWAA_ENV_NAME
    )

    conn = http.client.HTTPSConnection(mwaa_cli_token['WebServerHostname'])
    payload = mwaa_cli_command + " " + dag_id
    headers = {
      'Authorization': 'Bearer ' + mwaa_cli_token['CliToken'],
      'Content-Type': 'text/plain'
    }
    conn.request("POST", "/aws_mwaa/cli", payload, headers)
    res = conn.getresponse()
    data = res.read()
    dict_str = data.decode("UTF-8")
    mydata = ast.literal_eval(dict_str)
    return base64.b64decode(mydata['stdout'])