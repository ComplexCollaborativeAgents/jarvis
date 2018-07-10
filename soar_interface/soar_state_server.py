from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib
from log_config import logging
from threading import Thread
import socket

class soar_state_server:

    def __init__(self, soar_agent, port = 10000):
        logging.info("[soar_state_server] :: Soar state server connecting on port {}".format(port))

        self.quit = True
        self.port = port
        self.soar_agent = soar_agent

        # Restrict to a particular path
        class RequestHandler(SimpleXMLRPCRequestHandler):
            rpc_paths = ('/RPC2',)

        # Create server

        self.host = socket.gethostbyname("0.0.0.0")
        logging.info("[soar_state_server] :: hostname: " + self.host)

        self.server = SimpleXMLRPCServer( (self.host, self.port),
                                          requestHandler=RequestHandler)

        self.server.register_introspection_functions()


        def get_all():
            logging.debug("[soar_server] :: received get_all from client")
            return soar_agent.get_all()

        def get_all_predicates():
            return soar_agent.get_all_predicates()

        def get_next_instruction():
            logging.info("[soar_state_server] :: requesting next instruction from agent")
            return soar_agent.get_next_instruction()

        def dummy():
            logging.info("[soar_state_server] :: server ending.")

        self.server.register_function(get_all, 'get_all')
        self.server.register_function(get_all_predicates, 'get_all_predicates')
        self.server.register_function(get_next_instruction, 'get_next_instruction')

    def run(self):
        while not self.quit:
            self.server.handle_request()


    def run_in_background(self):
        self.quit = False
        logging.info("[soar_state_server] :: Starting soar server")
        self.thread = Thread(target = self.run, args=())
        self.thread.start()

    def stop(self):
        self.quit = True

        url = 'http://{}:{}'.format(self.host, self.port)
        s = xmlrpclib.client.ServerProxy(url)
        s.dummy()

        print("Done")
