# aws-discovery

This tool generates a comprehensive table with all AWS resources and their
ARN. This might be useful to create a resource map of all the things currently
configured on a AWS account.

## What does this tool do?

It checks all major services (or, at least, those ones I'm currently working
on. There's more, I know. If this almost suit your needs, I'd be more than
happy to review your PR :sunglasses:) and build a CSV with all resources it
finds.

## How to run

First, install all of its dependencies:

```bash
pipenv install
```

And then run it.

```bash
pipenv shell
python3 -m awsdiscovery.main
# OR
# This will list all of your repositories and their number of branches
# Useful to detect empty repository ;)
python3 -m awsdiscovery.codecommit us-east-1
```

Wait a little bit (depending on the number of resources, it might take a while
to gather all information) and it will print all the resources it found.
