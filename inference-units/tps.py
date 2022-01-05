from os import walk
import inspect
import time
import functools

import gevent.monkey

gevent.monkey.patch_all()

import argparse
from pathlib import Path
import boto3 as boto3
from botocore.config import Config
from locust import task, constant_pacing, events, LoadTestShape
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
from locust import User

setup_logging("INFO", None)

'''
This script will:
1. Read list of images from a base path
2. Run step load
3. Print the stats
4. Stop runs when non-zero faliure rate is observed
5. Use last run to calculate maximum TPS
'''

image_base_path = None
project_name = None
aws_region = None
model_version = None

class WebserviceUser(User):

    wait_time = constant_pacing(0)

    def __init__(self, *args, **kwargs):
       
        for (dirpath, dirnames, filenames) in walk(image_base_path):
            self.images = [Path(image_base_path) / filename for filename in filenames]
            break
        super(WebserviceUser, self).__init__(*args, **kwargs)
        config = Config(
            retries={
                'max_attempts': 1,
                'mode': 'standard'
            }
        )
        self.client = boto3.client(
            'lookoutvision',
            aws_region,
            config=config
        )

        def detection_tests(image_path, arg):
            try:
                start_time = time.time()
                with open(image_path, 'rb') as image:
                    r = self.client.detect_anomalies(ProjectName=project_name, ContentType='image/jpeg',Body=image.read(), ModelVersion=model_version)
            except Exception as exception:
                total_time = int((time.time() - start_time) * 1000)
                self.environment.events.request_failure.fire(request_type="GET",
                                                             name=inspect.stack()[0][3], response_time=total_time,
                                                             response_length=0, exception=exception)
            else:
                total_time = int((time.time() - start_time) * 1000)
                self.environment.events.request_success.fire(request_type="GET", name=inspect.stack()[0][3],
                                                             response_time=total_time, response_length=0)

        self.tasks = [functools.partial(detection_tests, image) for image in self.images]

def run_load(user_count, spawn_rate):
    # setup Environment and Runner
    env = Environment(user_classes=[WebserviceUser])
    local_runner = env.create_local_runner()

    
    # start a greenlet that periodically outputs the current stats
    gevent.spawn(stats_printer(env.stats))

    # start a greenlet that save current stats to history
    gevent.spawn(stats_history, env.runner)

    # start the test
    env.runner.start(user_count, spawn_rate=spawn_rate)

    # in 60 seconds stop the runner
    gevent.spawn_later(30, lambda: env.runner.quit())

    # wait for the greenlets
    env.runner.greenlet.join()

    
    # Sleep so that history is up to date
    time.sleep(5)

    # NOTE: Max TPS calculated from last run. 
    last_stats = env.stats.history[-1]
    max_tps = last_stats['current_rps'] - last_stats['current_fail_per_sec']
    p95_latency = last_stats['response_time_percentile_95']
    failure_tps = last_stats['current_fail_per_sec']
    print(f'Max supported TPS: {max_tps}')
    print(f'95th percentile response time: {p95_latency}')
    return max_tps, p95_latency, failure_tps


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Script to find the max TPS supported by a project version')
    parser.add_argument('--images', type=str, help='path to folder with images', required=True)
    parser.add_argument('--project-name', type=str, help='Project Version arn to run loadtest against', required=True)
    parser.add_argument('--region', type=str, help='Project Version arn to run loadtest against', required=True)
    parser.add_argument('--model-version', type=str, help='Project Version arn to run loadtest against', required=True)

    args = parser.parse_args()
    image_base_path = args.images
    project_name = args.project_name
    aws_region = args.region
    model_version = args.model_version

    print(f'project name ={project_name}, region = {aws_region}, image path = {image_base_path}')

    user_count = 10
    failure_tps = 0
    # NOTE: If max TPS is not reached in 3 iterations the customer might be running with >1 IU
    max_iterations = 3
    # NOTE: Advanced users can replace with custom shape & LocalRunner to find maxima
    # https://docs.locust.io/en/stable/generating-custom-load-shape.html
    while failure_tps <= 0 and max_iterations >= 0:
        max_tps, p95_latency, failure_tps = run_load(user_count, user_count/10)
        user_count *= 2
        max_iterations -= 1
