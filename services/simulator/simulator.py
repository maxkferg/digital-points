import os
import math
import time
import yaml
import json
import urllib
import shutil
import logging
import argparse
from graphqlclient import GraphQLClient
from graphql import getCurrentGeometry
from environment import Environment
from kafka import KafkaProducer, KafkaConsumer
from robots.robot_models import Turtlebot
from robots.robot_messages import get_odom_message

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

parser = argparse.ArgumentParser(description='Simulate robot movement.')
parser.add_argument('--headless', action='store_true', help='run without GUI components')



class Simulator():
    """
    Simulate physics using the model geometry.
    Pulls Model Geometry from GraphQL API, continuously run physics simulations
    
    Listens to control commands for each object in Kafka
    Publishes updated object locations to Kafka
    """


    def __init__(self, env, config):
        self.env = env
        self.robots = {}
        self.graphql_endpoint = config["API"]["host"]
        self.geometry_endpoint = config["Geometry"]["host"]
        self.graphql_client = GraphQLClient(self.graphql_endpoint)
        self.kafka_consumer = self._setup_kafka_consumer(config["Kafka"]["host"])
        self.kafka_producer = self._setup_kafka_producer(config["Kafka"]["host"])
        self._setup_geometry()
        self.env.start()


    def _setup_kafka_consumer(self, bootstrap_servers):
        topic = "robot.commands.velocity"
        return KafkaConsumer(topic, bootstrap_servers=bootstrap_servers)


    def _setup_kafka_producer(self, bootstrap_servers):
        return KafkaProducer(bootstrap_servers=bootstrap_servers)


    def _setup_geometry(self):
        result = self.graphql_client.execute(getCurrentGeometry)
        result = json.loads(result)
        for mesh in result['data']['meshesCurrent']:
            logging.info('Loading {}'.format(mesh['name']))
            relative_url = os.path.join(mesh['geometry']['directory'], mesh['geometry']['filename'])
            relative_url = relative_url.strip('./')
            position = [mesh['x'], mesh['y'], mesh['z']]
            is_stationary = mesh['physics']['stationary']
            mesh_id = mesh['id']
            if mesh['type']=='robot':
                self.robots[mesh_id] = self._setup_turtlebot(position)
            else:
                url = os.path.join(self.geometry_endpoint, relative_url)
                fp = os.path.join('tmp/', relative_url)
                self._download_geometry_resource(url, fp)
                self.env.load_geometry(fp, position, scale=mesh["scale"], stationary=is_stationary)


    def _setup_turtlebot(self, position):
        position[2] = max(0,position[2])
        physics = {}
        config = {
            "is_discrete": False,
            "initial_pos": position,
            "target_pos": [0,0,0],
            "resolution": 0.05,
            "power": 1.0,
            "linear_power": float(os.environ.get('LINEAR_SPEED', 50)), 
            "angular_power": float(os.environ.get('ANGULAR_SPEED', 10)), 
        }
        logging.info("Creating Turtlebot at: {}".format(position))
        turtlebot = Turtlebot(physics, config)
        turtlebot.set_position(position)
        return turtlebot

    def _download_geometry_resource(self, url, local_filepath):
        """
        Download the file from `url` and save it locally under `file_name`
        """
        logging.info("{} -> {}".format(url, local_filepath))
        os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
        with urllib.request.urlopen(url) as response, open(local_filepath, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)


    def _publish_robot_states(self):
        for robot_id, robot in self.robots.items():
            state = robot.get_state()
            position = state["position"]
            orientation = state["orientation"]
            message = get_odom_message(robot_id, position, orientation)
            message = json.dumps(message).encode('utf-8')
            future = self.kafka_producer.send('robot.events.odom', message)
            logging.info("Sent robot.events.odom message for robot %s"%robot_id)


    def run(self):
        logging.info("\n\n --- Starting simulation loop --- \n")
        linear_velocity = 0
        angular_velocity = 0
        start = time.time()
        steps = 0
        
        while True:
            result = self.kafka_consumer.poll()
            for partition, messages in result.items():
                for msg in messages:
                    command = json.loads(msg.value)
                    robot_id = command["robot"]["id"]
                    linear_velocity = command["velocity"]["linear"]["x"]
                    angular_velocity = command["velocity"]["angular"]["z"]
                    action = (angular_velocity, linear_velocity)
                    if not robot_id in self.robots:
                        logging.error("No robot with id %s"%robot_id)
                    else:
                        robot = self.robots[robot_id]
                        robot.applyAction(action)
                        logging.info("Robot {} action {}".format(robot_id, action))

            self.env.step()
            steps+=1

            # Push robot position at about 20 Hz
            if steps%24==0:
                self._publish_robot_states()

            # Try and maintain 240 FPS to match the bullet simulation speed
            duration = time.time()-start
            fps = steps/duration
            if fps<240:
                self.env.step()
                steps +=1
            if fps>240:
                time.sleep(max(0, steps/240-duration))
            if steps%240==0:
                logging.info("Current simulation speed  {:.3f}".format(fps))



if __name__=="__main__":
    args = parser.parse_args()
    with open('config.yaml') as cfg:
        config = yaml.load(cfg, Loader=yaml.Loader)
    env = Environment(headless=args.headless)
    simulator = Simulator(env, config)
    simulator.run()



