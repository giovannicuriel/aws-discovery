import boto3
import json
import sys 

client = boto3.client('codecommit', region_name=sys.argv[1])

results = client.list_repositories()
for item in results['repositories']:
    branch_results = client.list_branches(repositoryName=item['repositoryName'])
    print(f"{item['repositoryName']}: {len(branch_results['branches'])} branch(es)")
next_token = results['nextToken'] if 'nextToken' in results else None
while next_token != None:
    results = client.list_repositories(nextToken=next_token)
    for item in results['repositories']:
        branch_results = client.list_branches(repositoryName=item['repositoryName'])
        print(f"{item['repositoryName']}: {len(branch_results['branches'])} branch(es)")
    next_token = results['nextToken'] if 'nextToken' in results else None

