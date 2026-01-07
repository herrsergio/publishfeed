from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_ssm as ssm,
    aws_events as events,
    aws_events_targets as targets,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
)
from constructs import Construct

class RssFeedStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table: RSSContent
        # Partition Key: url (String)
        # GSI: StatusIndex (status, dateAdded)
        self.rss_table = dynamodb.Table(
            self, "RSSContent",
            partition_key=dynamodb.Attribute(name="url", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )
        
        self.rss_table.add_global_secondary_index(
            index_name="StatusIndex",
            partition_key=dynamodb.Attribute(name="status", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="dateAdded", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # DynamoDB Table: FeedConfigurations
        # Partition Key: feed_id (String)
        self.config_table = dynamodb.Table(
            self, "FeedConfigurations",
            partition_key=dynamodb.Attribute(name="feed_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Lambda Layer? (We use DockerImage so no layer needed presumably, or baking it in)
        
        # 1. Fetch Feed Function
        self.fetch_function = _lambda.DockerImageFunction(
            self, "FetchFeedFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                "../publishfeed",
                cmd=["lambda_fetch.handler"]
            ),
            timeout=Duration.minutes(5),
            memory_size=512,
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                "RSS_TABLE_NAME": self.rss_table.table_name,
                "CONFIG_TABLE_NAME": self.config_table.table_name
            }
        )

        # 2. Publish Feed Function
        self.publish_function = _lambda.DockerImageFunction(
            self, "PublishFeedFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                "../publishfeed",
                cmd=["lambda_publish.handler"]
            ),
            timeout=Duration.minutes(2),
            memory_size=256,
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                "RSS_TABLE_NAME": self.rss_table.table_name,
                "CONFIG_TABLE_NAME": self.config_table.table_name,
                # TWEET_MAX_LENGTH etc defined in config.py in the image
            }
        )

        # Grant Permissions
        self.rss_table.grant_read_write_data(self.fetch_function)
        self.config_table.grant_read_data(self.fetch_function)
        
        self.rss_table.grant_read_write_data(self.publish_function)
        self.config_table.grant_read_data(self.publish_function)
        
        # Grant SSM Permissions (Broad grant for now or specific path?)
        # We need to grant access to /rss-feed/*
        # Since we don't know the exact ARNs of parameters yet (dynamic), we grant on the path structure.
        # Ideally we construct ARN.
        # simpler: grant_read(parameter) but we don't have the parameter construct here.
        # We grant permission to get parameters by path.
        
        # Manually create policy statement for SSM
        from aws_cdk import aws_iam as iam
        ssm_policy = iam.PolicyStatement(
            actions=["ssm:GetParameter", "ssm:GetParameters"],
            resources=["arn:aws:ssm:*:*:parameter/rss-feed/*"]
        )
        self.publish_function.add_to_role_policy(ssm_policy)


        # Scheduler
        # 1. Fetch Daily
        rule_fetch = events.Rule(
            self, "RuleFetchDaily",
            schedule=events.Schedule.rate(Duration.days(1))
        )
        rule_fetch.add_target(targets.LambdaFunction(self.fetch_function))

        # 2. Publish Every 2 Hours
        rule_publish = events.Rule(
            self, "RulePublishEvery2Hours",
            schedule=events.Schedule.rate(Duration.hours(2))
        )
        rule_publish.add_target(targets.LambdaFunction(self.publish_function))
