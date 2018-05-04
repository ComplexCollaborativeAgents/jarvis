import os, sys, logging, json

CONFIG_FILE = "config.json"
with open(CONFIG_FILE) as config_file:
    try:
        config = json.load(config_file)
    except ValueError, e:
        logging.fatal("[soar_client] :: Invalid json at %s; error = %s" % (CONFIG_FILE, e))
        sys.exit()
    try:
        sys.path.append(config['Soar']['path'])

        import Python_sml_ClientInterface as sml
    except ValueError, e:
        logging.fatal("[soar_client] :: Cannot find local soar installation")

#import Python_sml_ClientInterface as sml
from threading import Thread
import time
import output_reader, input_writer
import random




class soar_agent(object):
    def __init__(self, config, username, tracker_server):
        self._config = config
        self._username = username

        ## create Soar kernel, agent, load rules

        self._kernel = self.create_kernel()
        self._agent = self.create_agent(str(self._config['SoarAgent']['name']))
        self._agentFilepath = str(self._config['SoarAgent']['file'])
        self.load_agent_rules(self._agentFilepath)
        self._input_link = self._agent.GetInputLink()
        self._output_link = self._agent.GetOutputLink()
        self._input_writer = input_writer.input_writer(self, config, tracker_server)
        self._output_reader = output_reader.output_reader(self, config)

        ## init state maintenance data structures
        self.stop_requested = False
        self._agent_thread = None
        self._is_running = False

    def create_kernel(self):
        kernel = sml.Kernel.CreateKernelInNewThread(random.randint(40000, 60000))
        if not kernel or kernel.HadError():
            logging.error("[soar_agent] :: Error creating kernel: " + kernel.GetLastErrorDescription())
            exit(1)

        return kernel

    def create_agent(self, agent_name):
        agent = self._kernel.CreateAgent(agent_name)
        if not agent:
            logging.error("[soar_agent] :: Error creating agent: " + self.kernel.GetLastErrorDescription())
            exit(1)
        return agent

    def load_agent_rules(self, agentFile):
        logging.info("[soar_agent] :: Loading agent at %s" % agentFile)
        self._agent.LoadProductions(os.path.realpath(agentFile));

    def run_SoarJavaDebugger(self):
        self._agent.SpawnDebugger(self._kernel.GetListenerPort())

    def register_output_callback(self, function, caller_object=None):
        self._agent.RegisterForRunEvent(sml.smlEVENT_AFTER_OUTPUT_PHASE, function, caller_object, True)

    def run_till_output(self):
        self._agent.RunSelfTilOutput()

    def run_forever(self):
        self._agent.RunSelfForever()

    def get_input_link(self):
        return self._input_link

    def get_output_link(self):
        return self._output_link

    def commit(self):
        self._agent.Commit()

    def shutdown(self):
        self.stop_requested = True
        self._agent.KillDebugger()
        # self._kernel.DestroyAgent(self._agent)
        self._kernel.Shutdown()

    def quit(self):
        self.stop_requested = True
        self._agent.KillDebugger()

    def check_for_incoming_events(self):
        self._kernel.CheckForIncomingEvents()

    def execute_command(self, command):
        time.sleep(self._config['Soar']['sleep-time'])
        self._agent.ExecuteCommandLine(command);

    def set_time(self, week, day):
        self._input_writer.set_time = {'week': week, 'day': day}

    def start(self):
        if (self._is_running):
            return
        self._is_running = True
        self._agent_thread = Thread(target=self.execute_command, args=("run",))
        self._agent_thread.start()
        logging.info("[soar_agent] :: spun-off agent thread.")

        ## start debugger
        if self._config["RunParams"]["run_mode"] == "debug":
            self.run_SoarJavaDebugger()

    def stop(self):
        self.stop_requested = True

    def step(self):
        self.execute_command("step")

    def stop_agent_if_requested(self):
        if self.stop_requested is True:
            logging.info("[soar_agent] :: stopping agent")
            self.execute_command("stop")
            self._is_running = False
            self.stop_requested = False

    def get_all(self):
        self._input_writer.new_interaction = "get-all"
        while self._output_reader.response is None:
            pass
        response = self._output_reader.response
        self._output_reader.response = None
        logging.debug("[soar_agent] :: state is {}".format(response))
        return response

def update(mid, this_agent, agent, message):
    this_agent.stop_agent_if_requested()
    this_agent._output_reader.read_output()
    this_agent._input_writer.generate_input()