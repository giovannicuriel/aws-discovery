import boto3
import json

resource_map = {}

def update_resource_mapping(resource_type, resource_id, stack_id, status=None):
    if not resource_type in resource_map:
        resource_map[resource_type] = {}
    
    if not resource_id in resource_map[resource_type]:
        resource_map[resource_type][resource_id] = {}
    
    if not 'parent_stack' in resource_map[resource_type][resource_id]:
        resource_map[resource_type][resource_id]['parent_stack'] = stack_id
        resource_map[resource_type][resource_id]['resource_status'] = status    
    elif resource_map[resource_type][resource_id]['parent_stack'] is None:
        resource_map[resource_type][resource_id]['parent_stack'] = stack_id
        resource_map[resource_type][resource_id]['resource_status'] = status

def update_stack_resource_map(result, stack_id):
    for resource in result['StackResourceSummaries']:
        update_resource_mapping(resource['ResourceType'], resource["PhysicalResourceId"], stack_id, resource['ResourceStatus'])
def build_cloudformation_entries():
    client = boto3.client('cloudformation')
    stacks = client.list_stacks()
    for stack in stacks['StackSummaries']:
        if stack['StackStatus'] == 'UPDATE_COMPLETE' or stack['StackStatus'] == 'CREATE_COMPLETE':
            stack_id = stack["StackId"]
            update_resource_mapping('AWS:CloudFormation:Stack', stack_id, None, stack['StackStatus'])
            result = client.list_stack_resources(StackName=stack_id)
            update_stack_resource_map(result, stack_id)
            next_token = result['NextToken'] if 'NextToken' in result else None
            while next_token != None:
                result = client.list_stack_resources(StackName=stack_name, NextToken = next_token)
                update_stack_resource_map(result)
                next_token = result.NextToken

def build_s3_entries():
    client = boto3.client('s3')
    buckets = client.list_buckets()['Buckets']
    for bucket in buckets:
        update_resource_mapping('AWS:S3:Bucket', bucket['Name'], None, 'CREATE_COMPLETE')

def build_apigateway_entries():
    client = boto3.client('apigateway')
    resource_list = client.get_rest_apis()['items']
    for resource in resource_list:
        update_resource_mapping('AWS::ApiGateway::RestApi', resource['id'], None, 'CREATE_COMPLETE')
        authorizers = client.get_authorizers(resource['id'])['items']
        for authorizer in authorizers:
            update_resource_mapping('AWS::ApiGateway::Authorizers', authorizer['id'], resource['id'], 'CREATE_COMPLETE')
        deployments = client.get_deployments(resource['id'])['items']
        for deployment in deployments:
            update_resource_mapping('AWS::ApiGateway::Deployment', deployment['id'], resource['id'], 'CREATE_COMPLETE')
    resource_list = client.get_api_keys()
    for resource in resource_list:
        update_resource_mapping('AWS::ApiGateway::ApiKey', resource['id'], None, 'CREATE_COMPLETE')
    

def generate_csv(resource_map):
    print('resource_type, resource_id, parent_stack, resource_status')
    for resource_type in resource_map:
        for resource_id in resource_map[resource_type]:
            resource = resource_map[resource_type][resource_id]
            print(f'{resource_type}, {resource_id}, {resource["parent_stack"]}, {resource["resource_status"]}')

build_cloudformation_entries()
build_s3_entries()
generate_csv(resource_map)
