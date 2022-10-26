try:
    import os
    import sys
    import json 
    import uuid
    import boto3 
    import json
    import Config
    import botocore.exceptions
except ModuleNotFoundError:
    os.system('pip install uuid')
    os.system('pip install boto3')

def main():
    try:
        i = 0
        n = 0
        guid = str(uuid.uuid4())[:10]
        print("""            region       regionName\n
                us-east-2	US East (Ohio)\n
                us-east-1	US East (N. Virginia)\n
                us-west-1	US West (N. California)\n
                us-west-2	US West (Oregon)\n
                af-south-1	Africa (Cape Town)\n
                ap-east-1	Asia Pacific (Hong Kong)\n
                ap-southeast-3	Asia Pacific (Jakarta)\n
                ap-south-1	Asia Pacific (Mumbai)\n
                ap-northeast-3	Asia Pacific (Osaka)\n
                ap-northeast-2	Asia Pacific (Seoul)\n
                ap-southeast-1	Asia Pacific (Singapore)\n
                ap-southeast-2	Asia Pacific (Sydney)\n
                ap-northeast-1	Asia Pacific (Tokyo)\n
                ca-central-1	Canada (Central)\n
                eu-central-1	Europe (Frankfurt)\n
                eu-west-1	Europe (Ireland)\n
                eu-west-2	Europe (London)\n
                eu-south-1	Europe (Milan)\n
                eu-west-3	Europe (Paris)\n
                eu-north-1	Europe (Stockholm)\n
                me-south-1	Middle East (Bahrain)\n
                me-central-1	Middle East (UAE)\n
                sa-east-1	South America (São Paulo)""")
        print('Type the Region:')
        region = str(sys.stdin.readline().strip())
        print('Enter Desired Instance Type: ')
        InstType = str(sys.stdin.readline().strip())
        print('Enter Desired Number of Elastic IPs for each EC2 Isntance: ')
        NIsIP = int(sys.stdin.readline().strip())
        print(f'selected Region: {region}, Instance Type: {InstType}, No of IP Address: {NIsIP}')
        ec2 = boto3.client('ec2',
            region_name= region,
            aws_access_key_id=Config.ACCESS_KEY,
            aws_secret_access_key=Config.SECRET_KEY
        )

        #getting VPC IDs of specific region
        subnets = ec2.describe_subnets()
        vpcs = ec2.describe_vpcs()
        subnetID = subnets['Subnets'][0]['SubnetId']
        vpcID = vpcs['Vpcs'][0]['VpcId']
        print(f'VPC ID: {vpcID}')

        #creating Security Group 
        sgGroupName = f'EC2_SG_{guid}'
        sgGroup = ec2.create_security_group(
            Description=f'Security group for {region} created in {vpcID} for EC2 Instances.',
            GroupName= sgGroupName,
            VpcId= vpcID
        )

        SGId = sgGroup['GroupId']
        print(f'Security Group ID: {SGId}')
        print('Creating EC2 Instance.....')
        rules = ec2.authorize_security_group_ingress(
            
            GroupId= SGId,
            GroupName= sgGroupName,
            IpPermissions=[
                {
                    'IpProtocol': '-1',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'allowing all traffics'
                        },
                    ]
                }
            ]
        )

        f = open('static.json')
        data = json.load(f)
        f.close()
        
        LaunchEC2 = ec2.run_instances(
            ImageId= data[region]['x86_64'],
            InstanceType= InstType,
            KeyName=Config.KeyName,
            MaxCount=1,
            MinCount=1,
            Monitoring={
                'Enabled': True
            },
            
            NetworkInterfaces=[{
                "DeleteOnTermination" : True,
                "DeviceIndex": 0,
                'Groups': [
                    SGId,
                ],
                'SecondaryPrivateIpAddressCount': int(NIsIP)-1,
                'SubnetId': subnetID
            }],
            #UserData='string',
            
            InstanceInitiatedShutdownBehavior='stop'
        )
        
        InstanceID = LaunchEC2['Instances'][0]['InstanceId']
        
        privateIPS = LaunchEC2['Instances'][0]['NetworkInterfaces'][0]['PrivateIpAddresses']
       
       
        ElasticIPs = []
        IPAdd = []
        print('Allocating Elastic IP Addresses.....')
        while i < int(NIsIP):
            AllocateIP = ec2.allocate_address(Domain='vpc')
            ElasticIPs.append(AllocateIP['AllocationId'])
            IPAdd.append(AllocateIP['PublicIp']) 
            i+=1 

        for j in range(0,1000):
            statusInstance = InstanceStatus(region, InstanceID)
            if statusInstance == 'running': 
                while n < NIsIP:
                    ec2.associate_address(
                        AllocationId=ElasticIPs[n],
                        InstanceId= InstanceID,
                        PrivateIpAddress= privateIPS[n]['PrivateIpAddress']
                    )
                    n+=1
                break

        print(f'EC2 Instance "{InstanceID}" Created  Attached - "{NIsIP}" Main Public IP Address: {IPAdd[0]} Primary Private IP Address: {privateIPS[0]} Public IP Addresses : {IPAdd} Private IP Addresses : {privateIPS}')

        return {
            "region" : region,
            "InstanceID" : InstanceID,
            "Private IP" : privateIPS,
            "Public IP" : IPAdd
        }
        
    except Exception as e:
	    print(f"exception {e}") 



def InstanceStatus(region, InstanceID):

    ec2 = boto3.client('ec2',
            region_name= region,
            aws_access_key_id=Config.ACCESS_KEY,
            aws_secret_access_key=Config.SECRET_KEY
        )
    response = ec2.describe_instance_status(
        InstanceIds=[
            InstanceID
        ]
    )
    
    if len(response['InstanceStatuses']) != 0:
        status = response["InstanceStatuses"][0]['InstanceState']["Name"]
    else: 
        status = 'pending'
    return status


if __name__ == "__main__":

    main()