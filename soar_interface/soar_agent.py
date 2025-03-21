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


from threading import Thread
import time
import output_reader, input_writer
import random


class soar_agent(object):
    def __init__(self, config, username, tracker_server):
        self._config = config
        self._username = username
        self.setup_soar_agent(tracker_server)
        self.init_state_maintenance_data_structures()

    def init_state_maintenance_data_structures(self):
        self.stop_requested = False
        self._agent_thread = None
        self._is_running = False

    def setup_soar_agent(self, tracker_server):
        self._kernel = self.create_kernel()
        self._agent = self.create_agent(str(self._config['SoarAgent']['name']))
        self._agentFilepath = str(self._config['SoarAgent']['file'])
        self.load_agent_rules(self._agentFilepath)
        self._input_link = self._agent.GetInputLink()
        self._output_link = self._agent.GetOutputLink()
        self._input_writer = input_writer.input_writer(self, self._config, tracker_server)
        self._output_reader = output_reader.output_reader(self, self._config)


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
        self.stop()
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
        self._input_writer.new_interactions.append({"name": "get-all"})
        while 'state' not in self._output_reader.response or len(self._output_reader.response['state']) <= 0:
            pass
        response = self._output_reader.response['state']
        del self._output_reader.response['state']
        logging.debug("[soar_agent] :: state is {}".format(response))
        return response

    def get_all_predicates(self):
        self._input_writer.new_interactions.append("get-all")
        while 'state' not in self._output_reader.response or len(self._output_reader.response['state']) <= 0:
            pass
        response = self._output_reader.response['state']
        del self._output_reader.response['state']
        predicate_response = self.convert_to_predicates(response)
        logging.debug("[soar_agent] :: predicates are {}".format(predicate_response))
        return predicate_response

    def convert_to_predicates(self, response):
        predicate_list = []
        for component in response:
            id = component['id']
            type = component['name']
            type_string = "type({},{})".format(id,type)
            predicate_list.append(type_string)
            if component['visible'] == 'true':
                visibility_string = "visible({})".format(id)
                predicate_list.append(visibility_string)

            if 'open' in component.keys():
                if component['open'] != 'false' and component['closed'] == 'false':
                    open_string = "open_state({}, {})".format(id, 'open')
                    predicate_list.append(open_string)
                if component['open'] == 'false' and component['closed'] != 'false':
                    open_string = "open_state({}, {})".format(id, 'closed')
                    predicate_list.append(open_string)

            if 'in' in component.keys():
                if component['in'] != 'false' and component['out'] == 'false':
                    in_string = "in_state({}, {})".format(id, 'in')
                    predicate_list.append(in_string)
                if component['in'] == 'false' and component['out'] != 'false':
                    in_string = "in_state({}, {})".format(id, 'out')
                    predicate_list.append(in_string)

            if 'locked' in component.keys():
                if component['locked'] != 'false' and component['unlocked'] == 'false':
                    locked_string = "locked_state({},{})".format(id, 'locked')
                    predicate_list.append(locked_string)
                if component['locked'] == 'false' and component['unlocked'] != 'false':
                    locked_string = "locked_state({},{})".format(id, 'unlocked')
                    predicate_list.append(locked_string)
        return predicate_list

    def get_next_instruction(self):
        self._input_writer.new_interactions.append({"name": "get-next-instruction"})
        while  'next-instruction' not in self._output_reader.response or len(self._output_reader.response['next-instruction']) <= 0:
            pass
        response = self._output_reader.response['next-instruction']
        del self._output_reader.response['next-instruction']
        logging.debug("[soar_agent] :: next-instruction is {}".format(response))
        return response

    def set_task(self, state, component):
        logging.debug("[soar_agent] :: asking to set task {}:{}".format(state, component))
        if state == 'remove' and component == 'toner_cartridge':
            self._input_writer.new_interactions.append({"name":"set-task", "task-name":"remove-toner-cartridge"})
        if state == 'remove' and component == 'drum_cartridge':
            self._input_writer.new_interactions.append({"name":"set-task", "task-name":"remove-drum-cartridge"})
        response = self._output_reader.response['set-task-ack']
        del self._output_reader.response['set-task-ack']
        logging.debug("[soar_agent] :: set-task-ack is {}".format(response))
        return response



def update(mid, this_agent, agent, message):
    this_agent.stop_agent_if_requested()
    this_agent._output_reader.read_output()
    this_agent._input_writer.generate_input()