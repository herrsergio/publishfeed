#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stack import RssFeedStack

app = cdk.App()
RssFeedStack(app, "RssFeedStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
