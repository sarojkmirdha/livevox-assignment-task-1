'''
Wrapper class for AWS actions
'''
import json
import os
import sys
import boto3

aws_access_key_id=os.environ['aws_access_key_id']
aws_secret_access_key=os.environ['aws_secret_access_key']

class Aws_Wrappers:
    '''
    AWS Wrappers for ASG details
    '''

    def __init__(self, asgname, region):
        '''
        AWS Wrappers class constructor to initialize the object
        Input Arguments: asgname must be str, region must be str
        '''
        self.asgname = asgname
        self.region = region
 
    def get_aws_handle(self):
        sg_client_handle = boto3.client('autoscaling',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name=self.region)
        return sg_client_handle

    def get_ec2_handle(self):
        ec2_client_handle = boto3.client('ec2',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name=self.region)
        return ec2_client_handle

    def get_describe_asg(self):
        asg_client = self.get_aws_handle()
        asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asgname])
        return asg_response

    def get_describe_instances(self):
        asg_client = self.get_aws_handle()
        ec2 = self.get_ec2_handle()

        asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asgname])
        instance_ids = [instance["InstanceId"] for instance in asg_response['AutoScalingGroups'][0]['Instances']]
        ec2_response = ec2.describe_instances(InstanceIds=instance_ids)
        instances = {}
        for reservation in ec2_response["Reservations"]:
          for instance in reservation["Instances"]:
            instances[instance["InstanceId"]] = {
                "InstanceId": instance["InstanceId"],
                "SecurityGroups": instance["SecurityGroups"],
                "ImageId": instance["ImageId"],
                "VpcId": instance["VpcId"],
                "LaunchTime": instance["LaunchTime"],
                "AvailabilityZone": instance["Placement"]["AvailabilityZone"],
            }
        return instances

    def get_scheduled_actions(self):
        asg_client = self.get_aws_handle()
        scheduledActions_response = asg_client.describe_scheduled_actions(AutoScalingGroupName=self.asgname)

        return scheduledActions_response
