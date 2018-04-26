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
        #self.create_input_link_ids()
        self.timestamp = 0

    # def create_input_link_ids(self):
    #     for input_var in self.input_vars["variable_list"]:
    #         input_var_name = str(input_var["name"])
    #         id = self._input_link.CreateIdWME(input_var_name)
    #         self.input_vars_id_map[input_var_name] = id
    #         id.CreateStringWME("name", input_var_name)
    #         id.CreateStringWME("type", "component")


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

    # def write_data_to_input_link(self):
    #     self.timestamp, current_state_list = self.tracker_server.get_all_since(self.timestamp)
    #     print(self.timestamp, current_state_list)
    #     for input_var in self.input_vars["variable_list"]:
    #         input_var_name = str(input_var["name"])
    #         input_states = input_var["states"]
    #         var_id = self.input_vars_id_map[input_var_name]
    #         for state in input_states:
    #             key = (input_var_name + " " + str(state)).replace("-", " ").title()
    #             value = current_state_list.get(key)
    #             if value is not None:
    #                 attribute_name = str(state).replace(" ", "_").lower()
    #                 value_name = "true"
    #
    #                 found_state_attribute = False
    #                 for i in range(0, var_id.GetNumberChildren()):
    #                     child = var_id.GetChild(i)
    #                     if child is not None:
    #                         attribute = child.GetAttribute()
    #                         a_value = child.GetValueAsString()
    #                         if attribute == str(state):
    #                             found_state_attribute = True
    #                             if a_value != str(value):
    #                                 child.DestroyWME()
    #                                 var_id.CreateStringWME(attribute_name, value_name)
    #                 if found_state_attribute == False:
    #                     var_id.CreateStringWME(attribute_name, value_name)

    def write_data_to_input_link(self):
        self.timestamp, current_state_list = self.tracker_server.get_all_since(self.timestamp)
        print(self.timestamp, current_state_list)

        ### add every perceptible components to the list
        for input_var in self.input_vars["variable_list"]:
            input_var_name = str(input_var["name"])
            input_states = input_var["states"]

            for state in input_states:
                key = (input_var_name + " " + str(state)).replace("-", " ").title()
                value = current_state_list.get(key)
                if value is not None:
                    var_id = self.input_vars_id_map.get(input_var_name)
                    #print("writing {}".format(input_var_name))
                    if var_id is None:
                        var_id = self._input_link.CreateIdWME("component")
                        var_id.CreateStringWME("name", input_var_name)
                        self.input_vars_id_map[input_var_name] = var_id

                    attribute_name = str(state).replace(" ", "_").lower()

                    found_state_attribute = False
                    for i in range (0, var_id.GetNumberChildren()):
                        child = var_id.GetChild(i)
                        if child is not None:
                            attribute = child.GetAttribute()
                            if attribute == str(state):
                                print "found attribute"
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
        for var_name in self.input_vars_id_map.keys():
            #print var_name
            for var_item in self.input_vars.get("variable_list"):
                if var_item["name"] == var_name:
                    input_states = var_item["states"]
            found_var = False
            for state in input_states:
                key = (var_name + " " + str(state)).replace("-", " ").title()
                value = current_state_list.get(key)
                #print(key, value)
                if value is not None:
                    found_var = True
            if found_var is False:
                #print("removing {}".format(var_name))
                var_id = self.input_vars_id_map[var_name]
                self.delete_all_children(var_id)
                var_id.DestroyWME()
                del self.input_vars_id_map[var_name]



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
                child = id.GetChild(index)  # remove the 0th child several times, Soar kernel readjusts the list after an item is deletd
                if child is not None:
                    child.DestroyWME()
        #self._soar_agent.commit()