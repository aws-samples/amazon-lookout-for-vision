#!/bin/bash
# make sure you call warmup.py for the model before running this
while true
do
	echo "Press CTRL+C to stop the script execution"
	sudo chmod 777 /tmp/aws.iot.lookoutvision.EdgeAgent.sock
        python3 imts-client-demo-basler.py 21569614 aliensblog output.png	
done
