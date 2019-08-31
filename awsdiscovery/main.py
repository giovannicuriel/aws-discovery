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
    print('Retrieving CloudFormation stacks')
    client = boto3.client('cloudformation')
    stacks = client.list_stacks()
    print('There are {} stacks'.format(len(stacks['StackSummaries'])))
    for stack in stacks['StackSummaries']:
        print('Checking stack {}, status {}'.format(stack['StackName'], stack['StackStatus']))
        if stack['StackStatus'] == 'UPDATE_COMPLETE' or stack['StackStatus'] == 'CREATE_COMPLETE':
            stack_id = stack["StackId"]
            update_resource_mapping('AWS:CloudFormation:Stack', stack_id, None, stack['StackStatus'])
            result = client.list_stack_resources(StackName=stack_id)
            update_stack_resource_map(result, stack_id)
            next_token = result['NextToken'] if 'NextToken' in result else None
            while next_token != None:
                result = client.list_stack_resources(StackName=stack_id, NextToken = next_token)
                update_stack_resource_map(result, stack_id)
                next_token = result.NextToken

def build_s3_entries():
    print('Retrieving S3 buckets')
    client = boto3.client('s3')
    buckets = client.list_buckets()['Buckets']
    print('There are {} buckets'.format(len(buckets)))
    for bucket in buckets:
        print('Checking bucket {}'.format(bucket['Name']))
        update_resource_mapping('AWS:S3:Bucket', bucket['Name'], None, 'CREATE_COMPLETE')

def build_apigateway_entries():
    print('Retrieving API gateway resources')
    client = boto3.client('apigateway')
    resource_list = client.get_rest_apis()['items']
    print('There are {} REST APIs'.format(len(resource_list)))
    for resource in resource_list:
        print('Checking API {}'.format(resource['name']))
        update_resource_mapping('AWS::ApiGateway::RestApi', resource['id'], None, 'CREATE_COMPLETE')
        authorizers = client.get_authorizers(restApiId=resource['id'])['items']
        for authorizer in authorizers:
            update_resource_mapping('AWS::ApiGateway::Authorizers', authorizer['id'], resource['id'], 'CREATE_COMPLETE')
        deployments = client.get_deployments(restApiId=resource['id'])['items']
        for deployment in deployments:
            update_resource_mapping('AWS::ApiGateway::Deployment', deployment['id'], resource['id'], 'CREATE_COMPLETE')
    resource_list = client.get_api_keys()
    print('There are {} API keys'.format(len(resource_list)))
    for resource in resource_list['items']:
        update_resource_mapping('AWS::ApiGateway::ApiKey', resource['id'], None, 'CREATE_COMPLETE')
    

def generate_csv(resource_map):
    """
    Generate a CSV-style output given resource map
    """
    print('resource_type, resource_id, parent_stack, resource_status')
    for resource_type in resource_map:
        for resource_id in resource_map[resource_type]:
            resource = resource_map[resource_type][resource_id]
            print(f'{resource_type}, {resource_id}, {resource["parent_stack"]}, {resource["resource_status"]}')

# build_cloudformation_entries()
# build_s3_entries()
build_apigateway_entries()
generate_csv(resource_map)
