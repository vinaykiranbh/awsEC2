import os

keyfile = 'newvinay.pem'
keyname = keyfile[:-4]
NewKeyName = "newKeyNAme"  #this will be keyname in AWS

os.system(f'ssh-keygen -y -f {keyfile} > {keyname}.pub')
os.system("AWS_REGIONS='$(aws ec2 describe-regions --query 'Regions[].RegionName' --output text)'")
os.system("for each_region in ${AWS_REGIONS} ; do aws ec2 import-key-pair --key-name {NewKeyName} --public-key-material fileb://{keyname}.pub --region $each_region ; done")