import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
from werkzeug.utils import redirect
import json
import uuid
import hmac
import hashlib
import requests
import time
from datetime import date
import base64
from datetime import date
import time
import logging
from datetime import date
import requests
from odoo import http
from odoo.http import request
import logging

# Cache storage (module-level)
_cached_data = {}
_cached_customer_form_filter_data = {}

_logger = logging.getLogger(__name__)
SECRET_KEY = 'your_secret_key'
CACHE_DURATION = 6
from datetime import date


class CustomerFormAPI(http.Controller):

    def _verify_api_key(self, token):
        start_time = time.time()
        try:
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            if not user:
                user = False
                duration = time.time() - start_time
                _logger.info(f"_verify_api_key completed in {duration:.4f} seconds with no user found for token.")
                return user
            result = {"success": "True", "user_Id": user.id, "user_login": user.login}
            duration = time.time() - start_time
            _logger.info(f"_verify_api_key completed successfully in {duration:.4f} seconds for user: {user.login}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"_verify_api_key failed in {duration:.4f} seconds with error: {str(e)}")
            return False

    @http.route('/api/customer_form', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def create_customer(self, **kwargs):
        start_time = time.time()
        try:
            api_key = kwargs.get('token')
            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"create_customer completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': "403"}

            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"create_customer completed in {duration:.4f} seconds with error: Invalid or expired token")
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
                'location_url': kwargs.get('location_url'),
                'face_base64': kwargs.get('face_base64'),
                'for_consider': kwargs.get('for_consider'),
                'shift_to_EENADU': kwargs.get('shift_to_EENADU', False),
                'Willing_to_Shift_to_EENADU': kwargs.get('would_like_to_stay_with_existing_news_papar', False),
                'Start_Circulating': kwargs.get('Start_Circulating'),
                'Agency': kwargs.get('Agency'),
                'age': kwargs.get('age'),
                'customer_type': kwargs.get('customer_type'),
                'occupation': kwargs.get('occupation'),
            })

            msg = (
                f"ఈనాడు చందాదారునిగా చేరినందుకు ధన్యవాదాలు.మీరు కోరిన విధంగా {kwargs.get('date')} వ తేదీ నుండి పత్రిక సరఫరా చేయబడుతుంది.ఈనాడు సర్క్యులేషన్."
            )

            # SMS API URL
            sms_url = "https://smsstriker.com/API/unicodesms.php"

            # Create payload with correct parameters
            payload = {
                'username': 'EERETA',
                'password': 'EERETA',
                'from': 'EERETA',
                'to': kwargs.get('mobile_number'),
                'msg': msg,
                'type': '1',
                'dnd_check': '0',  # Ensure Do Not Disturb is disabled
                'template_id': '1407175508018474089'  # Template ID as provided
            }

            # Send SMS request
            response = requests.get(sms_url, params=payload)

            # Check if SMS was sent successfully
            if response.status_code != 200:
                _logger.error(f"SMS sending failed: {response.text}")
                duration = time.time() - start_time
                _logger.error(f"create_customer failed in {duration:.4f} seconds: SMS failed")
                return {'success': False, 'message': 'Failed to send SMS', 'code': "500"}

            result = {'success': True, 'message': 'Customer Form created successfully', 'customer_id': customer.id,
                      "code": "200"}
            duration = time.time() - start_time
            _logger.info(
                f"create_customer completed successfully in {duration:.4f} seconds for customer_id: {customer.id}")
            return result

        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            _logger.error(f"create_customer failed in {duration:.4f} seconds: SMS request failed - {str(e)}")
            return {'success': False, 'message': 'Error in SMS API request', 'code': "500"}

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"create_customer failed in {duration:.4f} seconds with unexpected error: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}', 'code': "500"}

    @http.route('/api/login', type='json', auth='public', methods=['POST'])
    def api_login(self, email, password):
        start_time = time.time()
        try:
            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"api_login completed in {duration:.4f} seconds: User not found")
                raise AccessDenied("User not found!")
            try:
                user.sudo()._check_credentials(password, {'interactive': True})
            except AccessDenied:
                duration = time.time() - start_time
                _logger.info(f"api_login completed in {duration:.4f} seconds: Invalid password")
                raise AccessDenied("Invalid password!")
            user.generate_token()
            result = {'status': 'success', 'user_id': user.id, 'name': user.name, 'role': user.role,
                      'token': user.api_token,
                      'token_expiry': user.token_expiry}
            duration = time.time() - start_time
            _logger.info(f"api_login completed successfully in {duration:.4f} seconds for user: {email}")
            return result
        except AccessDenied:
            raise
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"api_login failed in {duration:.4f} seconds with error: {str(e)}")
            raise

    @http.route('/api/logout', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def api_logout(self, token):
        start_time = time.time()
        try:
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"api_logout completed in {duration:.4f} seconds: Invalid token")
                raise AccessDenied("Invalid token!")
            user.clear_token()
            result = {'status': 'success', 'message': "User logged out successfully", "code": "200"}
            duration = time.time() - start_time
            _logger.info(f"api_logout completed successfully in {duration:.4f} seconds for token: {token[:10]}...")
            return result
        except AccessDenied:
            raise
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"api_logout failed in {duration:.4f} seconds with error: {str(e)}")
            raise

    @http.route('/token_validation', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def token_validation(self, **params):
        start_time = time.time()
        try:
            api_key = params.get('token')
            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"token_validation completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': "403"}
            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"token_validation completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', "code": "403"}
            result = {'success': True, 'message': 'Valid token', 'user_login': user, "code": "200"}
            duration = time.time() - start_time
            _logger.info(
                f"token_validation completed successfully in {duration:.4f} seconds for user: {user.get('user_login', 'unknown')}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"token_validation failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': 'Error: {}'.format(str(e)), 'code': "403"}

    @http.route('/api/customer_forms_info', type='json', auth="public", methods=['POST'], csrf=False, cors="*")
    def get_customer_forms(self, **params):
        start_time = time.time()
        try:
            api_key = params.get('token')

            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"get_customer_forms completed in {duration:.4f} seconds with error: Token is missing")
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': "403"
                }

            # Validate Token
            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {
                    'success': False,
                    'message': 'Invalid or expired token',
                    "code": "403"
                }

            user_id = params.get("user_id")
            if not user_id:
                duration = time.time() - start_time
                _logger.info(f"get_customer_forms completed in {duration:.4f} seconds with error: User ID is required")
                return {'error': 'User ID is required', "code": "403"}

            try:
                user_id = int(user_id)
            except ValueError:
                duration = time.time() - start_time
                _logger.info(f"get_customer_forms completed in {duration:.4f} seconds with error: Invalid User ID")
                return {'error': 'Invalid User ID', "code": "403"}

            # Fetch user details
            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                duration = time.time() - start_time
                _logger.info(f"get_customer_forms completed in {duration:.4f} seconds with error: User not found")
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
                'location_url': record.location_url,
                'face_base64': f"data:image/png;base64,{record.face_base64.decode('utf-8')}" if record.face_base64 else None,
                'for_consider': record.for_consider,
                'shift_to_EENADU': record.shift_to_EENADU,
                'would_like_to_stay_with_existing_news_papar': record.Willing_to_Shift_to_EENADU,
                'Start_Circulating': record.Start_Circulating,
                'Agency': record.Agency,
                'age': record.age,
                'customer_type': record.customer_type,
                'occupation': record.occupation
            } for record in customer_forms]

            response = {'records': result, "code": "200"}
            duration = time.time() - start_time
            _logger.info(
                f"get_customer_forms completed successfully in {duration:.4f} seconds, returned {len(result)} records for agent: {agent_login}")
            return response
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_customer_forms failed in {duration:.4f} seconds with error: {str(e)}")
            raise

    @http.route('/api/users', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def getting_users(self, **kw):
        start_time = time.time()
        try:

            api_key = kw.get('token')

            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"getting_users completed in {duration:.4f} seconds with error: Token is missing")
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': "403"
                }

            # Validate Token
            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"getting_users completed in {duration:.4f} seconds with error: Invalid or expired token")
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
                    'pan_image': pan_image_data,
                })

            result = {'status': 200, 'users': user_list}
            duration = time.time() - start_time
            _logger.info(
                f"getting_users completed successfully in {duration:.4f} seconds, returned {len(user_list)} users")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"getting_users failed in {duration:.4f} seconds with error: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route('/api/users_you_created', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def users_you_created(self, **kw):
        start_time = time.time()
        try:

            api_key = kw.get('token')

            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"users_you_created completed in {duration:.4f} seconds with error: Token is missing")
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': "403"
                }

            # Validate Token
            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"users_you_created completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {
                    'success': False,
                    'message': 'Invalid or expired token',
                    "code": "403"
                }
            user = request.env['res.users'].sudo().search([('api_token', '=', api_key)], limit=1)
            user_id = user.id
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

            result = {'status': 200, 'users': user_list}
            duration = time.time() - start_time
            _logger.info(
                f"users_you_created completed successfully in {duration:.4f} seconds, returned {len(user_list)} users for creator: {user_id}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"users_you_created failed in {duration:.4f} seconds with error: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route('/api/users_you_created/id', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def users_you_created_byId(self, **kw):
        start_time = time.time()
        try:

            api_key = kw.get('token')

            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"users_you_created_byId completed in {duration:.4f} seconds with error: Token is missing")
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': "403"
                }

            # Validate Token
            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"users_you_created_byId completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {
                    'success': False,
                    'message': 'Invalid or expired token',
                    "code": "403"
                }

            user_id = int(kw.get('id'))
            if not (user_id):
                duration = time.time() - start_time
                _logger.info(
                    f"users_you_created_byId completed in {duration:.4f} seconds with error: user ID Not found")
                return {"message": "user ID Not found"}
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

            result = {'status': 200, 'users': user_list}
            duration = time.time() - start_time
            _logger.info(
                f"users_you_created_byId completed successfully in {duration:.4f} seconds, returned {len(user_list)} users for creator: {user_id}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"users_you_created_byId failed in {duration:.4f} seconds with error: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route('/api/customer_forms_info_one_day', type='json', auth="public", methods=['POST'], csrf=False, cors="*")
    def get_customer_forms_one_day(self, **params):
        """
        API to fetch today's customer forms entered by a specific agent.
        Uses caching to reduce database load.
        """
        start_time = time.time()
        try:
            api_key = params.get('token')
            if not api_key:
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_one_day completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': "403"}

            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_one_day completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

            user_id = params.get("user_id")
            if not user_id:
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_one_day completed in {duration:.4f} seconds with error: User ID is required")
                return {'error': 'User ID is required', "code": "403"}

            try:
                user_id = int(user_id)
            except ValueError:
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_one_day completed in {duration:.4f} seconds with error: Invalid User ID")
                return {'error': 'Invalid User ID', "code": "403"}

            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_one_day completed in {duration:.4f} seconds with error: User not found")
                return {'error': 'User not found', "code": "403"}

            agent_login = user.login
            today_date = date.today()

            # Define cache key
            cache_key = f"customer_forms_one_day_{agent_login}_{today_date}"
            now = time.time()

            # Use cache if available and valid
            if cache_key in _cached_data:
                cached_response, cached_time = _cached_data[cache_key]
                if now - cached_time < CACHE_DURATION:
                    _logger.info(f"[CACHE] Returning cached data for {agent_login}")
                    duration = time.time() - start_time
                    _logger.info(
                        f"get_customer_forms_one_day completed from cache in {duration:.4f} seconds for agent: {agent_login}")
                    return cached_response

            # Cache expired or not found – fetch from DB
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
                'location_url': record.location_url,
                'face_base64': f"data:image/png;base64,{record.face_base64.decode('utf-8')}" if record.face_base64 else None,
                'for_consider': record.for_consider,
                'shift_to_EENADU': record.shift_to_EENADU,
                'would_like_to_stay_with_existing_news_papar': record.Willing_to_Shift_to_EENADU,
                'Start_Circulating': record.Start_Circulating,
                'Agency': record.Agency,
                'age': record.age,
                'customer_type': record.customer_type,
                'occupation': record.occupation
            } for record in customer_forms]

            response = {
                'records': result,
                'count': len(result),
                'code': "200"
            }

            # Store result in cache
            _cached_data[cache_key] = (response, now)
            _logger.info(f"[CACHE] Data cached for {agent_login} with {len(result)} records.")

            duration = time.time() - start_time
            _logger.info(
                f"get_customer_forms_one_day completed successfully in {duration:.4f} seconds, returned {len(result)} records for agent: {agent_login}")
            return response
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_customer_forms_one_day failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': "500"}

    @http.route('/api/customer_forms_info_id', type='json', auth="public", methods=['POST'], csrf=False, cors="*")
    def get_customer_forms_info_id(self, **params):
        """
        API to fetch all customer forms entered by a specific agent.
        Uses caching to reduce database load.
        """
        start_time = time.time()
        try:
            api_key = params.get('token')
            if not api_key:
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_info_id completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': "403"}

            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_info_id completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

            user_id = params.get("user_id")
            if not user_id:
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_info_id completed in {duration:.4f} seconds with error: User ID is required")
                return {'error': 'User ID is required', "code": "403"}

            try:
                user_id = int(user_id)
            except ValueError:
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_info_id completed in {duration:.4f} seconds with error: Invalid User ID")
                return {'error': 'Invalid User ID', "code": "403"}

            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                duration = time.time() - start_time
                _logger.info(
                    f"get_customer_forms_info_id completed in {duration:.4f} seconds with error: User not found")
                return {'error': 'User not found', "code": "403"}

            agent_login = user.login

            # Define cache key (no date, since it's all records)
            cache_key = f"customer_forms_all_{agent_login}"
            now = time.time()

            # Use cache if available and valid
            if cache_key in _cached_data:
                cached_response, cached_time = _cached_data[cache_key]
                if now - cached_time < CACHE_DURATION:
                    _logger.info(f"[CACHE] Returning cached data for {agent_login}")
                    duration = time.time() - start_time
                    _logger.info(
                        f"get_customer_forms_info_id completed from cache in {duration:.4f} seconds for agent: {agent_login}")
                    return cached_response

            # Cache expired or not found – fetch from DB (all records for agent)
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
                'location_url': record.location_url,
                'face_base64': f"data:image/png;base64,{record.face_base64.decode('utf-8')}" if record.face_base64 else None,
                'for_consider': record.for_consider,
                'shift_to_EENADU': record.shift_to_EENADU,
                'would_like_to_stay_with_existing_news_papar': record.Willing_to_Shift_to_EENADU,
                'Start_Circulating': record.Start_Circulating,
                'Agency': record.Agency,
                'age': record.age,
                'customer_type': record.customer_type,
                'occupation': record.occupation
            } for record in customer_forms]

            response = {
                'records': result,
                'count': len(result),
                'code': "200"
            }

            # Store result in cache
            _cached_data[cache_key] = (response, now)
            _logger.info(f"[CACHE] Data cached for {agent_login} with {len(result)} records.")

            duration = time.time() - start_time
            _logger.info(
                f"get_customer_forms_info_id completed successfully in {duration:.4f} seconds, returned {len(result)} records for agent: {agent_login}")
            return response
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_customer_forms_info_id failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': "500"}

    @http.route("/update/status", type="json", methods=['POST'], csrf=False, cors="*")
    def _update_status(self, **params):
        start_time = time.time()
        try:
            api_key = params.get('token')
            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': "403"}

            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

            user_id = params.get("user_id")
            if not user_id:
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: User ID is required")
                return {'error': 'User ID is required', "code": "403"}

            try:
                user_id = int(user_id)
            except ValueError:
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: Invalid User ID")
                return {'error': 'Invalid User ID', "code": "403"}

            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: User not found")
                return {'error': 'User not found', "code": "403"}
            if params.get("status") not in ["active", "un_activ"]:
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: status is missing")
                return {'error': 'status is missing'}

            user.write({
                'status': params.get("status"),
            })
            if user.status == params.get("status"):
                result = {"success": "True", "user_id": user.id, "code": "200"}
                duration = time.time() - start_time
                _logger.info(f"_update_status completed successfully in {duration:.4f} seconds for user: {user_id}")
                return result
            else:
                duration = time.time() - start_time
                _logger.warning(
                    f"_update_status completed in {duration:.4f} seconds but status update failed for user: {user_id}")
                return {"success": "False", "code": "403"}
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"_update_status failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': "500"}

    @http.route('/api/agents_info_based_on_the_unit', type='json', auth='public', methods=['POST'], csrf=False,
                cors="*")
    def agents_info_based_on_the_unit(self, **kw):
        start_time = time.time()
        try:

            api_key = kw.get('token')
            unit_name = kw.get('unit_name')

            if not api_key:
                duration = time.time() - start_time
                _logger.info(
                    f"agents_info_based_on_the_unit completed in {duration:.4f} seconds with error: Token is missing")
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': "403"
                }

            # Validate Token
            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"agents_info_based_on_the_unit completed in {duration:.4f} seconds with error: Invalid or expired token")
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

            result = {'status': 200, 'users': user_list}
            duration = time.time() - start_time
            _logger.info(
                f"agents_info_based_on_the_unit completed successfully in {duration:.4f} seconds, returned {len(user_list)} agents for unit: {unit_name}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"agents_info_based_on_the_unit failed in {duration:.4f} seconds with error: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route('/api/For_root_map_asin', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def For_root_map_asin(self, **kw):
        start_time = time.time()
        try:
            user_id = int(kw.get('agent_id'))
            token = kw.get('token')
            from_to_list = kw.get('from_to_list', [])
            root_map_id = kw.get('root_map_id')

            if not token:
                duration = time.time() - start_time
                _logger.info(f"For_root_map_asin completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"For_root_map_asin completed in {duration:.4f} seconds with error: Invalid token")
                return {'success': False, 'message': 'Invalid token', 'code': 403}

            agent = request.env['res.users'].sudo().browse(user_id)
            if not agent.exists():
                duration = time.time() - start_time
                _logger.info(f"For_root_map_asin completed in {duration:.4f} seconds with error: Agent not found")
                return {'success': False, 'message': 'Agent not found', 'code': 404}

            fromto_obj = request.env['fromto.rootmap'].sudo()
            linked_ids = []
            root_map_rec = False

            # Only create root.map if flag is "true" (string)
            if not root_map_id:
                root_map_rec = request.env['root.map'].sudo().create({
                    'root_name': user["user_login"],
                    'date': date.today(),
                    'stage_dd': 'not_working',
                    'user_id': [(6, 0, [agent.id])],
                })
            else:
                root_map_rec = request.env['root.map'].sudo().browse(int(root_map_id))

            for pair in from_to_list:
                from_loc = pair.get('from_location')
                to_loc = pair.get('to_location')

                if not from_loc or not to_loc:
                    continue

                fromto_rec = fromto_obj.search([
                    ('from_location', '=', from_loc),
                    ('to_location', '=', to_loc)
                ], limit=1)

                if not fromto_rec:
                    fromto_rec = fromto_obj.create({
                        'from_location': from_loc,
                        'to_location': to_loc
                    })

                if root_map_rec and fromto_rec.id not in root_map_rec.for_fromto_ids.ids:
                    root_map_rec.write({'for_fromto_ids': [(4, fromto_rec.id)]})

                linked_ids.append(fromto_rec.id)

            if root_map_rec:
                agent.sudo().write({'root_name_id': root_map_rec.id})

            result = {
                'success': True,
                'message': 'Root map info updated successfully',
                'linked_ids': linked_ids,
                'code': 200
            }
            duration = time.time() - start_time
            _logger.info(
                f"For_root_map_asin completed successfully in {duration:.4f} seconds for agent: {user_id}, linked {len(linked_ids)} ids")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"For_root_map_asin failed in {duration:.4f} seconds with error: {str(e)}")
            return {
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e),
                'code': 500
            }

    @http.route('/api/change_root_map_stage', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def change_root_map_stage(self, **kw):
        start_time = time.time()
        try:
            token = kw.get('token')
            root_map_id = kw.get('root_map_id')
            new_stage = kw.get('stage')  # Expected: 'not_working', 'vinay', 'workingg'

            if not token:
                duration = time.time() - start_time
                _logger.info(f"change_root_map_stage completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"change_root_map_stage completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            if not root_map_id or not new_stage:
                duration = time.time() - start_time
                _logger.info(
                    f"change_root_map_stage completed in {duration:.4f} seconds with error: Missing root_map_id or stage")
                return {'success': False, 'message': 'Missing root_map_id or stage', 'code': 400}

            if new_stage not in ['not_working', 'vinay', 'workingg']:
                duration = time.time() - start_time
                _logger.info(
                    f"change_root_map_stage completed in {duration:.4f} seconds with error: Invalid stage value")
                return {'success': False, 'message': 'Invalid stage value', 'code': 400}

            root_map = request.env['root.map'].sudo().browse(int(root_map_id))
            if not root_map.exists():
                duration = time.time() - start_time
                _logger.info(
                    f"change_root_map_stage completed in {duration:.4f} seconds with error: Root map not found")
                return {'success': False, 'message': 'Root map not found', 'code': 404}

            root_map.write({'stage_dd': new_stage})

            result = {
                'success': True,
                'message': f"Stage updated to '{new_stage}'",
                'status': 200,
                'root_map': {
                    'id': root_map.id,
                    'name': root_map.root_name,
                    'stage': root_map.stage_dd
                }
            }
            duration = time.time() - start_time
            _logger.info(
                f"change_root_map_stage completed successfully in {duration:.4f} seconds for root_map: {root_map_id}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"change_root_map_stage failed in {duration:.4f} seconds with error: {str(e)}")
            return {
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e),
                'code': 500
            }

    @http.route('/api/user_root_maps_by_stage', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def user_root_maps_by_stage(self, **kw):
        start_time = time.time()
        try:
            user_id = kw.get('user_id')
            token = kw.get('token')

            if not token:
                duration = time.time() - start_time
                _logger.info(
                    f"user_root_maps_by_stage completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"user_root_maps_by_stage completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            # Get the target user (agent)
            agent = request.env['res.users'].sudo().browse(int(user_id))
            if not agent.exists():
                duration = time.time() - start_time
                _logger.info(f"user_root_maps_by_stage completed in {duration:.4f} seconds with error: User not found")
                return {'success': False, 'message': 'User not found', 'code': 404}

            # Fetch root.map records linked to this user
            root_maps = request.env['root.map'].sudo().search([
                ('user_id', 'in', [agent.id])
            ])

            # Organize by stage
            assigned = []
            working = []
            done = []

            for record in root_maps:
                from_to_data = []
                for fromto in record.for_fromto_ids:
                    from_to_data.append({
                        'id': fromto.id,
                        'from_location': fromto.from_location,
                        'extra_point': fromto.extra_point,
                        'to_location': fromto.to_location,
                    })
                root_data = {
                    'id': record.id,
                    'name': record.root_name,
                    'date': str(record.date),
                    'stage': record.stage_dd,
                    'from_to': from_to_data
                }

                if record.stage_dd == 'not_working':
                    assigned.append(root_data)
                elif record.stage_dd == 'vinay':
                    working.append(root_data)
                elif record.stage_dd == 'workingg':
                    done.append(root_data)

            result = {
                'success': True,
                'status': 200,
                'user_id': agent.id,
                'assigned': assigned,
                'working': working,
                'done': done
            }
            duration = time.time() - start_time
            total_maps = len(assigned) + len(working) + len(done)
            _logger.info(
                f"user_root_maps_by_stage completed successfully in {duration:.4f} seconds for user: {user_id}, total maps: {total_maps}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"user_root_maps_by_stage failed in {duration:.4f} seconds with error: {str(e)}")
            return {
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e),
                'code': 500
            }

    @http.route('/api/for_assign_extra_point', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def for_assign_extra_point(self, **kw):
        start_time = time.time()
        try:
            location_id = kw.get('location_id')
            api_key = kw.get('token')
            extra_point = kw.get('extra_point')

            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"for_assign_extra_point completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': 403}

            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"for_assign_extra_point completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            if not location_id:
                duration = time.time() - start_time
                _logger.info(
                    f"for_assign_extra_point completed in {duration:.4f} seconds with error: Location ID is missing")
                return {'success': False, 'message': 'Location ID is missing', 'code': 400}

            if extra_point is None:
                duration = time.time() - start_time
                _logger.info(
                    f"for_assign_extra_point completed in {duration:.4f} seconds with error: Extra point is missing")
                return {'success': False, 'message': 'Extra point is missing', 'code': 400}

            fromto_rec = request.env['fromto.rootmap'].sudo().search([
                ('id', '=', int(location_id))
            ], limit=1)

            if not fromto_rec:
                duration = time.time() - start_time
                _logger.info(
                    f"for_assign_extra_point completed in {duration:.4f} seconds with error: Location not found")
                return {'success': False, 'message': 'Location not found', 'code': 404}

            try:
                fromto_rec.sudo().write({'extra_point': extra_point})
                result = {'success': True, 'message': 'Extra point assigned successfully', 'code': 200}
                duration = time.time() - start_time
                _logger.info(
                    f"for_assign_extra_point completed successfully in {duration:.4f} seconds for location: {location_id}")
                return result
            except Exception as inner_e:
                duration = time.time() - start_time
                _logger.error(f"for_assign_extra_point failed in {duration:.4f} seconds: {str(inner_e)}")
                return {'success': False, 'message': f'Error assigning extra point: {str(inner_e)}', 'code': 500}
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"for_assign_extra_point failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': f'Error assigning extra point: {str(e)}', 'code': 500}

    @http.route('/api/for_agent_root_map_name', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def For_agent_root_map_name(self, **kw):
        start_time = time.time()
        try:
            agent_id = kw.get('agent_id')
            api_key = kw.get('token')

            if not api_key:
                duration = time.time() - start_time
                _logger.info(
                    f"For_agent_root_map_name completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': 403}

            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"For_agent_root_map_name completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            # Get agent
            agent = request.env['res.users'].sudo().search([('id', '=', int(agent_id))], limit=1)
            if not agent:
                duration = time.time() - start_time
                _logger.info(f"For_agent_root_map_name completed in {duration:.4f} seconds with error: Agent not found")
                return {'success': False, 'message': 'Agent not found', 'code': 404}

            root_map = agent.root_name_id
            if not root_map:
                duration = time.time() - start_time
                _logger.info(
                    f"For_agent_root_map_name completed in {duration:.4f} seconds with error: No root map assigned to agent")
                return {'success': False, 'message': 'No root map assigned to agent', 'code': 404}

            # Collect linked from-to routes
            from_to_list = []
            for route in root_map.for_fromto_ids:
                from_to_list.append({
                    'id': route.id,
                    'from_location': route.from_location,
                    'to_location': route.to_location
                })

            result = {
                'success': True,
                'status': 200,
                'agent_id': agent.id,
                'root_map': {
                    'id': root_map.id,
                    'name': root_map.root_name,
                    'stage': root_map.stage_dd,
                    'date': str(root_map.date),
                    'from_to_list': from_to_list
                }
            }
            duration = time.time() - start_time
            _logger.info(
                f"For_agent_root_map_name completed successfully in {duration:.4f} seconds for agent: {agent_id}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"For_agent_root_map_name failed in {duration:.4f} seconds with error: {str(e)}")
            return {
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e),
                'code': 500
            }

    @http.route('/unit_name_of_user', type='json', auth='none', methods=["POST"], csrf=False, cors="*")
    def get_unit_names(self, **kwargs):
        start_time = time.time()
        try:
            api_key = kwargs.get('token')
            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"get_unit_names completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': "403"}

            user = request.env['res.users'].sudo().search([('api_token', '=', api_key)], limit=1)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"get_unit_names completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

            # Return list of unit names
            unit_names = [{'id': unit.id, 'name': unit.name} for unit in user.unit_name_ids]

            result = {
                'success': True,
                'unit_names': unit_names,
                'code': 200
            }
            duration = time.time() - start_time
            _logger.info(
                f"get_unit_names completed successfully in {duration:.4f} seconds, returned {len(unit_names)} units for user: {user.login}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_unit_names failed in {duration:.4f} seconds with error: {str(e)}")
            return {
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e),
                'code': 500
            }

    @http.route('/api/customer_forms_filtered', type='json', auth="public", methods=['POST'], csrf=False, cors="*")
    def get_filtered_customer_forms(self, **params):
        start_time = time.time()
        try:
            api_key = params.get('token')
            if not api_key:
                duration = time.time() - start_time
                _logger.info(
                    f"get_filtered_customer_forms completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': "403"}

            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(
                    f"get_filtered_customer_forms completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

            # Filters
            from_date = params.get('from_date')  # format: "YYYY-MM-DD"
            to_date = params.get('to_date')  # format: "YYYY-MM-DD"
            unit_name = params.get('unit_name')  # string
            agent_name = params.get('agent_name')  # string
            Agency = params.get('Agency')  # string
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
                if Agency:
                    domain.append(('Agency', '=', Agency))

            except Exception as e:
                duration = time.time() - start_time
                _logger.error(
                    f"get_filtered_customer_forms failed in {duration:.4f} seconds with error: Invalid filter values - {str(e)}")
                return {'success': False, 'message': f'Invalid filter values: {e}', 'code': "400"}

            # Caching logic
            cache_key = f"filter_forms_{from_date or ''}_{to_date or ''}_{unit_name or ''}_{agent_name or ''}_{Agency or ''}_{order}"
            now = time.time()

            if cache_key in _cached_customer_form_filter_data:
                cached_response, cached_time = _cached_customer_form_filter_data[cache_key]
                if now - cached_time < CACHE_DURATION:
                    _logger.info(f"[CACHE] Returning cached data for key: {cache_key}")
                    duration = time.time() - start_time
                    _logger.info(f"get_filtered_customer_forms completed from cache in {duration:.4f} seconds")
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
                'location_url': form.location_url,
                'face_base64': f"data:image/png;base64,{form.face_base64.decode('utf-8')}" if form.face_base64 else None,
                'for_consider': form.for_consider,
                'shift_to_EENADU': form.shift_to_EENADU,
                'would_like_to_stay_with_existing_news_papar': form.Willing_to_Shift_to_EENADU,
                'Start_Circulating': form.Start_Circulating,
                'Agency': form.Agency,
                'age': form.age,
                'customer_type': form.customer_type,
                'occupation': form.occupation
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

            duration = time.time() - start_time
            _logger.info(
                f"get_filtered_customer_forms completed successfully in {duration:.4f} seconds, returned {len(result)} records")
            return response
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_filtered_customer_forms failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': "500"}

    @http.route("/update/target", type="json", methods=['POST'], csrf=False, cors="*")
    def _update_target(self, **params):
        start_time = time.time()
        try:
            api_key = params.get('token')
            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"_update_target completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing', 'code': "403"}

            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"_update_target completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': "403"}

            user_id = params.get("user_id")
            if not user_id:
                duration = time.time() - start_time
                _logger.info(f"_update_target completed in {duration:.4f} seconds with error: User ID is required")
                return {'error': 'User ID is required', "code": "403"}

            try:
                user_id = int(user_id)
            except ValueError:
                duration = time.time() - start_time
                _logger.info(f"_update_target completed in {duration:.4f} seconds with error: Invalid User ID")
                return {'error': 'Invalid User ID', "code": "403"}

            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                duration = time.time() - start_time
                _logger.info(f"_update_target completed in {duration:.4f} seconds with error: User not found")
                return {'error': 'User not found', "code": "403"}
            if params.get("target") == "":
                duration = time.time() - start_time
                _logger.info(f"_update_target completed in {duration:.4f} seconds with error: target is missing")
                return {'error': 'target is missing'}
            try:
                target_val = int(params.get("target"))
            except ValueError:
                duration = time.time() - start_time
                _logger.info(f"_update_target completed in {duration:.4f} seconds with error: target type is not int")
                return {'error': 'target type is not int, please send the number'}

            user.write({
                'target': target_val,
            })
            if str(user.target) == str(target_val):
                result = {"success": "True", "user_id": user.id, "code": "200"}
                duration = time.time() - start_time
                _logger.info(f"_update_target completed successfully in {duration:.4f} seconds for user: {user_id}")
                return result
            else:
                duration = time.time() - start_time
                _logger.warning(
                    f"_update_target completed in {duration:.4f} seconds but target update failed for user: {user_id}")
                return {"success": "False", "code": "403"}
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"_update_target failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': "500"}

    @http.route("/unit/users", type="json", auth="none", methods=["POST"], csrf=False, cors="*")
    def _users_in_unit(self, **params):
        start_time = time.time()
        try:
            api_key = params.get('token')
            unit_name = params.get('unit_name')

            # Missing token
            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"_users_in_unit completed in {duration:.4f} seconds with error: Token is missing")
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': 403
                }

            # Verify token
            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"_users_in_unit completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {
                    'success': False,
                    'message': 'Invalid or expired token',
                    'code': 403
                }

            # Missing unit name
            if not unit_name:
                duration = time.time() - start_time
                _logger.info(f"_users_in_unit completed in {duration:.4f} seconds with error: Unit name is required")
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

            result = {
                'success': True,
                'message': f'{len(user_data)} user(s) found in unit "{unit_name}"',
                'data': user_data,
                'code': 200,
            }
            duration = time.time() - start_time
            _logger.info(
                f"_users_in_unit completed successfully in {duration:.4f} seconds, returned {len(user_data)} users for unit: {unit_name}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"_users_in_unit failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': 500}

    @http.route('/api/user/id', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def get_users(self, **kw):
        start_time = time.time()
        try:

            api_key = kw.get('token')
            agent_id = kw.get('id')

            if not api_key:
                duration = time.time() - start_time
                _logger.info(f"get_users completed in {duration:.4f} seconds with error: Token is missing")
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': "403"
                }

            # Validate Token
            user = self._verify_api_key(api_key)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"get_users completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {
                    'success': False,
                    'message': 'Invalid or expired token',
                    "code": "403"
                }

            # Fetch users
            users = request.env['res.users'].sudo().search([('id', '=', int(agent_id))], limit=1)
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
                    'pan_image': pan_image_data,
                })

            result = {'status': 200, 'users': user_list}
            duration = time.time() - start_time
            _logger.info(f"get_users completed successfully in {duration:.4f} seconds, returned user {agent_id}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_users failed in {duration:.4f} seconds with error: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}