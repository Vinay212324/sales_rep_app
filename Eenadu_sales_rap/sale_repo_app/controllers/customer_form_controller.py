import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
from werkzeug.utils import redirect
import json
import uuid
import hmac
import hashlib

_logger = logging.getLogger(__name__)
SECRET_KEY = 'your_secret_key'


class CustomerFormAPI(http.Controller):

    def _verify_api_key(self, token):
        user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        if not user:
            user = False
            return user
        return {"success": "True", "user_Id": user.id, "user_login": user.login}

    @http.route('/api/customer_form', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def create_customer(self, **kwargs):
        try:
            api_key = kwargs.get('token')
            if not api_key:
                return {'success': False, 'message': 'Token is missing', 'code': "403"}

            user = self._verify_api_key(api_key)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', "code": "403"}

            job_one = {
                "Central Job": "central_job",
                "PSU": "psu",
                "State Job": "state_job"
            }.get(kwargs.get('job_type_one'), "")

            customer = request.env['customer.form'].sudo().create({
                'agent_name': kwargs.get('agent_name'),
                'agent_login': kwargs.get('agent_login'),
                'unit_name': kwargs.get('unit_name'),
                'date': kwargs.get('date'),
                'time': kwargs.get('time'),
                'family_head_name': kwargs.get('family_head_name'),
                'father_name': kwargs.get('father_name'),
                'mother_name': kwargs.get('mother_name'),
                'spouse_name': kwargs.get('spouse_name'),
                'house_number': kwargs.get('house_number'),
                'street_number': kwargs.get('street_number'),
                'city': kwargs.get('city'),
                'pin_code': kwargs.get('pin_code'),
                'address': kwargs.get('address'),
                'mobile_number': kwargs.get('mobile_number'),
                'eenadu_newspaper': kwargs.get('eenadu_newspaper', False),
                'feedback_to_improve_eenadu_paper': kwargs.get('feedback_to_improve_eenadu_paper'),
                'read_newspaper': kwargs.get('read_newspaper', False),
                'current_newspaper': kwargs.get('current_newspaper'),
                'reason_for_not_taking_eenadu_newsPaper': kwargs.get('reason_for_not_taking_eenadu_newsPaper'),
                'reason_not_reading': kwargs.get('reason_not_reading'),
                'free_offer_15_days': kwargs.get('free_offer_15_days', False),
                'reason_not_taking_offer': kwargs.get('reason_not_taking_offer'),
                'employed': kwargs.get('employed', False),
                'job_type': kwargs.get('job_type'),
                'job_type_one': job_one,
                'job_profession': kwargs.get('job_profession'),
                'job_designation': kwargs.get('job_designation'),
                'company_name': kwargs.get('company_name'),
                'profession': kwargs.get('profession'),
                'job_designation_one': kwargs.get('job_designation_one'),
                'latitude': kwargs.get('latitude'),
                'longitude': kwargs.get('longitude'),
            })
            return {'success': True, 'message': 'Customer Form created successfully', 'customer_id': customer.id,
                    "code": "200"}
        except Exception as e:
            return {'success': False, 'message': 'Error: {}'.format(str(e)), 'code': "403"}

    @http.route('/api/login', type='json', auth='public', methods=['POST'])
    def api_login(self, email, password):
        user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if not user:
            raise AccessDenied("User not found!")
        try:
            user.sudo()._check_credentials(password, {'interactive': True})
        except AccessDenied:
            raise AccessDenied("Invalid password!")
        user.generate_token()
        return {'status': 'success', 'user_id': user.id, 'name': user.name, 'role': user.role, 'token': user.api_token,
                'token_expiry': user.token_expiry}

    @http.route('/api/logout', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def api_logout(self, token):
        user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        if not user:
            raise AccessDenied("Invalid token!")
        user.clear_token()
        return {'status': 'success', 'message': "User logged out successfully", "code": "200"}

    @http.route('/token_validation', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def token_validation(self, **params):
        try:
            api_key = params.get('token')
            if not api_key:
                return {'success': False, 'message': 'Token is missing', 'code': "403"}
            user = self._verify_api_key(api_key)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', "code": "403"}
            return {'success': True, 'message': 'Valid token', 'user_login': user, "code": "200"}
        except Exception as e:
            return {'success': False, 'message': 'Error: {}'.format(str(e)), 'code': "403"}


    @http.route('/api/customer_forms_info', type='json', auth="public", methods=['GET'], csrf=False, cors="*")
    def get_customer_forms(self, **params):
        """
        Fetch customer form records based on the user login.
        """
        api_key = params.get('token')

        if not api_key:
            return {
                'success': False,
                'message': 'Token is missing',
                'code': "403"
            }


        # Validate Token
        user = self._verify_api_key(api_key)
        if not user:
            return {
                'success': False,
                'message': 'Invalid or expired token',
                "code": "403"
            }

        user_id = params.get("user_id")
        if not user_id:
            return {'error': 'User ID is required', "code": "403"}

        try:
            user_id = int(user_id)
        except ValueError:
            return {'error': 'Invalid User ID', "code": "403"}

        # Fetch user details
        user = request.env['res.users'].sudo().browse(user_id)
        if not user.exists():
            return {'error': 'User not found', "code": "403"}

        agent_login = user.login  # Get the login of the user
        _logger.info(f"Fetching records for agent login: {agent_login}")

        # Debugging: Check if any records exist at all
        all_records = request.env['customer.form'].sudo().search([])
        _logger.info(f"Total Customer Forms: {len(all_records)}")

        # Print all records to check agent_login values
        for record in all_records:
            _logger.info(f"Record ID: {record.id}, Agent Login: {record.agent_login}")

        # Check if `agent_login` is a Many2one relation instead of a Char field
        customer_forms = request.env['customer.form'].sudo().search([('agent_login', '=', agent_login)])
        if not customer_forms:
            _logger.warning(f"No records found for agent_login: {agent_login}")

        # Prepare the result
        result = [{
            'id': record.id,
            'agent_name': record.agent_name,
            'agent_login': record.agent_login,
            'unit_name': record.unit_name,
            'date': record.date,
            'time': record.time,
            'family_head_name': record.family_head_name,
            'father_name': record.father_name,
            'mother_name': record.mother_name,
            'spouse_name': record.spouse_name,
            'house_number': record.house_number,
            'street_number': record.street_number,
            'city': record.city,
            'pin_code': record.pin_code,
            'address': record.address,
            'mobile_number': record.mobile_number,
            'eenadu_newspaper': record.eenadu_newspaper,
            'feedback_to_improve_eenadu_paper': record.feedback_to_improve_eenadu_paper,
            'read_newspaper': record.read_newspaper,
            'current_newspaper': record.current_newspaper,
            'reason_for_not_taking_eenadu_newsPaper': record.reason_for_not_taking_eenadu_newsPaper,
            'reason_not_reading': record.reason_not_reading,
            'free_offer_15_days': record.free_offer_15_days,
            'reason_not_taking_offer': record.reason_not_taking_offer,
            'employed': record.employed,
            'job_type': record.job_type,
            'job_type_one': record.job_type_one,
            'job_profession': record.job_profession,
            'job_designation': record.job_designation,
            'company_name': record.company_name,
            'profession': record.profession,
            'job_designation_one': record.job_designation_one,
            'latitude': record.latitude,
            'longitude': record.longitude,
        } for record in customer_forms]

        return {'records': result, "code": "200"}

    @http.route('/api/users', type='json', auth='public', methods=['GET'], csrf=False, cors="*")
    def get_users(self, **kw):
        try:

            api_key = kw.get('token')

            if not api_key:
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': "403"
                }

            # Validate Token
            user = self._verify_api_key(api_key)
            if not user:
                return {
                    'success': False,
                    'message': 'Invalid or expired token',
                    "code": "403"
                }

            # Fetch users
            users = request.env['res.users'].sudo().search([])
            user_list = []

            for user in users:
                user_list.append({
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'login': user.login,
                    'create_uid': user.create_uid,
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






