import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class localApi(http.Controller):

    @http.route('/get_created_staff', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def get_user_you_created(self, **kwargs):
        try:
            user = request.env.user
            user_id = user.id
            users = request.env['res.users'].sudo().search([('create_uid', '=', user_id)])
            user_list = []

            for user in users:
                user_list.append({
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'login': user.login,
                    'create_uid': user.create_uid.id if user.create_uid else False,
                    'unit_name': user.unit_name,
                    'phone': user.phone,
                    'state': user.state,
                    'pan_number': user.pan_number,
                    'aadhar_number': user.aadhar_number,
                    'role': user.role,
                    'status': user.status,
                })

            return {'status': 200, 'users': user_list}

        except Exception as e:
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route('/create_staff', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def create_staff(self, **kwargs):
        print("vinay21212121aaaaaaaaaaaa")

        try:
            staff_data = kwargs.get('params', {})
            print(staff_data)
            print(staff_data.get('name'))
            user = request.env.user
            print(user.id)
            vals = {
                'name': staff_data.get('name'),
                'unit_name': staff_data.get('unit'),
                'email': staff_data.get('email'),
                'login': staff_data.get('user_id'),
                'password': staff_data.get('password'),
                'phone': staff_data.get('phone'),
                'aadhar_number': staff_data.get('adhaar'),
                'role': "agent",
                'create_uid': user.id,
                # Add any other necessary values here
            }
            staff_user = request.env['res.users'].sudo().create(vals)
            print(staff_user.id,"vinay")
            return {'status': 200, 'id': staff_user.id}
        except Exception as e:
            _logger.error("Staff Creation Error: %s", e)
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}


    @http.route('/user_info', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def user_info(self, **kwargs):
        print("vinay21212121angngfnfgnfgnfgnftgnaaaaaaaaaaa")

        try:
            user = request.env.user
            print(user.id)
            vals = {
                'name': user.name,
                'unit_name': user.unit_name,
                'email': user.email,
                'login': user.user_id,
                'password': user.password,
                'phone': user.phone,
                'aadhar_number': user.aadhar_number,
                'create_uid': user.id,
            }

            return {'status': 200, 'user_info': vals}
        except Exception as e:
            _logger.error("Staff Creation Error: %s", e)
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}
