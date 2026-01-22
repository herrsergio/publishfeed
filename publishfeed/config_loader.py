import os
import boto3
import json
from dynamo_ops import DynamoDBOps

class ConfigLoader:
    def __init__(self):
        self.ssm = boto3.client('ssm')
        self.db_ops = DynamoDBOps()

    def load_feed_config(self, feed_id):
        """
        Load feed configuration (URLs, hashtags) from DynamoDB.
        """
        return self.db_ops.get_feed_config(feed_id)

    def load_secrets(self, feed_id):
        """
        Load secrets (Twitter keys) from SSM Parameter Store.
        Expected path: /rss-feed/{feed_id}/twitter_creds
        """
        parameter_name = f"/rss-feed/{feed_id}/twitter_creds"
        try:
            response = self.ssm.get_parameter(
                Name=parameter_name,
                WithDecryption=True
            )
            secrets_json = response['Parameter']['Value']
            return json.loads(secrets_json)
        except self.ssm.exceptions.ParameterNotFound:
            print(f"Secrets not found for {feed_id} at {parameter_name}")
            return None

    def load_linkedin_secrets(self):
        """
        Load LinkedIn secrets from global SSM path.
        Expected path: /rss-feed/global/linkedin_creds
        """
        parameter_name = "/rss-feed/global/linkedin_creds"
        try:
            response = self.ssm.get_parameter(
                Name=parameter_name,
                WithDecryption=True
            )
            secrets_json = response['Parameter']['Value']
            return json.loads(secrets_json)
        except self.ssm.exceptions.ParameterNotFound:
            print(f"LinkedIn secrets not found at {parameter_name}")
            return None
