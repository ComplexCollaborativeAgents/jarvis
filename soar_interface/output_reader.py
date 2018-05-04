from soar_agent import sml
import logging
import random
import json


class output_reader(object):
    def __init__(self, soar_agent, config):
        self._soar_agent = soar_agent
        self._config = config
        self.response = None

    def read_output(self):
        number_of_commands = self._soar_agent._agent.GetNumberCommands()
        output_list = []
        for i in range(0, number_of_commands):
            commandID = self._soar_agent._agent.GetCommand(i)
            commandName = commandID.GetAttribute()
            dict = {}
            if commandName == "component":
                for i in range(0, commandID.GetNumberChildren()):
                    child = commandID.GetChild(i)
                    attribute = child.GetAttribute()
                    value = child.GetValueAsString()
                    dict[attribute] = value
            commandID.AddStatusComplete()
            output_list.append(dict)
        self.response = output_list