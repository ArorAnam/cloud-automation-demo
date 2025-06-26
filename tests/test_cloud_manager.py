"""Tests for cloud_manager CLI"""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock

from scripts.cloud_manager import cli, CloudManager


@pytest.fixture
def runner():
    """Create a Click CLI test runner"""
    return CliRunner()


@pytest.fixture
def mock_cloud_manager():
    """Create a mock CloudManager instance"""
    with patch('scripts.cloud_manager.CloudManager') as mock:
        manager = Mock()
        mock.return_value = manager
        yield manager


class TestCLI:
    """Test cases for CLI commands"""
    
    def test_cli_help(self, runner):
        """Test CLI help command"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Cloud Manager CLI' in result.output
        assert 'deploy' in result.output
        assert 'destroy' in result.output
        assert 'status' in result.output
    
    def test_deploy_command(self, runner, mock_cloud_manager):
        """Test deploy command"""
        # Mock Terraform responses
        mock_cloud_manager.terraform.init.return_value = (0, "Initialized", "")
        mock_cloud_manager.terraform.plan.return_value = (0, "Plan succeeded", "")
        mock_cloud_manager.terraform.apply.return_value = (0, "Apply complete", "")
        
        result = runner.invoke(cli, ['deploy', '--environment', 'dev', '--auto-approve'])
        
        assert result.exit_code == 0
        assert 'Deploying to dev environment' in result.output
        assert 'Deployment successful!' in result.output
    
    def test_deploy_with_confirmation(self, runner, mock_cloud_manager):
        """Test deploy command with user confirmation"""
        mock_cloud_manager.terraform.init.return_value = (0, "Initialized", "")
        mock_cloud_manager.terraform.plan.return_value = (0, "Plan succeeded", "")
        
        # Simulate user typing 'y' for confirmation
        result = runner.invoke(cli, ['deploy'], input='y\\n')
        
        assert result.exit_code == 0
        assert 'Do you want to apply these changes?' in result.output
    
    def test_deploy_cancelled(self, runner, mock_cloud_manager):
        """Test deploy command when user cancels"""
        mock_cloud_manager.terraform.init.return_value = (0, "Initialized", "")
        mock_cloud_manager.terraform.plan.return_value = (0, "Plan succeeded", "")
        
        # Simulate user typing 'n' for cancellation
        result = runner.invoke(cli, ['deploy'], input='n\\n')
        
        assert result.exit_code == 0
        assert 'Deployment cancelled' in result.output
    
    def test_destroy_command(self, runner, mock_cloud_manager):
        """Test destroy command"""
        mock_cloud_manager.terraform.destroy.return_value = (0, "Destroyed", "")
        
        result = runner.invoke(cli, ['destroy', '--environment', 'dev', '--force'])
        
        assert result.exit_code == 0
        assert 'Destroying dev environment' in result.output
        assert 'Resources destroyed successfully!' in result.output
    
    def test_destroy_with_confirmation(self, runner, mock_cloud_manager):
        """Test destroy command with confirmation"""
        result = runner.invoke(cli, ['destroy', '--environment', 'dev'], input='n\\n')
        
        assert result.exit_code == 0
        assert 'WARNING: This will destroy all resources' in result.output
        assert 'Destroy cancelled' in result.output
    
    def test_status_command_json(self, runner, mock_cloud_manager):
        """Test status command with JSON output"""
        mock_resources = {
            "ec2_instances": [
                {"id": "i-123", "name": "test", "state": "running", "type": "t3.micro"}
            ],
            "s3_buckets": [
                {"name": "test-bucket", "created": "2023-01-01T00:00:00Z"}
            ]
        }
        mock_cloud_manager.list_resources.return_value = mock_resources
        
        result = runner.invoke(cli, ['status', '--format', 'json'])
        
        assert result.exit_code == 0
        output_json = json.loads(result.output.strip().split('\\n')[-1])
        assert output_json == mock_resources
    
    def test_status_command_table(self, runner, mock_cloud_manager):
        """Test status command with table output"""
        mock_resources = {
            "ec2_instances": [
                {"id": "i-123", "name": "test", "state": "running", "type": "t3.micro"}
            ],
            "s3_buckets": [],
            "vpc_ids": []
        }
        mock_cloud_manager.list_resources.return_value = mock_resources
        
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert 'EC2 Instances:' in result.output
        assert 'test (i-123): running [t3.micro]' in result.output
        assert 'S3 Buckets:' in result.output
        assert 'No buckets found' in result.output
    
    def test_validate_command(self, runner, mock_cloud_manager):
        """Test validate command"""
        mock_cloud_manager.terraform.init.return_value = (0, "Initialized", "")
        mock_cloud_manager.terraform.validate.return_value = (0, "Valid", "")
        
        result = runner.invoke(cli, ['validate', '--environment', 'staging'])
        
        assert result.exit_code == 0
        assert 'Validating Terraform configuration for staging' in result.output
        assert 'Configuration is valid!' in result.output
    
    def test_output_command(self, runner, mock_cloud_manager):
        """Test output command"""
        mock_cloud_manager.terraform.output.return_value = (0, "vpc-123456", "")
        
        result = runner.invoke(cli, ['output', 'vpc_id'])
        
        assert result.exit_code == 0
        assert 'vpc-123456' in result.output


class TestCloudManager:
    """Test cases for CloudManager class"""
    
    @patch('scripts.cloud_manager.boto3.Session')
    @patch('scripts.cloud_manager.Terraform')
    def test_cloud_manager_init(self, mock_terraform, mock_session):
        """Test CloudManager initialization"""
        manager = CloudManager('dev')
        
        assert manager.environment == 'dev'
        assert manager.aws_region == 'us-east-1'
        mock_session.assert_called_once_with(region_name='us-east-1')
    
    @patch('scripts.cloud_manager.boto3.Session')
    @patch('scripts.cloud_manager.Terraform')
    def test_get_terraform_state(self, mock_terraform, mock_session):
        """Test getting Terraform state"""
        mock_tf_instance = Mock()
        mock_terraform.return_value = mock_tf_instance
        mock_tf_instance.cmd.return_value = (0, '{"version": 4}', "")
        
        manager = CloudManager('dev')
        state = manager.get_terraform_state()
        
        assert state == {"version": 4}
        mock_tf_instance.cmd.assert_called_once_with("state", "pull")
    
    @patch('scripts.cloud_manager.boto3.Session')
    @patch('scripts.cloud_manager.Terraform')
    def test_list_resources(self, mock_terraform, mock_session):
        """Test listing resources"""
        # Mock AWS clients
        mock_ec2 = Mock()
        mock_s3 = Mock()
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.client.side_effect = lambda service: {
            'ec2': mock_ec2,
            's3': mock_s3,
            'cloudwatch': Mock()
        }[service]
        
        # Mock EC2 response
        mock_ec2.describe_instances.return_value = {
            "Reservations": [{
                "Instances": [{
                    "InstanceId": "i-123",
                    "State": {"Name": "running"},
                    "InstanceType": "t3.micro",
                    "Tags": [{"Key": "Name", "Value": "test-instance"}]
                }]
            }]
        }
        
        # Mock S3 response
        mock_s3.list_buckets.return_value = {
            "Buckets": [{"Name": "test-bucket", "CreationDate": MagicMock(isoformat=lambda: "2023-01-01")}]
        }
        mock_s3.get_bucket_tagging.return_value = {
            "TagSet": [{"Key": "Environment", "Value": "dev"}]
        }
        
        manager = CloudManager('dev')
        resources = manager.list_resources()
        
        assert len(resources['ec2_instances']) == 1
        assert resources['ec2_instances'][0]['id'] == 'i-123'
        assert len(resources['s3_buckets']) == 1
        assert resources['s3_buckets'][0]['name'] == 'test-bucket'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])