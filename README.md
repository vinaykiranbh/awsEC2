1. Change keys in config.py and make sure all the files are in same folder. 
2. Script will display list of regions available
3. need to enter the region (for example: us-east-1), you need to enter the Instance Type, for exmaple : t2.small or t4g.xlarge, and no of IP addresses required. 
4. script will check for whether this region is valid and has centos 7 AMI available
5. script will then get the VPCId of the region entered 
6. Security Group is created for rules (ALL TRAFFIC)
7. Instance will be created and security groups are attached to Instance
8. Elastic IP address is allocated and ready to associate to Instance for each private IP address
9. Script will check for Instance Status. if it's in running state, it will attach the elastic ip address to the instance.
10. Lastly, script prints the Instance ID, Elastic IP address (public). 



To use the same keypair for all regions. You below commands. 

1. ssh-keygen -y -f keypair.pem > keypair.pub

Replace keypair.pem with your file name. If it is kimhay.pem then command will be 

ssh-keygen -y -f kimhay.pem > kimhay.pub


2. AWS_REGIONS='$(aws ec2 describe-regions --query 'Regions[].RegionName' --output text)'

This command will get all the regions from cli and save it to AWS_REGIONS

3. setopt shwordsplit

This command is used to activate shell looping 


4. for each_region in ${AWS_REGIONS} ; do aws ec2 import-key-pair --key-name NewKeyName --public-key-material fileb://kimhay.pub --region $each_region ; done



Replace: 

i) NewKeyName with the keyname u want to set in AWS 
ii) File://kimhay.pub 


Above 4 commands, will import key pairs to all the regions. 


Replace the NewKeyName in config.py

