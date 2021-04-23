from flask_restx import Resource
from flask import request, current_app as app

from ..models import ns_demo, mdl_address, mdl_resp_address


@ns_demo.route('/address', methods=['GET', 'POST'])
class ManageAddress(Resource):
    @ns_demo.response(200, 'Success')
    @ns_demo.response(400, 'Bad Request')
    @ns_demo.marshal_with(mdl_resp_address)
    @ns_demo.param('id', 'id of a person')
    @ns_demo.param('street', 'street of the house')
    @ns_demo.param('street_number', 'house number')
    @ns_demo.param('post_code', 'post code of the house')
    @ns_demo.param('city', 'city the house in located in')
    @ns_demo.param('country', 'country/state the house in located in')
    def get(self):
        app.logger.info(f"Received request for a person")
        addr_id = request.args.get('id', None)
        street = request.args.get('street', None)
        street_number = request.args.get('street_number', None)
        post_code = request.args.get('post_code', None)
        city = request.args.get('city', None)
        country = request.args.get('country', None)
        resp = app.db.select_address(addr_id=addr_id, street=street, street_number=street_number, post_code=post_code,
                                     city=city, country=country)
        return resp, 200

    @ns_demo.response(200, 'Success')
    @ns_demo.response(400, 'Bad Request')
    @ns_demo.expect(mdl_address)
    def post(self):
        data = request.json
        resp = app.db.insert_address(data['street'], data['street_number'], data['post_code'], data['city'],
                                     data['country'])
        return resp, 200
