import logging as _logging
import os
import sys
import time
from pathlib import Path
import importlib

from aioxmpp import JID


def boot_agent(file: Path, jid: JID, properties: Path, logging:int, verify_security: bool):
    log_file_name = jid.localpart + ('_' + jid.resource if jid.resource else '')
    logs_path = os.path.join(str(file.parent.absolute()), 'logs')
    log_file = os.path.join(logs_path, log_file_name + '.log')

    os.makedirs(logs_path, exist_ok = True)
    _logging.basicConfig(filename=log_file, filemode='w', level=logging, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    try:
        _boot_agent(file, jid, properties, verify_security)
    except Exception as e:
        logger = _logging.getLogger('peak.mas.bootloader')
        logger.exception(e)
    except KeyboardInterrupt:
        pass


def _boot_agent(file: Path, jid: JID, properties: Path, verify_security: bool):
    logger = _logging.getLogger('peak.mas.bootloader')
    logger.debug('creating agent')
    agent_class = get_class(file)
    if properties:
        properties = get_class(properties)(jid.localpart)
        properties = properties.extract(jid.localpart)
    else:
        properties = None
    
    agent_instance = agent_class(jid, properties, verify_security)
    logger.info('starting agent')
    agent_instance.start(True).result()
    logger.info('agent started')
    while agent_instance.is_alive():
        try:
            time.sleep(1)
        except Exception as e:
            logger.error('AGENT CRACHED')
            logger.exception(e)
            logger.info('stoping agent... (Exception)')
            agent_instance.stop()
        except KeyboardInterrupt:
            logger.info('stoping agent... (Keyboard Interrupt)')
            agent_instance.stop()
    else:
        logger.info('clean exit')


def get_class(file: Path):
    module_path, module_file = os.path.split(file.absolute())
    module_name = module_file.split('.')[0]
    sys.path.append(module_path)
    module = importlib.import_module(module_name)
    return getattr(module, module_name)
