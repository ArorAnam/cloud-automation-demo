#!/usr/bin/env python3
"""
Cloud Manager CLI - Main entry point for cloud automation tools
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import click
import boto3
from python_terraform import Terraform
import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class CloudManager:
    """Main class for cloud resource management"""
    
    def __init__(self, environment: str = "dev"):
        self.environment = environment
        self.terraform_dir = Path(__file__).parent.parent / "terraform" / "environments" / environment
        self.terraform = Terraform(working_dir=str(self.terraform_dir))
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        
        # Initialize AWS clients
        self.session = boto3.Session(region_name=self.aws_region)
        self.ec2 = self.session.client("ec2")
        self.s3 = self.session.client("s3")
        self.cloudwatch = self.session.client("cloudwatch")
        
    def get_terraform_state(self) -> Dict[str, Any]:
        """Get current Terraform state"""
        try:
            return_code, stdout, stderr = self.terraform.cmd("state", "pull")
            if return_code == 0:
                return json.loads(stdout)
            else:
                logger.error("Failed to get Terraform state", stderr=stderr)
                return {}
        except Exception as e:
            logger.exception("Error getting Terraform state", error=str(e))
            return {}
    
    def list_resources(self) -> Dict[str, list]:
        """List all managed resources"""
        resources = {
            "ec2_instances": [],
            "s3_buckets": [],
            "vpc_ids": []
        }
        
        try:
            # List EC2 instances
            response = self.ec2.describe_instances(
                Filters=[
                    {"Name": "tag:Environment", "Values": [self.environment]},
                    {"Name": "tag:ManagedBy", "Values": ["terraform"]}
                ]
            )
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    resources["ec2_instances"].append({
                        "id": instance["InstanceId"],
                        "state": instance["State"]["Name"],
                        "type": instance["InstanceType"],
                        "name": next((tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), "N/A")
                    })
            
            # List S3 buckets
            response = self.s3.list_buckets()
            for bucket in response.get("Buckets", []):
                try:
                    tags = self.s3.get_bucket_tagging(Bucket=bucket["Name"])
                    tag_dict = {tag["Key"]: tag["Value"] for tag in tags.get("TagSet", [])}
                    if tag_dict.get("Environment") == self.environment:
                        resources["s3_buckets"].append({
                            "name": bucket["Name"],
                            "created": bucket["CreationDate"].isoformat()
                        })
                except self.s3.exceptions.NoSuchTagSet:
                    pass
            
        except Exception as e:
            logger.exception("Error listing resources", error=str(e))
        
        return resources


@click.group()
@click.option("--debug/--no-debug", default=False, help="Enable debug logging")
@click.pass_context
def cli(ctx, debug):
    """Cloud Manager CLI - Manage cloud infrastructure with ease"""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    ctx.ensure_object(dict)


@cli.command()
@click.option("--environment", "-e", default="dev", help="Target environment (dev/staging/prod)")
@click.option("--auto-approve", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def deploy(ctx, environment, auto_approve):
    """Deploy infrastructure to specified environment"""
    manager = CloudManager(environment)
    
    click.echo(f"Deploying to {environment} environment...")
    
    # Initialize Terraform
    return_code, stdout, stderr = manager.terraform.init()
    if return_code != 0:
        click.echo(f"Terraform init failed: {stderr}", err=True)
        sys.exit(1)
    
    # Plan changes
    # Note: Terraform plan returns:
    # 0 = succeeded with empty diff (no changes)
    # 1 = error occurred
    # 2 = succeeded with non-empty diff (changes present)
    return_code, stdout, stderr = manager.terraform.plan()
    
    # Check if it's a real error (code 1) vs successful plan with changes (code 2) or no changes (code 0)
    if return_code == 1:
        click.echo(f"Terraform plan failed: {stderr}", err=True)
        sys.exit(1)
    elif return_code == 2:
        click.echo("✅ Terraform plan succeeded - changes detected")
    elif return_code == 0:
        click.echo("✅ Terraform plan succeeded - no changes needed")
        click.echo("Infrastructure is already up to date!")
        return
    else:
        # Handle any other unexpected return codes
        click.echo(f"⚠️  Terraform plan returned unexpected code {return_code}")
        click.echo(f"Output: {stdout}")
        if stderr:
            click.echo(f"Warnings/Messages: {stderr}")
    
    # Apply changes
    if auto_approve or click.confirm("Do you want to apply these changes?"):
        return_code, stdout, stderr = manager.terraform.apply(skip_plan=True, auto_approve=True)
        if return_code == 0:
            click.echo("🎉 Deployment successful!")
        else:
            click.echo(f"❌ Deployment failed: {stderr}", err=True)
            sys.exit(1)
    else:
        click.echo("Deployment cancelled.")


@cli.command()
@click.option("--environment", "-e", default="dev", help="Target environment (dev/staging/prod)")
@click.option("--force", is_flag=True, help="Force destroy without confirmation")
@click.pass_context
def destroy(ctx, environment, force):
    """Destroy infrastructure in specified environment"""
    manager = CloudManager(environment)
    
    if not force:
        click.echo(f"⚠️  WARNING: This will destroy all resources in {environment}!")
        if not click.confirm("Are you sure you want to continue?"):
            click.echo("Destroy cancelled.")
            return
    
    click.echo(f"🗑️  Destroying {environment} environment...")
    
    return_code, stdout, stderr = manager.terraform.destroy(auto_approve=True)
    if return_code == 0:
        click.echo("✅ Resources destroyed successfully!")
    else:
        click.echo(f"❌ Destroy failed: {stderr}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--environment", "-e", default="dev", help="Target environment (dev/staging/prod)")
@click.option("--format", "-f", type=click.Choice(["json", "table"]), default="table", help="Output format")
@click.pass_context
def status(ctx, environment, format):
    """Show status of resources in specified environment"""
    manager = CloudManager(environment)
    
    click.echo(f"Getting status for {environment} environment...")
    
    resources = manager.list_resources()
    
    if format == "json":
        click.echo(json.dumps(resources, indent=2))
    else:
        # EC2 Instances
        click.echo("\nEC2 Instances:")
        if resources["ec2_instances"]:
            for instance in resources["ec2_instances"]:
                click.echo(f"  - {instance['name']} ({instance['id']}): {instance['state']} [{instance['type']}]")
        else:
            click.echo("  No instances found")
        
        # S3 Buckets
        click.echo("\nS3 Buckets:")
        if resources["s3_buckets"]:
            for bucket in resources["s3_buckets"]:
                click.echo(f"  - {bucket['name']} (created: {bucket['created']})")
        else:
            click.echo("  No buckets found")


@cli.command()
@click.option("--environment", "-e", default="dev", help="Target environment (dev/staging/prod)")
@click.pass_context
def validate(ctx, environment):
    """Validate Terraform configuration"""
    manager = CloudManager(environment)
    
    click.echo(f"Validating Terraform configuration for {environment}...")
    
    # Initialize first
    return_code, stdout, stderr = manager.terraform.init()
    if return_code != 0:
        click.echo(f"❌ Terraform init failed: {stderr}", err=True)
        sys.exit(1)
    
    # Validate
    return_code, stdout, stderr = manager.terraform.validate()
    if return_code == 0:
        click.echo("✅ Configuration is valid!")
        # Show any warnings if present
        if stderr and "Warning" in stderr:
            click.echo(f"⚠️  Warnings: {stderr}")
    else:
        click.echo(f"❌ Validation failed: {stderr}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--environment", "-e", default="dev", help="Target environment (dev/staging/prod)")
@click.argument("output_name")
@click.pass_context
def output(ctx, environment, output_name):
    """Get Terraform output value"""
    manager = CloudManager(environment)
    
    return_code, stdout, stderr = manager.terraform.output(output_name)
    if return_code == 0:
        click.echo(stdout.strip())
    else:
        click.echo(f"Failed to get output: {stderr}", err=True)
        sys.exit(1)


@cli.group()
@click.pass_context
def cost(ctx):
    """Cost management commands"""
    pass


@cost.command("estimate")
@click.option("--environment", "-e", default="dev", help="Target environment (dev/staging/prod)")
@click.pass_context
def cost_estimate(ctx, environment):
    """Estimate monthly costs for environment"""
    # This is a placeholder for cost estimation logic
    click.echo(f"Estimating costs for {environment} environment...")
    click.echo("Cost estimation feature coming soon!")


if __name__ == "__main__":
    cli()