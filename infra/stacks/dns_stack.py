from pathlib import Path

from aws_cdk import CustomResource, Duration, Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_route53 as route53
from aws_cdk.custom_resources import Provider
from constructs import Construct

# EB CNAME for the initial production environment.
# After the first blue/green swap this should be updated to whichever env is live.
EB_ORIGIN_HOST = "mimir-blue.us-east-1.elasticbeanstalk.com"

_LAMBDA_DIR = Path(__file__).resolve().parent.parent / "lambda" / "route53_cname"


class MimirDns(Stack):
    """CloudFront distribution + Route53 CNAME for mimir.featurefactory.io.

    Creates a *new* CloudFront distribution for Mimir (distinct from the
    existing static-site distribution E1RVYM4PQIZHGZ which is left intact).
    Uses the pre-issued ACM certificate for mimir.featurefactory.io and points
    at the mimir-blue EB environment as the initial origin.

    The Route53 record is managed via an idempotent custom-resource Lambda
    (infra/lambda/route53_cname/handler.py) that UPSERTs the CNAME rather
    than failing if the record already exists.  This avoids ConflictingResourceExists
    errors on re-deploy when the record still points at the old EB/S3 origin.

    ``acm_cert_arn`` must be in us-east-1 (CloudFront requirement) — the
    existing cert arn:aws:acm:us-east-1:411113550285:certificate/b0d774c7-…
    satisfies this.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        domain: str,
        acm_cert_arn: str,
        hosted_zone: route53.IHostedZone | None = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._domain = domain
        self._subdomain = f"mimir.{domain}"

        if hosted_zone is None:
            hosted_zone = route53.HostedZone.from_lookup(
                self, "Zone", domain_name=domain
            )

        cert = acm.Certificate.from_certificate_arn(
            self, "MimirCert", certificate_arn=acm_cert_arn
        )

        distribution = self._create_distribution(cert)
        self._create_route53_cname(hosted_zone, distribution)

    def _create_distribution(self, cert: acm.ICertificate) -> cloudfront.Distribution:
        """Create the CloudFront distribution for mimir.featurefactory.io."""
        hsts_policy = cloudfront.ResponseHeadersPolicy(
            self,
            "HstsPolicy",
            security_headers_behavior=cloudfront.ResponseSecurityHeadersBehavior(
                strict_transport_security=cloudfront.ResponseHeadersStrictTransportSecurity(
                    access_control_max_age=Duration.seconds(3600),
                    override=True,
                    include_subdomains=True,
                ),
            ),
        )

        return cloudfront.Distribution(
            self,
            "MimirCdn",
            domain_names=[self._subdomain],
            certificate=cert,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.HttpOrigin(
                    EB_ORIGIN_HOST,
                    protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                    http_port=80,
                    # Tell Django this connection is HTTPS so SECURE_SSL_REDIRECT
                    # doesn't loop (Django checks SECURE_PROXY_SSL_HEADER).
                    custom_headers={"X-Forwarded-Proto": "https"},
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                # Disable caching — Django renders dynamic pages, DRF returns live data.
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                # Forward all headers/cookies/query strings so Django sessions work.
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                response_headers_policy=hsts_policy,
                # ALLOW_ALL is required — CloudFront's default (GET+HEAD only) returns
                # 403 for any POST/PUT/PATCH/DELETE (login, HTMX, DRF writes, etc.).
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
            ),
            comment="Mimir FOB — mimir.featurefactory.io",
        )

    def _create_route53_cname(
        self,
        hosted_zone: route53.IHostedZone,
        distribution: cloudfront.Distribution,
    ) -> None:
        """Idempotent CNAME upsert via Lambda custom resource.

        Unlike a plain CDK ARecord, this survives re-deploys when a CNAME
        already exists (avoids ConflictingResourceExists from Route53 API).
        """
        on_event_fn = lambda_.Function(
            self,
            "Route53CnameFn",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.on_event",
            code=lambda_.Code.from_asset(str(_LAMBDA_DIR)),
            timeout=Duration.minutes(2),
        )

        on_event_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "route53:ListResourceRecordSets",
                    "route53:ChangeResourceRecordSets",
                ],
                resources=[
                    f"arn:aws:route53:::hostedzone/{hosted_zone.hosted_zone_id}",
                ],
            )
        )

        provider = Provider(self, "Route53CnameProvider", on_event_handler=on_event_fn)

        record_fqdn = f"mimir.{self._domain}."
        cname_resource = CustomResource(
            self,
            "MimirCnameResource",
            service_token=provider.service_token,
            properties={
                "HostedZoneId": hosted_zone.hosted_zone_id,
                "RecordName": record_fqdn,
                "TargetDomain": distribution.distribution_domain_name,
                "Ttl": "300",
            },
        )
        cname_resource.node.add_dependency(distribution)
