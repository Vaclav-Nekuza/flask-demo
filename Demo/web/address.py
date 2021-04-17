from flask_restx import Resource
from flask import request, current_app as app

from ..models import ns_demo, mdl_address, mdl_resp_address


@ns_demo.route('/address', methods=['GET', 'POST'])
class ManageAddress(Resource):
    @ns_demo.response(200, 'Success')
    @ns_demo.response(400, 'Bad Request')
    @ns_demo.marshal_with(mdl_resp_address)
    @ns_demo.param('id', 'id of a person')
    def get(self):
        app.logger.info(f"Received request for a person")
        addr_id = request.args.get('id', None)
        resp = app.db.select_address(addr_id=addr_id)
        return resp, 200

    @ns_demo.response(200, 'Success')
    @ns_demo.response(400, 'Bad Request')
    @ns_demo.expect(mdl_address)
    def post(self):
        data = request.json
        resp = app.db.insert_person(data['street'], data['street_number'], data['post_code'], data['city'],
                                    data['country'])
        return resp, 200
