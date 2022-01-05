# Calculate Inference Units for Lookout for Vision Model

Please refer to the blog https://aws.amazon.com/blogs/machine-learning/calculate-inference-units-for-an-amazon-rekognition-custom-labels-model/

## Steps:

## Start your model

After your model is trained, start the model with 1 Inference Unit. You can use the following command from the AWS Command Line Interface (AWS CLI) to start your model:

```
aws lookoutvision start-model \
  --project-name <PROJECT NAME> \
  --model-version <MODEL VERSION> \
  --min-inference-units 1 \
  --region < REGION >

```

## Launch an EC2 instance and set up your test environment

Launch an EC2 instance that you use to run a script that uses a sample image to call the model we started in the previous step. You can follow the steps in the [quick start guide](https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html) to launch an EC2 instance. Although the guide uses an instance type of t2.micro, you should use a compute-optimized instance type such as C5 to run this test.

After you connect to the EC2 instance, run the following commands from the terminal to install the required dependencies:

```
sudo yum install python3
sudo yum install gcc
sudo yum install python3-devel
sudo pip3 install locust
sudo pip3 install boto3

```


## Run the test script 

```

python3 ./tps.py --images ./images --project-name < PROJECT NAME > --region < REGION > --model-version < MODEL VERSION >

```