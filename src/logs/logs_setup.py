import logging
import logging.config
import yaml
from enum import StrEnum

class LoggerEnv(StrEnum):
    DEV = "dev"
    PROD ="prod"

def init_logging():
    conf_dict = None
    with open("src/logs/logging_config.yaml", "rt") as conf:
        conf_dict = yaml.safe_load(conf.read())
    logging.config.dictConfig(conf_dict)
    
if __name__ == "__main__":
    init_logging()
    logger = logging.getLogger(LoggerEnv.DEV.value)
    logger.debug("Hello World")