#!/bin/bash
wget -O- https://apt.corretto.aws/corretto.key | sudo apt-key add - 
sudo add-apt-repository 'deb https://apt.corretto.aws stable main'
sudo apt-get update; sudo apt-get install -y java-1.8.0-amazon-corretto-jdk
java -version
curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip > greengrass-nucleus-latest.zip
unzip greengrass-nucleus-latest.zip -d GreengrassCore && rm greengrass-nucleus-latest.zip

# Export access key and secret key

sudo -E java -Dlog.store=FILE \
  -jar ./GreengrassCore/lib/Greengrass.jar \
  --aws-region us-east-1 \
  --root /greengrass/v2 \
  --thing-name l4vEdgeDemoThing \
  --thing-group-name l4vEdgeDemoGroup \
  --tes-role-name MyGreengrassV2Role \
  --tes-role-alias-name MyGreengrassCoreTokenExchangeRoleAlias \
  --component-default-user ggc_user:ggc_group \
  --provision true \
  --setup-system-service true

sudo chmod 755 /greengrass/v2 && sudo chmod 755 /greengrass
