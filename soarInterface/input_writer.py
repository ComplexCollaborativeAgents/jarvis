from soar_agent import sml
import xmlrpclib, time, sys
import json, logging





class input_writer(object):
    def __init__(self, soar_agent, config, tracker_server):
        self._soar_agent = soar_agent
        self._config = config
        self._input_link = soar_agent.get_input_link()
        #self.to_write = None
        self.tracker_server = tracker_server
        self.set_time = None
        self.input_vars = self.load_input_vars_file()
        self.input_vars_id_map = {}
        self.create_input_link_ids()

    def create_input_link_ids(self):
        for input_var in self.input_vars["variable_list"]:
            input_var_name = str(input_var["name"])
            self.input_vars_id_map[input_var_name] = self._input_link.CreateIdWME(input_var_name)


    def load_input_vars_file(self):
        input_vars_file = self._config['SoarAgent']['input_vars']
        with open(input_vars_file) as ivars:
            try:
                input_vars = json.load(ivars)
            except ValueError, e:
                logging.fatal("[soar_client] :: Invalid json at %s; error = %s" % (input_vars_file, e))
                sys.exit()
        return input_vars

    def generate_input(self):
        # put a sleep here so that the start/stop from the Python app works smoothly
        # Should be removed, when in production
        # maybe should be put in a config
        #time.sleep(self._config['Soar']['sleep-time'])
        #
        # if self.to_write is not None:
        #     self.write_data_to_input_link(self.to_write)
        #     self.to_write = None
        self.write_data_to_input_link()

    def update_time(self):
        pass

    def clear_interaction_link(self):
        self.delete_all_children(self._interaction_id)

    def clear_input_link(self):
        self.delete_all_children(self._input_link)

    def reset_input_link(self):
        self.delete_all_children(self._input_link)
        self._interaction_id = self._input_link.CreateIdWME("response")

    def write_data_to_input_link(self):
        current_state_list = self.tracker_server.get_all()
        #print current_state_list
        for input_var in self.input_vars["variable_list"]:
            input_var_name = str(input_var["name"])
            input_states = input_var["states"]
            var_id = self.input_vars_id_map[input_var_name]
            self.delete_all_children(var_id)
            for state in input_states:
                key = input_var_name + "_" + str(state)
                value = current_state_list.get(key)
                if value is not None:
                    var_id.CreateStringWME(str(state), str(value))

    def write_data_to_identifier(self, id, data):
        object = data
        for key in object:
            value = object[key]
            if isinstance(value, int):
                id.CreateIntWME(str(key), value)
            elif isinstance(value, (str, unicode)):
                id.CreateStringWME(str(key), str(value))
            elif isinstance(value, float):
                id.CreateFloatWME(str(key), value)
            else:
                subid = id.CreateIdWME(str(key))
                self.write_data_to_identifier(subid, value)

    def delete_all_children(self, id):
        index = 0
        if id.GetNumberChildren is not None:
            for i in range(0, id.GetNumberChildren()):
                child = id.GetChild(
                    index)  # remove the 0th child several times, Soar kernel readjusts the list after an item is deletd
                if child is not None:
                    child.DestroyWME()
        self._soar_agent.commit()
