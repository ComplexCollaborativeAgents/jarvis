## configure logging
import logging, coloredlogs
coloredlogs.DEFAULT_FIELD_STYLES = {'hostname': {'color': 'magenta'}, 'programname': {'color': 'cyan'}, 'name': {'color': 'blue'}, 'levelname': {'color': 'blue', 'bold': True}, 'asctime': {'color': 'cyan'}}
coloredlogs.install(level='INFO', fmt='%(asctime)s  %(levelname)s  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
