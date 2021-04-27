from flask_restx import Resource
from flask import request, current_app as app

from ..models import ns_demo, mdl_person, mdl_resp_person


@ns_demo.route('/personal', methods=['GET', 'POST'])
class ManagePeople(Resource):
    @ns_demo.response(200, 'Success')
    @ns_demo.response(400, 'Bad Request')
    @ns_demo.marshal_with(mdl_resp_person)
    @ns_demo.param('email', 'email')
    @ns_demo.param('surname', 'surname')
    @ns_demo.param('first_name', 'first_name')
    @ns_demo.param('id', 'id of a person')
    def get(self):
        pers_id = request.args.get('id', None)
        first_name = request.args.get('first_name', None)
        surname = request.args.get('surname', None)
        email = request.args.get('email', None)
        app.logger.info(f"Received request for a person")
        resp = app.db.select_person(pers_id=pers_id, email=email, first_name=first_name, surname=surname)
        return resp, 200

    @ns_demo.response(200, 'Success')
    @ns_demo.response(400, 'Bad Request')
    @ns_demo.expect(mdl_person)
    def post(self):
        data = request.json
        app.logger.info(f"Received request to insert new person")
        resp = app.db.insert_person(data['first_name'], data['surname'], data['address'], data['email'],
                                    data['date_of_birth'])
        return resp, 200
