import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
from werkzeug.utils import redirect
import json
import uuid
import hmac
import hashlib
import time
from datetime import date
import logging
import base64

from datetime import date
import time
import logging
from datetime import date


# Cache storage (module-level)
_cached__data = {}
_cached_customer_form_filter_data = {}




_logger = logging.getLogger(__name__)
SECRET_KEY = 'your_secret_key'
_cached_data = {}  # Simple dictionary for cache
CACHE_DURATION = 6
from datetime import date


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
                'job_working_state': kwargs.get('job_working_state'),
                'job_working_location': kwargs.get('job_working_location'),
                'job_location_landmark': kwargs.get('job_location_landmark'),
                'profession': kwargs.get('profession'),
                'job_designation_one': kwargs.get('job_designation_one'),
                'latitude': kwargs.get('latitude'),
                'longitude': kwargs.get('longitude'),
                'location_address': kwargs.get('location_address'),
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


    @http.route('/api/customer_forms_info', type='json', auth="public", methods=['POST'], csrf=False, cors="*")
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
            'job_working_state': record.job_working_state,
            'job_working_location': record.job_working_location,
            'job_designation_one': record.job_designation_one,
            'latitude': record.latitude,
            'longitude': record.longitude,
            'location_address': record.location_address,
        } for record in customer_forms]

        return {'records': result, "code": "200"}

    @http.route('/api/users', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
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
                aadhar_image_data = None
                if user.aadhar_base64:
                    aadhar_image_data = f"data:image/png;base64,{user.aadhar_base64.decode('utf-8')}"
                pan_image_data = None
                if user.Pan_base64:
                    pan_image_data = f"data:image/png;base64,{user.Pan_base64.decode('utf-8')}"

                user_list.append({
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'login': user.login,
                    'create_uid': user.create_uid.id if user.create_uid else None,
                    'unit_name': user.unit_name,
                    'phone': user.phone,
                    'state': user.state,
                    'pan_number': user.pan_number,
                    'aadhar_number': user.aadhar_number,
                    'role': user.role,
                    'status': user.status,
                    'aadhar_image': aadhar_image_data,
                    'pan_image' : pan_image_data,
                })

            return {'status': 200, 'users': user_list}

        except Exception as e:
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route('/api/users_you_created', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def users_you_created(self, **kw):
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
            user = request.env['res.users'].sudo().search([('api_token', '=', api_key)], limit=1)
            user_id =user.id
            # Fetch users
            users = request.env['res.users'].sudo().search([('create_uid', '=', user_id)])
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

    @http.route('/api/customer_forms_info_one_day', type='json', auth="public", methods=['POST'], csrf=False, cors="*")
    def get_customer_forms_one_day(self, **params):
        """
        API to fetch today's customer forms entered by a specific agent.
        Uses caching to reduce database load.
        """
        api_key = params.get('token')
        if not api_key:
            return {'success': False, 'message': 'Token is missing', 'code': "403"}

        user = self._verify_api_key(api_key)
        if not user:
            return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

        user_id = params.get("user_id")
        if not user_id:
            return {'error': 'User ID is required', "code": "403"}

        try:
            user_id = int(user_id)
        except ValueError:
            return {'error': 'Invalid User ID', "code": "403"}

        user = request.env['res.users'].sudo().browse(user_id)
        if not user.exists():
            return {'error': 'User not found', "code": "403"}

        agent_login = user.login
        today_date = date.today()

        # Define cache key
        cache_key = f"customer_forms_{agent_login}_{today_date}"
        now = time.time()

        # ✅ Use cache if available and valid
        if cache_key in _cached_data:
            cached_response, cached_time = _cached_data[cache_key]
            if now - cached_time < CACHE_DURATION:
                _logger.info(f"[CACHE] Returning cached data for {agent_login}")
                return cached_response

        # ❌ Cache expired or not found – fetch from DB
        customer_forms = request.env['customer.form'].sudo().search([
            ('agent_login', '=', agent_login),
            ('date', '=', today_date)
        ])

        result = [{
            'id': record.id,
            'agent_name': record.agent_name,
            'agent_login': record.agent_login,
            'unit_name': record.unit_name,
            'date': str(record.date),
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
            'job_working_state': record.job_working_state,
            'job_working_location': record.job_working_location,
            'job_designation_one': record.job_designation_one,
            'latitude': record.latitude,
            'longitude': record.longitude,
            'location_address': record.location_address,
        } for record in customer_forms]

        response = {
            'records': result,
            'count': len(result),
            'code': "200"
        }

        # ✅ Store result in cache
        _cached_data[cache_key] = (response, now)
        _logger.info(f"[CACHE] Data cached for {agent_login} with {len(result)} records.")

        return response

    @http.route('/api/customer_forms_info_id', type='json', auth="public", methods=['POST'], csrf=False, cors="*")
    def get_customer_forms_info_id(self, **params):
        """
        API to fetch today's customer forms entered by a specific agent.
        Uses caching to reduce database load.
        """
        api_key = params.get('token')
        if not api_key:
            return {'success': False, 'message': 'Token is missing', 'code': "403"}

        user = self._verify_api_key(api_key)
        if not user:
            return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

        user_id = params.get("user_id")
        if not user_id:
            return {'error': 'User ID is required', "code": "403"}

        try:
            user_id = int(user_id)
        except ValueError:
            return {'error': 'Invalid User ID', "code": "403"}

        user = request.env['res.users'].sudo().browse(user_id)
        if not user.exists():
            return {'error': 'User not found', "code": "403"}

        agent_login = user.login
        today_date = date.today()

        # Define cache key
        cache_key = f"customer_forms_{agent_login}_{today_date}"
        now = time.time()

        # ✅ Use cache if available and valid
        if cache_key in _cached__data:
            cached_response, cached_time = _cached__data[cache_key]
            if now - cached_time < CACHE_DURATION:
                _logger.info(f"[CACHE] Returning cached data for {agent_login}")
                return cached_response

        # ❌ Cache expired or not found – fetch from DB
        customer_forms = request.env['customer.form'].sudo().search([
            ('agent_login', '=', agent_login)
        ])

        result = [{
            'id': record.id,
            'agent_name': record.agent_name,
            'agent_login': record.agent_login,
            'unit_name': record.unit_name,
            'date': str(record.date),
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
            'job_working_state': record.job_working_state,
            'job_working_location': record.job_working_location,
            'job_designation_one': record.job_designation_one,
            'latitude': record.latitude,
            'longitude': record.longitude,
            'location_address': record.location_address,
        } for record in customer_forms]

        response = {
            'records': result,
            'count': len(result),
            'code': "200"
        }

        # ✅ Store result in cache
        _cached__data[cache_key] = (response, now)
        _logger.info(f"[CACHE] Data cached for {agent_login} with {len(result)} records.")

        return response




    @http.route("/update/status", type="json", methods=['POST'], csrf=False, cors="*")
    def _update_status(self,**params):

        api_key = params.get('token')
        if not api_key:
            return {'success': False, 'message': 'Token is missing', 'code': "403"}

        user = self._verify_api_key(api_key)
        if not user:
            return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

        user_id = params.get("user_id")
        if not user_id:
            return {'error': 'User ID is required', "code": "403"}

        try:
            user_id = int(user_id)
        except ValueError:
            return {'error': 'Invalid User ID', "code": "403"}

        user = request.env['res.users'].sudo().browse(user_id)
        if not user.exists():
            return {'error': 'User not found', "code": "403"}
        if params.get("status") not in ["active","un_activ"]:
            return {'error':'status is missing'}

        user.write({
            'status': params.get("status"),
        })
        if user.status == params.get("status"):
            return {"success":"True","user_id":user.id, "code":"200"}
        else:
            return {"success":"False", "code":"403"}

    @http.route('/api/agents_info_based_on_the_unit', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def agents_info_based_on_the_unit(self, **kw):
        try:

            api_key = kw.get('token')
            unit_name = kw.get('unit_name')

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
            # user = request.env['res.users'].sudo().search([('api_token', '=', api_key)], limit=1)
            # user_id = user.id
            # # Fetch users
            users = request.env['res.users'].sudo().search([
                '&',
                ('unit_name', '=', unit_name),
                ('role', '=', 'agent')
            ])
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

    @http.route('/api/For_root_map_asin', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def For_root_map_asin(self, **kw):
        try:
            agent_id = kw.get('agent_id')
            api_key = kw.get('token')
            root_map_name = kw.get('root_map')  # Sent as string
            print(agent_id,api_key,root_map_name)
            if not api_key:
                return {'success': False, 'message': 'Token is missing', 'code': 403}

            user = self._verify_api_key(api_key)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            agent = request.env['res.users'].sudo().search([('id', '=', int(agent_id))], limit=1)
            if not agent:
                return {'success': False, 'message': 'Agent not found', 'code': 404}
            print("vinay21321")
            # Search or create root.map
            root_map_rec = request.env['root.map'].sudo().search([('root_name', '=', root_map_name)], limit=1)
            print(root_map_rec)
            if not root_map_rec:
                print("madhavarao")
                root_map_rec = request.env['root.map'].sudo().create({
                    'root_name': root_map_name,
                    'date': date.today()
                })

            # Assign to agent
            print(root_map_rec.id)
            agent.root_name_id = root_map_rec.id

            return {
                'success': True,
                'message': 'Root map assigned successfully',
                'status': 200,
                'agent_id': agent.id,
                'root_map': {
                    'id': root_map_rec.id,
                    'name': root_map_rec.root_name
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e),
                'code': 500
            }

    @http.route('/api/for_agent_root_map_name', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def For_agent_root_map_name(self, **kw):
        try:
            agent_id = int(kw.get('agent_id'))
            api_key = kw.get('token')

            if not api_key:
                return {'success': False, 'message': 'Token is missing', 'code': 403}

            user = self._verify_api_key(api_key)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            agent = request.env['res.users'].sudo().search([('id', '=', int(agent_id))], limit=1)
            if not agent:
                return {'success': False, 'message': 'Agent not found', 'code': 404}

            return {
                'status': 200,
                'success': True,
                'root_map': {
                    'id': agent.root_name_id.id if agent.root_name_id else None,
                    'name': agent.root_name_id.root_name if agent.root_name_id else ""
                }
            }

        except Exception as e:
            return {'success': False, 'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route('/unit_name_of_user', type='json', auth='none', methods=["POST"], csrf=False, cors="*")
    def get_unit_names(self, **kwargs):
        try:
            api_key = kwargs.get('token')
            if not api_key:
                return {'success': False, 'message': 'Token is missing', 'code': "403"}

            user = request.env['res.users'].sudo().search([('api_token', '=', api_key)], limit=1)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

            # Return list of unit names
            unit_names = [{'id': unit.id, 'name': unit.name} for unit in user.unit_name_ids]

            return {
                'success': True,
                'unit_names': unit_names,
                'code': 200
            }

        except Exception as e:
            return {
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e),
                'code': 500
            }

    @http.route('/api/customer_forms_filtered', type='json', auth="public", methods=['POST'], csrf=False, cors="*")
    def get_filtered_customer_forms(self, **params):
        api_key = params.get('token')
        if not api_key:
            return {'success': False, 'message': 'Token is missing', 'code': "403"}

        user = self._verify_api_key(api_key)
        if not user:
            return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

        # Filters
        from_date = params.get('from_date')  # format: "YYYY-MM-DD"
        to_date = params.get('to_date')  # format: "YYYY-MM-DD"
        unit_name = params.get('unit_name')  # string
        agent_name = params.get('agent_name')  # string
        order = params.get('order', 'desc')  # 'asc' or 'desc'

        # Compose domain (search filters)
        domain = []

        try:
            if from_date and to_date:
                domain.append(('date', '>=', from_date))
                domain.append(('date', '<=', to_date))
            elif from_date:
                domain.append(('date', '>=', from_date))
            elif to_date:
                domain.append(('date', '<=', to_date))

            if unit_name:
                domain.append(('unit_name', '=', unit_name))

            if agent_name:
                domain.append(('agent_name', '=', agent_name))
        except Exception as e:
            return {'success': False, 'message': f'Invalid filter values: {e}', 'code': "400"}

        # Caching logic
        cache_key = f"filter_forms_{from_date}_{to_date}_{unit_name}_{agent_name}_{order}"
        now = time.time()

        if cache_key in _cached_customer_form_filter_data:
            cached_response, cached_time = _cached_customer_form_filter_data[cache_key]
            if now - cached_time < CACHE_DURATION:
                _logger.info(f"[CACHE] Returning cached data for key: {cache_key}")
                return cached_response

        # Sorting order
        order_by = 'date asc' if order == 'asc' else 'date desc'

        forms = request.env['customer.form'].sudo().search(domain, order=order_by)

        result = [{
            'id': form.id,
            'agent_name': form.agent_name,
            'agent_login': form.agent_login,
            'unit_name': form.unit_name,
            'date': str(form.date),
            'time': form.time,
            'family_head_name': form.family_head_name,
            'father_name': form.father_name,
            'mother_name': form.mother_name,
            'spouse_name': form.spouse_name,
            'house_number': form.house_number,
            'street_number': form.street_number,
            'city': form.city,
            'pin_code': form.pin_code,
            'address': form.address,
            'mobile_number': form.mobile_number,
            'eenadu_newspaper': form.eenadu_newspaper,
            'feedback_to_improve_eenadu_paper': form.feedback_to_improve_eenadu_paper,
            'read_newspaper': form.read_newspaper,
            'current_newspaper': form.current_newspaper,
            'reason_for_not_taking_eenadu_newsPaper': form.reason_for_not_taking_eenadu_newsPaper,
            'reason_not_reading': form.reason_not_reading,
            'free_offer_15_days': form.free_offer_15_days,
            'reason_not_taking_offer': form.reason_not_taking_offer,
            'employed': form.employed,
            'job_type': form.job_type,
            'job_type_one': form.job_type_one,
            'job_profession': form.job_profession,
            'job_designation': form.job_designation,
            'company_name': form.company_name,
            'profession': form.profession,
            'job_working_state': form.job_working_state,
            'job_working_location': form.job_working_location,
            'job_designation_one': form.job_designation_one,
            'latitude': form.latitude,
            'longitude': form.longitude,
            'location_address': form.location_address,
        } for form in forms]

        response = {
            'success': True,
            'records': result,
            'count': len(result),
            'code': "200"
        }

        # Save to cache
        _cached_customer_form_filter_data[cache_key] = (response, now)
        _logger.info(f"[CACHE] Data cached for filtered query key: {cache_key}")

        return response

    @http.route("/update/target", type="json", methods=['POST'], csrf=False, cors="*")
    def _update_status(self, **params):

        api_key = params.get('token')
        if not api_key:
            return {'success': False, 'message': 'Token is missing', 'code': "403"}

        user = self._verify_api_key(api_key)
        if not user:
            return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

        user_id = params.get("user_id")
        if not user_id:
            return {'error': 'User ID is required', "code": "403"}

        try:
            user_id = int(user_id)
        except ValueError:
            return {'error': 'Invalid User ID', "code": "403"}

        user = request.env['res.users'].sudo().browse(user_id)
        if not user.exists():
            return {'error': 'User not found', "code": "403"}
        if params.get("target") ==  "":
            return {'error': 'target is missing'}
        if type(int(params.get("target"))) != type(66):
            return {'error': 'target type is not int, pleas send the number'}

        user.write({
            'target': params.get("target"),
        })
        if str(user.target) == str(params.get("target")):
            return {"success": "True", "user_id": user.id, "code": "200"}
        else:
            return {"success": "False", "code": "403"}

    @http.route("/unit/users", type="json", auth="none", methods=["POST"], csrf=False, cors="*")
    def _users_in_unit(self, **params):
        api_key = params.get('token')
        unit_name = params.get('unit_name')

        # Missing token
        if not api_key:
            return {
                'success': False,
                'message': 'Token is missing',
                'code': 403
            }

        # Verify token
        user = self._verify_api_key(api_key)
        if not user:
            return {
                'success': False,
                'message': 'Invalid or expired token',
                'code': 403
            }

        # Missing unit name
        if not unit_name:
            return {
                'success': False,
                'message': 'Unit name is required',
                'code': 400
            }

        # Fetch users in unit
        users_in_unit = request.env['res.users'].sudo().search([('unit_name', '=', unit_name)])

        # Format user data
        user_data = []
        for u in users_in_unit:
            user_data.append({
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'login': u.login,
                'unit_name': u.unit_name,  # Assumes unit_name is a Char or stores string
                'role': u.role if hasattr(u, 'role') else '',  # Avoid crash if role missing
            })

        return {
            'success': True,
            'message': f'{len(user_data)} user(s) found in unit "{unit_name}"',
            'data': user_data,
            'code': 200,
        }
