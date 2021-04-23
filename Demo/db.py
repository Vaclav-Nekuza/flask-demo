from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.selectable import Select
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine import create_engine
from sqlalchemy import Table, MetaData, String, Integer, Sequence, ForeignKey, bindparam
from sqlalchemy.sql import select
from sqlalchemy.schema import CreateSchema, Column
from sqlalchemy_utils import ArrowType, database_exists, create_database
from sqlalchemy.exc import IntegrityError
import arrow
from typing import Dict, Union, List
from flask import has_app_context

if has_app_context():
    from flask import current_app as app

from .error import EngineCreation, DBDoesNotExist, SchemaDoesNotExist, SelectError, Inconsistency, TableNotDefined, \
    InsertError


class DB:
    def __init__(self, db_uri: str, schema_name: str, logger) -> None:
        """
        constructor
        :param db_uri uri used for database connection
        """
        self.db_uri: str = db_uri
        self.logger = logger
        self.logger.info(f"Initializing Database connection")
        self.engine: Engine = self.make_engine()
        self.db_check()
        self.schema_name = schema_name
        self.make_schema()
        self.metadata: MetaData = MetaData(self.engine)
        self.address_table: Table = self.crt_address_table()
        self.person_table: Table = self.crt_person_table()

        self._init_select_stmt()
        self._init_insert_statements()
        self.metadata.create_all(self.engine)

    def _insert(self, statement: Insert, params: Dict[str, Union[int, str]]):
        """
        General insert method executing received insert statement
        :param statement: Insert statement
        :param params: parameters for insert
        :return: success response or raises a exception
        """
        conn = self.engine.connect()
        try:
            self.logger.info(f"Inserting data into {statement.table}")
            result = conn.execute(statement, params)
            return result
        except IntegrityError as err:
            self.duplicity_check(statement, params, err)
        except Exception as err:
            InsertError(statement, params, err).abort()
        finally:
            conn.close()

    def _select(self, statement: Select, params: Dict[str, Union[int, str]]):
        """
        General select method executing received select statement
        :param statement: Select statement
        :param params: parameters for select
        :return:
        """
        conn = self.engine.connect()
        try:
            self.logger.info(f"selecting data")
            return conn.execute(statement, params)
        except Exception as err:
            SelectError(statement, params, err).abort()

    def insert_person(self, first_name, surname, address, email, date_of_birth):
        self.logger.info(f"Inserting new person")
        params = {'street': address['street'], 'street_number': address['street_number'],
                  'post_code': address['post_code'], 'city': address['city'], 'country': address['country']}
        addr = self.select_address(**params)
        if addr['data'] == {}:
            ins_resp = self.insert_address(**params)
            if ins_resp['err_code'] == 0:
                addr = self.select_address(**params)
            else:
                InsertError(self.addr_ins, params).abort()
        addr_id = addr['data']['id']
        params = {
            'created': arrow.now(),
            'first_name': first_name,
            'surname': surname,
            'address_id': addr_id,
            'email': email,
            'date_of_birth': arrow.get(date_of_birth)
        }
        self._insert(self.per_ins, params)
        return self.get_success_response("Successfully inserted new person")

    def insert_address(self, street: str, street_number: int, post_code: int, city: str, country: str) \
            -> Dict[str, Union[int, str]]:
        self.logger.info(f"Inserting new address ")
        params = {
            'street': street,
            'street_number': street_number,
            'post_code': post_code,
            'city': city,
            'country': country
        }
        self._insert(self.addr_ins, params)
        return self.get_success_response("Successfully inserted new address")

    def select_person(self, pers_id: int = None, email: str = None, first_name: str = None, surname: str = None) -> \
            Dict[str, Union[int, str, List[Dict[str, Union[int, str, Dict[str, Union[int, str]]]]]]]:
        resp = []
        if pers_id is not None:
            self.logger.info(f"Selecting person using id: {pers_id}")
            people = self._select(self.get_per_sel_stmt, {'id': pers_id})
        elif email is not None:
            self.logger.info(f"Selecting person using email: {email}")
            people = self._select(self.get_per_email_sel_stmt, {'email': email})
        elif first_name is not None and surname is not None:
            self.logger.info(f"Selecting person using name: {first_name} {surname}")
            people = self._select(self.get_per_name_sel_stmt, {'first_name': first_name, 'surname': surname})
        elif pers_id is None and email is None and first_name is None and surname is None:
            self.logger.info(f"Selecting all people")
            people = self._select(self.get_per_all_sel_stmt, {})
        else:
            self.logger.info(f"Request for people used unsupported parameters")
            return self.get_fail_response([])
        for person in people:
            address = self.select_address(addr_id=person['address_id'])['data']
            resp_person = {
                'id': person['id'],
                'created': person['created'],
                'first_name': person['first_name'],
                'surname': person['surname'],
                'address': {
                    'id': address['id'],
                    'street': address['street'],
                    'street_number': address['street_number'],
                    'post_code': address['post_code'],
                    'city': address['city'],
                    'country': address['country']
                },
                'email': person['email'],
                'date_of_birth': str(person['date_of_birth'])
            }
            resp.append(resp_person)
        return self.get_success_response(resp)

    def select_address(self, addr_id: int = None, street: str = None, street_number: int = None, post_code: int = None,
                       city: str = None, country: str = None) -> Dict[str, Union[int, str, Dict[str, Union[int, str]]]]:
        """
        method specific for selecting addresses from database
        :params: parameters for selecting address
        :return: api response for the request
        """
        result = {}
        if addr_id is not None:
            self.logger.info(f"Selecting address using id: {addr_id}")
            resp = self._select(self.get_addr_sel_stmt, {'id': addr_id})
        elif street is not None and street_number is not None and post_code is not None and city is not None and \
                country is not None:
            self.logger.info(f"Selecting address using full address: {street}, {street_number}, {post_code}, " +
                             f"{city}, {country}")
            resp = self._select(self.get_addr_full_sel_stmt, {'street': street, 'street_number': street_number,
                                                              'post_code': post_code, 'city': city, 'country': country})
        else:
            return self.get_fail_response(result)
        for row in resp:
            result = {
                "id": row[0],
                "street": row[1],
                "street_number": row[2],
                "post_code": row[3],
                "city": row[4],
                "country": row[5],
            }
        return self.get_success_response(result)

    def duplicity_check(self, statement: Insert, params: Dict[str, Union[int, str]], err):
        """
        In case of IntegrityError from Postgres it checks if it is a identical duplicate or inconsistent duplicate
        :param statement: Insert causing IntegrityError
        :param params: parameters bound in the statement
        :param err: the error it self
        :return: it either raises its own exception or returns None
        """
        self.logger.info(f"Checking for duplicate data")
        table = statement.table
        if table == self.person_table:
            stmt = self.get_per_all_sel_stmt
        else:
            stmt = self.get_addr_full_sel_stmt
        result = self._select(stmt, params)
        for row in result:
            if table == self.person_table:
                if not (row[2] == params["first_name"] and row[3] == params["surname"] and
                        row[4] == params["address_id"] and row[6] == params["date_of_birth"]):
                    Inconsistency(row, params, table, err).abort()
            elif table == self.address_table:
                if not (row[1] == params["street"] and row[2] == params["street_number"] and
                        row[3] == params["post_code"] and row[4] == params["city"] and row[5] == params["country"]):
                    Inconsistency(row, params, table, err).abort()
            else:
                TableNotDefined(table).abort()
        self.logger.info(f"identical duplicate data found it is being ignored")
        return None

    @staticmethod
    def get_fail_response(response):
        return {'err_code': 1,
                'message': "Invalid combination of arguments on request",
                'data': response}

    @staticmethod
    def get_success_response(response):
        return {'err_code': 0,
                'message': "Success",
                'data': response}

    # establishing database
    # ----------------------------------------------------------------------------------------------------------------------

    def crt_person_table(self) -> Table:
        return Table('person_table',
                     self.metadata,
                     Column('id', Integer, Sequence('personal_id_seq', schema=self.schema_name), unique=True),
                     Column('created', ArrowType, nullable=False),
                     Column('first_name', String, nullable=False),
                     Column('surname', String, nullable=False),
                     Column('address_id', Integer, ForeignKey(self.address_table.columns.id), nullable=False),
                     Column('email', String, primary_key=True, unique=True),
                     Column('date_of_birth', ArrowType),
                     schema=self.schema_name)

    def crt_address_table(self) -> Table:
        return Table('address_table',
                     self.metadata,
                     Column('id', Integer, Sequence('address_id_seq', schema=self.schema_name), unique=True),
                     Column('street', String, nullable=False, primary_key=True),
                     Column('street_number', Integer, nullable=False, primary_key=True),
                     Column('post_code', Integer, nullable=False, primary_key=True),
                     Column('city', String, nullable=False, primary_key=True),
                     Column('country', String, nullable=False, primary_key=True),
                     schema=self.schema_name)

    def make_schema(self) -> None:
        """
        Creates database schema
        """
        conn = self.engine.connect()
        try:
            if not conn.dialect.has_schema(conn, self.schema_name):
                self.logger.info(f"Creating schema {self.schema_name}")
                conn.execute(CreateSchema(self.schema_name))
            conn.close()
        except Exception as err:
            conn.close()
            SchemaDoesNotExist(self.schema_name, err).abort()

    def db_check(self) -> None:
        """
        Checks if needed database is present, if not it creates it.
        :raises: DatabaseExp in case it fails to create database connection
        """
        try:
            if not database_exists(self.engine.url):
                self.logger.info(f"Creating new database")
                create_database(self.engine.url)
        except Exception as err:
            url = str(self.engine.url)
            db_name = url.split("/")[-1]
            username = url.split("//")[1].split(":")[0]
            DBDoesNotExist(db_name, username, str(err)).abort()

    def make_engine(self) -> Engine:
        """
        Creates engine for database connection.
        :return: the engine
        """
        try:
            self.logger.info(f"Creating engine")
            return create_engine(self.db_uri)
        except Exception as err:
            EngineCreation(e=err).abort()

    def dispose(self) -> None:
        self.engine.dispose()

    def _init_insert_statements(self):
        self.addr_ins = self.address_table.insert()
        self.per_ins = self.person_table.insert()

    def _init_select_stmt(self) -> None:
        """
        Initializes select statements
        :return: Tuple of selects using bindparam to insert specific variables
        """
        self.get_addr_sel_stmt = select([self.address_table]).where(self.address_table.columns.id == bindparam('id'))

        self.get_addr_full_sel_stmt = select([self.address_table]). \
            where(self.address_table.columns.street == bindparam('street')). \
            where(self.address_table.columns.street_number == bindparam('street_number')). \
            where(self.address_table.columns.post_code == bindparam('post_code')). \
            where(self.address_table.columns.city == bindparam('city')). \
            where(self.address_table.columns.country == bindparam('country'))

        self.get_per_all_sel_stmt = select([self.person_table])

        self.get_per_sel_stmt = select([self.person_table]).where(self.person_table.columns.id == bindparam('id'))

        self.get_per_email_sel_stmt = select([self.person_table]). \
            where(self.person_table.columns.email == bindparam('email'))

        self.get_per_name_sel_stmt = select([self.person_table]). \
            where(self.person_table.columns.first_name == bindparam('first_name')). \
            where(self.person_table.columns.surname == bindparam('surname'))

        self.get_per_addr_sel_stmt = select([self.person_table]). \
            where(self.person_table.columns.address_id == bindparam('address_id'))
