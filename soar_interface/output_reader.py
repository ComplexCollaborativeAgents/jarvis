from soar_agent import sml
import logging
import random
import json
import soar_agent


class output_reader(object):
    def __init__(self, soar_agent, config):
        self._soar_agent = soar_agent
        self._config = config
        self.response = None

    def read_output(self):
        number_of_commands = self._soar_agent._agent.GetNumberCommands()
        output_dict = {}
        for i in range(0, number_of_commands):
            commandID = self._soar_agent._agent.GetCommand(i)
            commandName = commandID.GetAttribute()
            if commandName == "state":
                output_dict['state'] = self.process_state_description(commandID)
            if commandName == "next-instruction":
                output_dict['next-instruction'] = self.processNextInstruction(commandID)
            commandID.AddStatusComplete()
        #print("output is {}".format(output_dict))
        self.response = output_dict

    def process_state_description(self, commandID):
        state_list = []
        #print("generating state description")
        for i in range(0, commandID.GetNumberChildren()):
            component_dict = {}
            componentID = commandID.GetChild(i).ConvertToIdentifier()
            if componentID.GetAttribute() == "component":
                for j in range(0, componentID.GetNumberChildren()):
                    child = componentID.GetChild(j)
                    attribute = child.GetAttribute()
                    value = child.GetValueAsString()
                    component_dict[attribute] = value
                #print(component_dict)
                state_list.append(component_dict)
        return state_list

    def processNextInstruction(self, commandID):
        dict = {}
        for i in range(0, commandID.GetNumberChildren()):
            child = commandID.GetChild(i)
            if child.GetAttribute() == 'action':
                dict['action'] = child.GetValueAsString()
            if child.GetAttribute() == 'component':
                dict['component'] = child.GetValueAsString()

        #self._soar_agent._input_writer.new_interactions.remove('get-next-instruction')
        return dict