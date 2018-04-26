from soar_agent import sml
import logging
import random
import json


class output_reader(object):
    def __init__(self, soar_agent, config):
        self._soar_agent = soar_agent
        self._config = config

    def read_output(self):
        number_of_commands = self._soar_agent._agent.GetNumberCommands()
        for i in range(0, number_of_commands):
            commandID = self._soar_agent._agent.GetCommand(i)
            commandName = commandID.GetAttribute()
            if commandName == "instruction":
                action = commandID.GetParameterValue("action")
                component = commandID.GetParameterValue("component")
                message = action + " " + component
                logging.info("[output_writer] :: instruction - \"%s\"" % message)
                self.compose_and_post_message(commandID)
            commandID.AddStatusComplete()
        pass

    def compose_and_post_message(self, command_id):
        pass

    def post_to_application(self, response_json):
        pass
