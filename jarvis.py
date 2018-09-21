import sys
import xmlrpclib
import soar_interface
import soar_interface.soar_state_server
from soar_interface.soar_agent import update
import json
import argparse
from log_config import logging


### read in the config file
CONFIG_FILE = "config.json"
with open(CONFIG_FILE) as config_file:
    try:
        config = json.load(config_file)
    except ValueError, e:
        logging.fatal("[soar_client] :: Invalid json at %s; error = %s" % (CONFIG_FILE, e))
        sys.exit()


def create_connection_with_tracker():
    url = 'http://{}:{}'.format(config['Servers']['input_host'], config['Servers']['input_port'])
    server = xmlrpclib.ServerProxy(url)
    logging.info("[soar_client] :: Created a connection to the tracker server at: {}".format(url))
    return server


def create_and_run_myserver(soar_agent):
    soar_server = soar_interface.soar_state_server.soar_state_server(soar_agent, port=config['Servers']['output_port'])
    soar_server.run_in_background()


def create_and_start_coach(tracker_server):
    coach = soar_interface.soar_agent.soar_agent(config, 'soar-coach', tracker_server)
    logging.info("[soar_client] :: Created ARA Soar coach")
    coach.register_output_callback(update, coach)
    logging.info("[soar_client] :: Started coaching agent")
    coach.start()
    coach.stop()
    return coach


if __name__ == '__main__':
    tracker_server = create_connection_with_tracker()
    coach = create_and_start_coach(tracker_server)
    create_and_run_myserver(coach)