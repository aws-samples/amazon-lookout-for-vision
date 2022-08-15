# Lookout for Vision Workshop Edge Components

Amazon Lookout for Vision is a machine learning (ML) service that spots defects and anomalies in visual representations using computer vision (CV). With Amazon Lookout for Vision, manufacturing companies can increase quality and reduce operational costs by quickly identifying differences in images of objects at scale. This workshop is intended to run through an end to end example of using the boto3 python SDK to train and host Lookout for Vision models. For a console-only getting started guide, see https://docs.aws.amazon.com/lookout-for-vision/latest/developer-guide/getting-started.html

The components in this directory allow you to use real-time inference and get segmentation results via CPU or GPU systems. Files ending with -file.py use static images from the local filesystem, and components ending in -mqtt.py are also intergrated with AWS IoT Core via MQTT messages of inference results. Scripts including the name 'basler' require Basler GigE cameras.

## Steps:
 - Go to the workshop labs at https://catalog.us-east-1.prod.workshops.aws/workshops/cbfb2625-416f-45e3-88b2-b68a1d25dab2/en-US
 - Go to labs 3,4 or 5 depending on your use case
