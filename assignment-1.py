from datetime import datetime, timedelta
from aws_wrappers import Aws_Wrappers
import pdb
import pytest

# Mention ASG, REGION
asgname = "<asgname>"    #enter ASG name
region = "<region>"      #enter region name where ASG located
aws_wrappers = Aws_Wrappers(asgname, region)


@pytest.mark.parametrize(("aws_wrappers", "asgname", "region"), [(aws_wrappers, asgname, region)])
def test_ASG_desirerunningcount(aws_wrappers, asgname, region): 
   '''
   # TestCase A-1 
   # ASG desire running count should be same as running instances. if mismatch fails
   '''
   try:
      # Describe ASG 
      describe_asg_response = aws_wrappers.get_describe_asg()
      #Gets Desired Running Count
      desired_running_count = describe_asg_response["AutoScalingGroups"][0]["DesiredCapacity"] 
      # Gets instances attached in ASG
      intances_count_in_asg = len(describe_asg_response["AutoScalingGroups"][0]["Instances"])
      instance_status_check = {}
      for i in range(0, intances_count_in_asg):
         # Get instance Id's of attached instances in ASG 
         instance_id = describe_asg_response["AutoScalingGroups"][0]["Instances"][i]["InstanceId"]
         # Get status of instances
         instance_status = describe_asg_response["AutoScalingGroups"][0]["Instances"][i]["LifecycleState"]
         instance_status_check[instance_id] = instance_status
      #Get Running instances count   
      running_instance_count = len(instance_status_check.values())
      #Desired count should be equal to running
      if desired_running_count == running_instance_count:
          print("PASSED: Desired instance capacity is same as running instances, DesiredCapacity: {}, RunningInstance: {}".format(desired_running_count, running_instance_count))
      else:
          print("FAILED: Desired instance capacity is not same as running instances, DesiredCapacity: {}, RunningInstance: {}".format(desired_running_count, running_instance_count))
   except Exception as e:
      assert False

@pytest.mark.parametrize(("aws_wrappers", "asgname", "region"), [(aws_wrappers, asgname, region)])
def test_ASG_availability_zone(aws_wrappers, asgname, region):
    '''
    # TestCase A-2 
    # if more than 1 instance running on ASG, then ec2 instance should on available and distributed on multiple availibity zone.
    '''
    try:
       #Describe ASG
       describe_asg_response = aws_wrappers.get_describe_asg()
       # Count instances in ASG
       instances_count_in_asg = len(describe_asg_response["AutoScalingGroups"][0]["Instances"])
       if instances_count_in_asg < 2:
          assert False #0 or 1 istances are running
       availability_zones = {}
       for i in range(0, instances_count_in_asg):
          instance_id = describe_asg_response["AutoScalingGroups"][0]["Instances"][i]["InstanceId"] 
          av_zone = describe_asg_response["AutoScalingGroups"][0]["Instances"][i]['AvailabilityZone']
          availability_zones[instance_id] = av_zone
       print(availability_zones)
       if len(availability_zones) < instances_count_in_asg:
           print("FAILED - EC2 Instances are not distributed across multiple Availability Zones")
       else:
           print("PASSED - EC2 Instances are available and distributed across multiple Availability Zones")
    except Exception as e:
      assert False

@pytest.mark.parametrize(("aws_wrappers", "asgname", "region"), [(aws_wrappers, asgname, region)])
def test_ASG_vpcid_sg_imgid(aws_wrappers, asgname, region):
   '''
   # TestCase A-3
   # SecuirtyGroup, ImageID and VPCID should be same on ASG running instances
   '''
   try:
      ec2_details = {}
      asg_instance = aws_wrappers.get_describe_instances()
      security_groups = [sgroup["GroupId"] for instance in asg_instance.values() for sgroup in instance["SecurityGroups"]]
      image_ids = [instance["ImageId"] for instance in asg_instance.values()]
      vpc_ids = [instance["VpcId"] for instance in asg_instance.values()]
      instance_id =  [instance["InstanceId"] for instance in asg_instance.values()]
      for instance in range(len(instance_id)):
          ec2_details[instance_id[instance]] = {"vpc_id": vpc_ids[instance], "security_group": set(security_groups),"image_id":image_ids[instance]}

      instance_ids = list(ec2_details.keys())

      vpc_id = ec2_details[instance_ids[0]]['vpc_id']
      security_group = ec2_details[instance_ids[0]]['security_group']
      image_id = ec2_details[instance_ids[0]]['image_id']

      for ids in instance_ids:
         if ec2_details[ids]['vpc_id'] == vpc_id or ec2_details[ids]['security_group'] == security_group or ec2_details[ids]['image_id'] == image_id:
              print("PASSED - Security Group, Image ID, and VPC ID are the same on all running instances")
         else:
             print("FAILED - Security Group, Image ID, and VPC ID are not the same on all running instances")
   except Exception as e:
      assert False


@pytest.mark.parametrize(("aws_wrappers", "asgname", "region"), [(aws_wrappers, asgname, region)])
def test_ASG_Uptime_of_Instances(aws_wrappers, asgname, region):
   '''
   # TestCase A-4
   # Findout uptime of ASG running instances and get the longest running instance.
   '''
   try:
      asg_instance = aws_wrappers.get_describe_instances()
      longest_running_instance = None
      longest_uptime = timedelta()
      for instance in asg_instance.values():
        instance_id = instance["InstanceId"]
        launch_time = instance['LaunchTime']
        uptime = datetime.now(launch_time.tzinfo) - launch_time
        print("Instance - ID: {0}, Uptime: {1}".format(instance_id, uptime))
        if uptime > longest_uptime:
            longest_uptime = uptime
            longest_running_instance = instance_id
      print("Longest Running Instance - ID: {0}, Uptime: {1}".format(longest_running_instance, longest_uptime))
   except Exception as e:
      assert False
      print(str(e))

@pytest.mark.parametrize(("aws_wrappers", "asgname", "region"), [(aws_wrappers, asgname, region)])
def test_ASG_ScheduledActions(aws_wrappers, asgname, region): 
    '''
    # TestCase B-1
    # Find the Scheduled actions of the given ASG which is going to run next and calculate elapsed in hh:mm: ss from the current time.
    '''
    try:
        # Get the scheduled actions of ASG
        scheduled_action_details = aws_wrappers.get_scheduled_actions()
        #List of Scheduled of scheduled action
        scheduled_actions = scheduled_action_details["ScheduledUpdateGroupActions"]
        if len(scheduled_actions) == 0:
            print("No Scheduled Actions found on given ASG")
            assert False

        next_scheduled_action = min(scheduled_actions, key=lambda stime: stime["StartTime"])
        current_time = datetime.utcnow()
        start_time = next_scheduled_action["StartTime"].replace(tzinfo=None)
        elapsed_time = current_time - start_time
        hh_mm_ss = str(elapsed_time)
        print("Time to Next Scheduled Action - {0}".format(hh_mm_ss))
    except Exception as e:
      assert False
      print(str(e))

@pytest.mark.parametrize(("aws_wrappers", "asgname", "region"), [(aws_wrappers, asgname, region)])
def test_ASG_calculate_launched_and_terminated_instances(aws_wrappers, asgname, region):
    '''
    # TestCase B-2
    # Calculate the total number of instances launched and terminated on the current day for the given ASG.
    '''
    try:
       launch_count = 0
       terminate_count = 0
       today = datetime.now().date()
       # Get the sheduled actions of ASG
       ags_handle = aws_wrappers.get_aws_handle()
       response = ags_handle.describe_scaling_activities(AutoScalingGroupName=asgname)
       for activity in response['Activities']:
           print("\n")
           print(activity['StartTime'].date()) 
           print(activity['Description']) 
           print(activity['StatusCode'])
           print("\n")
       scheduled_action_details = aws_wrappers.get_scheduled_actions()
       #List of Scheduled of scheduled actions
       scheduled_actions = scheduled_action_details["ScheduledUpdateGroupActions"]
       for action in scheduled_actions:
         if action["StartTime"].date() == today:
            if action["DesiredCapacity"] > action["MinSize"]:
                launch_count += action["DesiredCapacity"] - action["MinSize"]
            elif action["DesiredCapacity"] < action["MinSize"]:
                terminate_count += action["MinSize"] - action["DesiredCapacity"]

       print("Instances Launched Today - {0}, Instances Terminated Today - {1}".format(launch_count, terminate_count))
    except Exception as e:
      assert False
      print(str(e))
