"""
S3 database backups for Mimir pre-migrate snapshots.

Creates:
  - S3 bucket ``mimir-db-backups-{account}`` with encryption and 90-day lifecycle.
  - IAM managed policy ``MimirDbBackup`` (S3 put/list on backup bucket) on the EB
    instance role so ``manage.py pre_deploy_backup`` can upload via boto3.
  - Attaches ``AmazonSSMManagedInstanceCore`` to the EB instance role so
    ``deploy-idle.sh`` can run backup via SSM SendCommand before deploy.
"""

import aws_cdk as cdk
from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct

EB_INSTANCE_ROLE = "aws-elasticbeanstalk-ec2-role"


class MimirBackups(Stack):
    """S3 pre-migrate backup bucket + EB instance IAM for uploads and SSM."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = self._create_bucket()
        backup_policy = self._create_backup_policy()
        self._attach_policies_to_instance_role(backup_policy)

        cdk.CfnOutput(
            self,
            "BackupBucketName",
            value=self.bucket.bucket_name,
            description="S3 bucket for pre-migrate pg_dump and dumpdata artifacts",
            export_name="mimir-backup-bucket-name",
        )
        cdk.CfnOutput(
            self,
            "BackupPolicyArn",
            value=backup_policy.managed_policy_arn,
            description="IAM managed policy ARN for EB instance S3 backup uploads",
            export_name="mimir-backup-policy-arn",
        )

    @property
    def bucket_name(self) -> str:
        return self.bucket.bucket_name

    def _create_bucket(self) -> s3.Bucket:
        return s3.Bucket(
            self,
            "DbBackupsBucket",
            bucket_name=f"mimir-db-backups-{self.account}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="ExpirePreMigrate",
                    prefix="pre-migrate/",
                    expiration=Duration.days(90),
                    enabled=True,
                ),
            ],
        )

    def _create_backup_policy(self) -> iam.ManagedPolicy:
        bucket_arn = self.bucket.bucket_arn
        return iam.ManagedPolicy(
            self,
            "DbBackupPolicy",
            managed_policy_name="MimirDbBackup",
            description="Allow Mimir EB instances to upload pre-migrate DB backups to S3.",
            statements=[
                iam.PolicyStatement(
                    sid="ListBackupBucket",
                    effect=iam.Effect.ALLOW,
                    actions=["s3:ListBucket"],
                    resources=[bucket_arn],
                ),
                iam.PolicyStatement(
                    sid="PutBackupObjects",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:PutObject",
                        "s3:AbortMultipartUpload",
                    ],
                    resources=[f"{bucket_arn}/pre-migrate/*"],
                ),
            ],
        )

    def _attach_policies_to_instance_role(self, backup_policy: iam.ManagedPolicy) -> None:
        instance_role = iam.Role.from_role_name(
            self,
            "EbInstanceRole",
            role_name=EB_INSTANCE_ROLE,
        )
        backup_policy.attach_to_role(instance_role)

        instance_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore",
            )
        )
