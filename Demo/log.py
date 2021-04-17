import logging
import logging.config
import flask

APP_NAME = 'flask.app'


def set_logger(app: flask.Flask):
    print(f"Initializing logger, name {APP_NAME}")
    app.logger = logging.getLogger(APP_NAME)
    if app.config.get("LOG_CONFIG", False):
        logging.config.dictConfig(app.config.get("LOG_CONFIG"))
        app.logger.info("logger initialized using LOG_CONFIG from config file")
    else:
        app.logger.info("logger initialized using default settings")
