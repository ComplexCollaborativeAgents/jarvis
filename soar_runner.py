import sys
import xmlrpclib
import soar_interface
from soar_interface.soar_agent import update
from application import application
import json
import argparse

## configure logging
import logging, coloredlogs
coloredlogs.DEFAULT_FIELD_STYLES = {'hostname': {'color': 'magenta'}, 'programname': {'color': 'cyan'}, 'name': {'color': 'blue'}, 'levelname': {'color': 'blue', 'bold': True}, 'asctime': {'color': 'cyan'}}
coloredlogs.install(level='DEBUG', fmt='%(asctime)s  %(levelname)s  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


### read in the config file
CONFIG_FILE = "config.json"
with open(CONFIG_FILE) as config_file:
    try:
        config = json.load(config_file)
    except ValueError, e:
        logging.fatal("[soar_client] :: Invalid json at %s; error = %s" % (CONFIG_FILE, e))
        sys.exit()

def parse_server_arguments():
    parser = argparse.ArgumentParser(description='Single Shot MultiBox Detection')
    parser.add_argument('--host', default='localhost', type=str,
                        help='hostname for remote event queries')
    parser.add_argument('--port', default=28000, type=int,
                        help='socket port# for event state queries')
    args = parser.parse_args()
    return args

def create_connection_with_tracker():
    args = parse_server_arguments()
    url = 'http://{}:{}'.format(args.host, args.port)
    tracker_server = xmlrpclib.ServerProxy(url)
    logging.info("[soar_client] :: Created a connection to the tracker server.")
    return tracker_server


def create_and_start_coach(tracker_server):
    coach = soar_interface.soar_agent.soar_agent(config, 'soar-coach', tracker_server)
    logging.info("[soar_client] :: Created ARA Soar coach")
    coach.register_output_callback(update, coach)
    logging.info("[soar_client] :: Started coaching agent")
    return coach




def run_application(coach):
    app = application.Application(coach)
    app.master.title("Soar agent")
    app.mainloop()

if __name__ == '__main__':
    tracker_server = create_connection_with_tracker()
    coach = create_and_start_coach(tracker_server)
    run_application(coach)