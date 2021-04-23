from flask_restx import fields, Namespace
import arrow

now_date = str(arrow.now()).split("T")[0]

ns_demo = Namespace(name='demo',
                    description='demo api',
                    path='/api/v1')

model_address = {
    "street": fields.String(description="street name", required=True),
    "street_number": fields.Integer(description="street number", required=True),
    "post_code": fields.Integer(description="post code", required=True),
    "city": fields.String(description="city", required=True),
    "country": fields.String(description="country", required=True),
}

mdl_address = ns_demo.model('mdl_address', model_address)

mdl_return_address = mdl_address.inherit(
    'mdl_return_address', {
        "id": fields.Integer(description="unique identifier of a address", required=True),
    }
)

model_resp_address = {
    'err_code': fields.Integer(description='response identifier, 0 for success', required=True),
    'message': fields.String(description='message corresponding to the result', required=True),
    'data': fields.List(fields.Nested(mdl_return_address))
}

mdl_resp_address = ns_demo.model('mdl_resp_address', model_resp_address)

model_person = {
    "first_name": fields.String(description="first name", required=True),
    "surname": fields.String(description="surname", required=True),
    "address": fields.Nested(mdl_address),
    "email": fields.String(description="email", required=True),
    "date_of_birth": fields.String(description="date of birth", required=True, example=now_date),
}

mdl_person = ns_demo.model('mdl_person', model_person)

mdl_return_person = mdl_person.inherit(
    'mdl_return_person', {
        'id': fields.Integer(description='id of the record', required=True),
        'created': fields.DateTime(description='time the person was created', required=True),
    }
)

model_resp_person = {
    'err_code': fields.Integer(description='response identifier, 0 for success', required=True),
    'message': fields.String(description='message corresponding to the result', required=True),
    'data': fields.List(fields.Nested(mdl_return_person))
}

mdl_resp_person = ns_demo.model('mdl_resp_person', model_resp_person)

