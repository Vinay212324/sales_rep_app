from odoo import http, fields
from odoo.http import request
from datetime import datetime, date, time
import pytz
import time
import logging

_logger = logging.getLogger(__name__)

class SelfieController(http.Controller):

    def _verify_api_key(self, token):
        start_time = time.time()
        """Check if the token belongs to a valid user"""
        try:
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            duration = time.time() - start_time
            if user:
                _logger.info(f"_verify_api_key completed successfully in {duration:.4f} seconds for user: {user.login}")
            else:
                _logger.info(f"_verify_api_key completed in {duration:.4f} seconds with no user found for token.")
            return user
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"_verify_api_key failed in {duration:.4f} seconds with error: {str(e)}")
            return False

    @http.route('/api/start_work', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def start_work(self, **post):
        start_time = time.time()
        try:
            token = post.get('token')
            selfie_base64 = post.get('selfie')

            if not token:
                duration = time.time() - start_time
                _logger.info(f"start_work completed in {duration:.4f} seconds with error: Token is required")
                return {'success': False, 'message': 'Token is required', 'code': 403}
            if not selfie_base64:
                duration = time.time() - start_time
                _logger.info(f"start_work completed in {duration:.4f} seconds with error: Selfie is missing")
                return {'success': False, 'message': 'Selfie is missing', 'code': 400}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"start_work completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            # Use UTC time for storage (Odoo standard)
            utc_now = datetime.utcnow()

            session = request.env['work.session'].sudo().create({
                'user_id': user.id,
                'start_time': False,
                'start_selfie': selfie_base64.encode('utf-8'),
            })

            session.write({
                'start_time': utc_now,
            })

            # Convert to IST for response
            ist = pytz.timezone('Asia/Kolkata')
            ist_start_time = pytz.utc.localize(utc_now).astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')

            result = {
                'success': True,
                'message': 'Start selfie saved successfully',
                'session_id': session.id,
                'start_time_ist': ist_start_time,
                'code': 200
            }
            duration = time.time() - start_time
            _logger.info(f"start_work completed successfully in {duration:.4f} seconds for user: {user.login}, session: {session.id}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"start_work failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': 500}

    @http.route('/api/end_work', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def end_work(self, **post):
        start_time = time.time()
        try:
            token = post.get('token')
            selfie_base64 = post.get('selfie')

            if not token:
                duration = time.time() - start_time
                _logger.info(f"end_work completed in {duration:.4f} seconds with error: Token is required")
                return {'success': False, 'message': 'Token is required', 'code': 403}
            if not selfie_base64:
                duration = time.time() - start_time
                _logger.info(f"end_work completed in {duration:.4f} seconds with error: Selfie is missing")
                return {'success': False, 'message': 'Selfie is missing', 'code': 400}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"end_work completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            session = request.env['work.session'].sudo().search([
                ('user_id', '=', user.id),
                ('end_time', '=', False)
            ], order='start_time desc', limit=1)

            if not session:
                duration = time.time() - start_time
                _logger.info(f"end_work completed in {duration:.4f} seconds with error: No active session found")
                return {'success': False, 'message': 'No active session found', 'code': 404}

            # Use UTC time for storage
            utc_now = datetime.utcnow()

            session.write({
                'end_time': utc_now,
                'end_selfie': selfie_base64.encode('utf-8')
            })

            # Convert to IST for response
            ist = pytz.timezone('Asia/Kolkata')
            ist_end_time = pytz.utc.localize(utc_now).astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')

            result = {
                'success': True,
                'message': 'End selfie saved successfully',
                'session_id': session.id,
                'end_time_ist': ist_end_time,
                'code': 200
            }
            duration = time.time() - start_time
            _logger.info(f"end_work completed successfully in {duration:.4f} seconds for user: {user.login}, session: {session.id}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"end_work failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': 500}

    @http.route('/api/user/today_selfies', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def get_today_selfies(self, **post):
        start_time = time.time()
        try:
            token = post.get('token')
            user_id = post.get('user_id')

            if not token or not user_id:
                duration = time.time() - start_time
                _logger.info(f"get_today_selfies completed in {duration:.4f} seconds with error: Token and User ID are required")
                return {'success': False, 'message': 'Token and User ID are required', 'code': 400}

            if not self._verify_api_key(token):
                duration = time.time() - start_time
                _logger.info(f"get_today_selfies completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            ist = pytz.timezone("Asia/Kolkata")
            today = datetime.now(ist).date()
            start_of_day = datetime.combine(today, time.min).replace(tzinfo=None)
            end_of_day = datetime.combine(today, time.max).replace(tzinfo=None)

            sessions = request.env['work.session'].sudo().search([
                ('user_id', '=', int(user_id)),
            ])

            selfie_sessions = []
            from datetime import timedelta

            for session in sessions:
                start_time_session = session.start_time + timedelta(hours=5, minutes=30) if session.start_time else None
                end_time_session = session.end_time + timedelta(hours=5, minutes=30) if session.end_time else None

                selfie_sessions.append({
                    'session_id': session.id,
                    'start_time': str(start_time_session) if start_time_session else None,
                    'end_time': str(end_time_session) if end_time_session else None,
                    'start_selfie': f"data:image/png;base64,{session.start_selfie.decode('utf-8')}" if session.start_selfie else None,
                    'end_selfie': f"data:image/png;base64,{session.end_selfie.decode('utf-8')}" if session.end_selfie else None,
                })

            result = {
                'success': True,
                'user_id': int(user_id),
                'date': str(today),
                'selfies': selfie_sessions,
                'code': 200
            }
            duration = time.time() - start_time
            _logger.info(f"get_today_selfies completed successfully in {duration:.4f} seconds for user: {user_id}, sessions: {len(selfie_sessions)}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_today_selfies failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': 500}

    @http.route('/api/all_pin_locations', type='json', auth='public', methods=['POST'], csrf=False)
    def get_all_pin_locations(self, **kwargs):
        start_time = time.time()
        try:
            token = kwargs.get('token')

            if not token:
                duration = time.time() - start_time
                _logger.info(f"get_all_pin_locations completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing'}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"get_all_pin_locations completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token'}

            pins = request.env['pin.location'].sudo().search([])
            data = [{'id': p.id, 'name': p.name, 'code': p.code, 'location_name': p.location_name, 'phone':p.phone, 'unit_name':p.unit_name} for p in pins]

            result = {'success': True, 'data': data}
            duration = time.time() - start_time
            _logger.info(f"get_all_pin_locations completed successfully in {duration:.4f} seconds, returned {len(data)} locations")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_all_pin_locations failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/api/Pin_location_asin', type='json', auth='public', methods=['POST'], csrf=False)
    def assign_pin_location(self, **kwargs):
        start_time = time.time()
        try:
            token = kwargs.get('token')
            user_id = kwargs.get('user_id')
            pin_location_id = kwargs.get('pin_lo_id')

            if not token or not user_id or not pin_location_id:
                duration = time.time() - start_time
                _logger.info(f"assign_pin_location completed in {duration:.4f} seconds with error: Missing token, user_id, or pin_lo_id")
                return {'success': False, 'message': 'Missing token, user_id, or pin_lo_id'}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"assign_pin_location completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token'}

            target_user = request.env['res.users'].sudo().browse(int(user_id))
            pin_location = request.env['pin.location'].sudo().browse(int(pin_location_id))

            if not target_user.exists():
                duration = time.time() - start_time
                _logger.info(f"assign_pin_location completed in {duration:.4f} seconds with error: User not found")
                return {'success': False, 'message': 'User not found'}
            if not pin_location.exists():
                duration = time.time() - start_time
                _logger.info(f"assign_pin_location completed in {duration:.4f} seconds with error: Pin location not found")
                return {'success': False, 'message': 'Pin location not found'}

            target_user.write({
                'pin_location_ids': [(4, pin_location.id)],
                'present_pin_id': pin_location.id,
            })

            result = {
                'success': True,
                'message': f'Pin location {pin_location.location_name} assigned to user {target_user.name}'
            }
            duration = time.time() - start_time
            _logger.info(f"assign_pin_location completed successfully in {duration:.4f} seconds for user: {user_id}, location: {pin_location_id}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"assign_pin_location failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/api/get_current_pin_location', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def get_current_pin_location_of_user(self, **kwargs):
        start_time = time.time()
        try:
            token = kwargs.get('token')

            if not token:
                duration = time.time() - start_time
                _logger.info(f"get_current_pin_location_of_user completed in {duration:.4f} seconds with error: Token is required")
                return {'success': False, 'message': 'Token is required', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"get_current_pin_location_of_user completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            pin = user.present_pin_id
            if not pin:
                duration = time.time() - start_time
                _logger.info(f"get_current_pin_location_of_user completed in {duration:.4f} seconds with error: No current pin location assigned")
                return {'success': False, 'message': 'No current pin location assigned', 'code': 404}

            result = {
                'success': True,
                'data': {
                    'id': pin.id,
                    'name': pin.name,
                    'location_name': pin.location_name,
                    'code': pin.code
                },
                'code': 200
            }
            duration = time.time() - start_time
            _logger.info(f"get_current_pin_location_of_user completed successfully in {duration:.4f} seconds for user: {user.login}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_current_pin_location_of_user failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e), 'code': 500}

    @http.route('/api/create_pin_location', type='json', auth='public', methods=['POST'], csrf=False)
    def create_pin_location(self, **kwargs):
        start_time = time.time()
        try:
            # Token authentication
            token = kwargs.get('token')
            if not token:
                duration = time.time() - start_time
                _logger.info(f"create_pin_location completed in {duration:.4f} seconds with error: Token is missing")
                return {'success': False, 'message': 'Token is missing'}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"create_pin_location completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token'}

            # Required fields
            required_fields = ['code', 'location_name', 'phone', 'unit_name']
            for field in required_fields:
                if not kwargs.get(field):
                    duration = time.time() - start_time
                    _logger.info(f"create_pin_location completed in {duration:.4f} seconds with error: Missing field: {field}")
                    return {'success': False, 'message': f'Missing field: {field}'}

            # Create the record
            pin = request.env['pin.location'].sudo().create({
                'code': kwargs.get('code'),
                'location_name': kwargs.get('location_name'),
                'phone': kwargs.get('phone'),
                'unit_name': kwargs.get('unit_name'),
            })

            result = {
                'success': True,
                'message': 'Pin location created successfully',
                'data': {
                    'id': pin.id,
                    'code': pin.code,
                    'location_name': pin.location_name,
                    'phone': pin.phone,
                    'unit_name': pin.unit_name
                }
            }
            duration = time.time() - start_time
            _logger.info(f"create_pin_location completed successfully in {duration:.4f} seconds for location: {pin.id}")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"create_pin_location failed in {duration:.4f} seconds with error: {str(e)}")
            return {'success': False, 'message': str(e)}