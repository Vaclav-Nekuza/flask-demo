import typing
from flask import Flask
from flask_restx import Api

from . import log
from .db import DB
from .models import ns_demo
from .web.person import *
from .web.address import *

app_version = [0, 1, 0]


class Demo(Flask):
    version: typing.List[int]
    api: Api
    contact_email: str
    contact_url: str
    db: DB

    def __init__(
            self,
            *args,
            version: typing.Optional[typing.List[int]] = None,
            contact_email: typing.Optional[str] = None,
            **kwargs,
    ) -> None:
        super(Demo, self).__init__(*args, **kwargs)
        self.version = version or [1, 0, 0]
        self.contact_email = contact_email or "Vaclav.Nekuza@outlook.com"

        # setup from default config file
        self.config.from_pyfile('../config.py')
        # setup from local config file, rewriting default setup
        self.config.from_pyfile('/etc/demo/config.py', silent=True)

        # logger setup
        log.set_logger(self)

        # flask_restx setup
        self.api = Api(app=self)
        self.api.add_namespace(ns_demo)

        # database setup
        self.logger.info('Connecting to database')
        self.db = DB(self.config['DB_CONN'], self.config["SCHEMA_NAME"], self.logger)

    def dispose(self):
        self.db.dispose()


app: Demo
app = Demo(__name__, version=app_version)

app.dispose()
