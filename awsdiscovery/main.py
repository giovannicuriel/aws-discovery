import boto3
import json

resource_map = {}

def update_resource_mapping(resource_type, resource_id, stack_id, status=None, extra=None):
    if not resource_type in resource_map:
        resource_map[resource_type] = {}
    
    if not resource_id in resource_map[resource_type]:
        resource_map[resource_type][resource_id] = {}
    
    if not 'parent_stack' in resource_map[resource_type][resource_id]:
        resource_map[resource_type][resource_id]['parent_stack'] = stack_id
        resource_map[resource_type][resource_id]['resource_status'] = status    
        resource_map[resource_type][resource_id]['extra'] = extra
    elif resource_map[resource_type][resource_id]['parent_stack'] is None:
        resource_map[resource_type][resource_id]['parent_stack'] = stack_id
        resource_map[resource_type][resource_id]['resource_status'] = status
        resource_map[resource_type][resource_id]['extra'] = extra
        

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
    

def build_cloudfront_entries():
    print('Retrieving CloudFront resources')
    client = boto3.client('cloudfront')
    resource_list = client.list_distributions()
    for resource in resource_list['DistributionList']['Items']:
        print('Checking distribution {}'.format(resource['Id']))
        update_resource_mapping('AWS::CloudFormation::Distribution', resource['Id'], None, 'CREATE_COMPLETE')
        for origin in resource['Origins']['Items']:
            update_resource_mapping('AWS::CloudFormation::Distribution::Origin', origin['Id'], resource['Id'], 'CREATE_COMPLETE')

def build_dynamodb_entries():
    print('Retrieving DynamoDB resources')
    client = boto3.client('dynamodb')
    resource_list = client.list_tables()
    for resource in resource_list['TableNames']:
        print('Checking table {}'.format(resource))
        update_resource_mapping('AWS::DynamoDB::Table', resource, None, 'CREATE_COMPLETE')

def build_secretsmanager_entries():
    print('Retrieving SecretsManager resources')
    client = boto3.client('secretsmanager')
    results = client.list_secrets()
    print('There are {} secrets.'.format(len(results['SecretList'])))
    for item in results['SecretList']:
        update_resource_mapping('AWS::SecretsManager::Secret', item['ARN'], None, 'CREATE_COMPLETED', item['Name'])
    next_token = results['NextToken'] if 'NextToken' in results else None
    while next_token != None:
        results = client.list_secrets(NextToken=next_token)
        print('There are more {} secrets.'.format(len(results['SecretList'])))
        for item in results['SecretList']:
            update_resource_mapping('AWS::SecretsManager::Secret', item['ARN'], None, 'CREATE_COMPLETED', item['Name'])
        next_token = results['NextToken'] if 'NextToken' in results else None

def build_ecs_entries():
    print('Retrieving ECS resources')
    client = boto3.client('ecs')
    results = client.list_clusters()
    print('There are {} clusters.'.format(len(results['clusterArns'])))
    for item in results['clusterArns']:
        update_resource_mapping('AWS::ECS::Cluster', item, None, 'CREATE_COMPLETED')
    next_token = results['nextToken'] if 'nextToken' in results else None
    while next_token != None:
        results = client.list_clusters(nextToken=next_token)
        print('There are more {} clusters.'.format(len(results['clusterArns'])))
        for item in results['clusterArns']:
            update_resource_mapping('AWS::ECS::Cluster', item, None, 'CREATE_COMPLETED')
        next_token = results['nextToken'] if 'nextToken' in results else None


def generate_csv(resource_map):
    """
    Generate a CSV-style output given resource map
    """
    file = open('./output.csv', 'w')
    file.write('resource_type, resource_id, parent_stack, resource_status\n')
    for resource_type in resource_map:
        for resource_id in resource_map[resource_type]:
            resource = resource_map[resource_type][resource_id]
            file.write(f'{resource_type}, {resource_id}, {resource["parent_stack"]}, {resource["resource_status"]}\n')
    file.close()

build_cloudformation_entries()
build_s3_entries()
build_apigateway_entries()
build_cloudfront_entries()
build_dynamodb_entries()
build_secretsmanager_entries()
build_ecs_entries()
generate_csv(resource_map)
