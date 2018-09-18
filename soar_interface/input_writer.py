from soar_agent import sml
import xmlrpclib, time, sys
import json, logging



class input_writer(object):
    def __init__(self, soar_agent, config, tracker_server):
        self._soar_agent = soar_agent
        self._config = config
        self._input_link = soar_agent.get_input_link()
        self.new_interactions = []
        self.tracker_server = tracker_server
        self.set_time = None
        self.input_vars = self.load_input_vars_file()
        self.input_vars_id_map = {}
        self.timestamp = 0

        self._world_link = self._input_link.CreateIdWME("world")
        self._interaction_link = self._input_link.CreateIdWME("interaction")


    def load_input_vars_file(self):
        input_vars_file = self._config['SoarAgent']['input_vars']
        with open(input_vars_file) as ivars:
            try:
                input_vars = json.load(ivars)
            except ValueError, e:
                logging.fatal("[soar_runner] :: Invalid json at %s; error = %s" % (input_vars_file, e))
                sys.exit()
        return input_vars

    def generate_input(self):
        time.sleep(self._config['Soar']['sleep-time'])
        self.timestamp, current_state_list = self.tracker_server.get_all_since(self.timestamp)
        self.write_time_to_input_link()
        self.write_world_info_to_input_link(current_state_list)
        if len(self.new_interactions) > 0:
            self.write_interaction_to_input_link()

    def write_interaction_to_input_link(self):
        self.delete_all_children(self._interaction_link)
        logging.debug("[input_writer] :: writing interactions {}".format(self.new_interactions))
        if len(self.new_interactions) > 0:
            for interaction in self.new_interactions:
                self._interaction_link.CreateStringWME("request", interaction)
        self.new_interactions = []

    def write_time_to_input_link(self):
        time_WME = self._input_link.FindByAttribute("time", 0)
        if time_WME is not None:
            time_WME.DestroyWME()
        self._input_link.CreateStringWME("time", str(self.timestamp))

    def write_world_info_to_input_link(self, current_state_list):
        #print(current_state_list)
        for input_var in self.input_vars["variable_list"]:
            input_var_name = str(input_var["name"])
            input_states = input_var["states"]

            for state in input_states:
                key = (input_var_name + " " + str(state)).replace("-", " ").title()

                if input_var_name == "toner-cartridge-lock":
                    value = current_state_list.get(str(state).title())
                else:
                    value = current_state_list.get(key)


                logging.debug("[input_writer] :: {}:{}".format(key, value))
                if value is not None:
                    var_id = self.input_vars_id_map.get(input_var_name)
                    logging.debug("[input_writer] :: writing component {}".format(input_var_name))
                    if var_id is None:
                        var_id = self._world_link.CreateIdWME("component")
                        var_id.CreateStringWME("name", input_var_name)
                        #print(self.input_vars_id_map)
                        self.input_vars_id_map[input_var_name] = var_id
                        # print(input_var_name, var_id)
                        # print(self.input_vars_id_map)

                    attribute_name = str(state).replace(" ", "_").lower()

                    found_state_attribute = False
                    for i in range (0, var_id.GetNumberChildren()):
                        child = var_id.GetChild(i)
                        if child is not None:
                            attribute = child.GetAttribute()
                            if attribute == str(state):
                                found_state_attribute = True
                                state_id = child.ConvertToIdentifier()
                                state_id.GetChild(0).DestroyWME()
                                state_id.CreateStringWME("confidence", str(round(value[1],2)))

                    if found_state_attribute == False:
                        #print value[1]
                        state_id = var_id.CreateIdWME(attribute_name)
                        state_id.CreateStringWME("confidence", str(round(value[1],2)))
                else:
                    var_id = self.input_vars_id_map.get(input_var_name)
                    if var_id is not None:
                        attribute_name = str(state).replace(" ", "_").lower()
                        for i in range(0, var_id.GetNumberChildren()):
                            child = var_id.GetChild(i)
                            if child is not None:
                                attribute = child.GetAttribute()
                                if attribute == str(state):
                                    child.DestroyWME()

        ### remove every non-perceptible component from the list
        self.remove_components_not_visible(current_state_list, input_states)

    def remove_components_not_visible(self, current_state_list, input_states):
        for var_name in self.input_vars_id_map.keys():
            # print var_name
            for var_item in self.input_vars.get("variable_list"):
                if var_item["name"] == var_name:
                    input_states = var_item["states"]
            found_var = False
            for state in input_states:
                key = (var_name + " " + str(state)).replace("-", " ").title()
                if var_name == "toner-cartridge-lock":
                    value = current_state_list.get(str(state).title())
                else:
                    value = current_state_list.get(key)
                # print(key, value)
                if value is not None:
                    found_var = True
            if found_var is False:
                # print("removing {}".format(var_name))
                var_id = self.input_vars_id_map[var_name]
                self.delete_all_children(var_id)
                var_id.DestroyWME()
                del self.input_vars_id_map[var_name]

    def delete_all_children(self, id):
        index = 0
        if id.GetNumberChildren is not None:
            for i in range(0, id.GetNumberChildren()):
                child = id.GetChild(index)  # remove the 0th child several times, Soar kernel readjusts the list after an item is deletd
                if child is not None:
                    child.DestroyWME()
        #self._soar_agent.commit()