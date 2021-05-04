import flask
from flask_restx import abort
from flask import current_app as app


class DemoExcept(Exception):

    def __init__(self, user_msg="", inter_msg="", http_code=404, err_code=1000):
        Exception.__init__(self)
        self.user_mgs = user_msg
        self.inter_msg = inter_msg
        self.http_code = http_code
        self.err_code = err_code

    def represent(self):
        return {"code": int(self.http_code),
                "message": str(self.user_mgs),
                "internal_message": str(self.inter_msg),
                "err_code": self.err_code}

    def abort(self):
        repr_dict = self.represent()
        # app.logger.debug(f"{str(repr_dict)}")
        abort(**repr_dict)

    def __str__(self, *args, **kwargs):
        return f"{type(self).__name__}({self.represent()})"


class EngineCreation(DemoExcept):
    def __init__(self, e=None):
        inter_msg = f"Error while creating an engine. "
        if e:
            inter_msg += str(e)
        if flask.has_app_context():
            app.logger.error(f"EngineCreation exception internal message: {inter_msg}")
        DemoExcept.__init__(self,
                            user_msg="Internal Error while establishing connection to database",
                            inter_msg=inter_msg,
                            http_code=500,
                            err_code=1001)


class DBDoesNotExist(DemoExcept):
    def __init__(self, db_name, user, e=None):
        inter_msg = f"Error while creating database. "
        if e:
            inter_msg += str(e)
        if flask.has_app_context():
            app.logger.error(f"DBDoesNotExist exception internal message: {inter_msg}")
        DemoExcept.__init__(self,
                            user_msg="Internal Error while establishing database",
                            inter_msg=inter_msg,
                            http_code=500,
                            err_code=1002)


class SchemaDoesNotExist(DemoExcept):
    def __init__(self, schema_name, e=None):
        inter_msg = f"Schema {schema_name} failed to be created "
        if e:
            inter_msg += str(e)
        if flask.has_app_context():
            app.logger.error(f"Schema exception, {inter_msg}")
        DemoExcept.__init__(self,
                            user_msg="Internal database Error",
                            inter_msg=inter_msg,
                            http_code=500,
                            err_code=1003)


class SelectError(DemoExcept):
    def __init__(self, statement, params, e=None):
        inter_msg = f"Select {statement} failed to execute with parameters {params} "
        if e:
            inter_msg += str(e)
        if flask.has_app_context():
            app.logger.error(f"Select exception, {inter_msg}")
        DemoExcept.__init__(self,
                            user_msg="Internal database Error",
                            inter_msg=inter_msg,
                            http_code=500,
                            err_code=1004)


class Inconsistency(DemoExcept):
    def __init__(self, row, params, table, e=None):
        inter_msg = f"Inconsistent data insert into {table} \nold data: {row}\nnew data: {params}\n"
        if e:
            inter_msg += str(e)
        if flask.has_app_context():
            app.logger.error(f"Insert exception, {inter_msg}")
        DemoExcept.__init__(self,
                            user_msg="Error occurred while inserting new data",
                            inter_msg=inter_msg,
                            http_code=400,
                            err_code=1005)


class TableNotDefined(DemoExcept):
    def __init__(self, table=None):
        inter_msg = f"Table: {table} not defined in duplicity_check."
        if flask.has_app_context():
            app.logger.error(f"Table: {table} missing from duplicity_check method")
        DemoExcept.__init__(self,
                            user_msg="Table wasn't properly defined",
                            inter_msg=inter_msg,
                            http_code=500,
                            err_code=1006)


# InsertError(statement, params, err)
class InsertError(DemoExcept):
    def __init__(self, statement, params, e=None):
        inter_msg = f"insert {statement} failed to execute with parameters {params} "
        if e:
            inter_msg += str(e)
        if flask.has_app_context():
            app.logger.error(f"Insert exception, {inter_msg}")
        DemoExcept.__init__(self,
                            user_msg="Internal database Error",
                            inter_msg=inter_msg,
                            http_code=400,
                            err_code=1007)
