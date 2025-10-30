from odoo import http, fields
from odoo.http import request
from datetime import datetime, date, time
import pytz
import time

class SelfieController(http.Controller):

    def _update_function_timing(self, function_name, execution_time):
        """
        Helper method to update or create timing record for a function.
        """
        if execution_time < 0:
            return  # Skip invalid times

        Timing = request.env['function.timing'].sudo()
        existing = Timing.search([('name', '=', function_name)], limit=1)
        if existing:
            existing.write({
                'total_time': existing.total_time + execution_time,
                'min_time': min(existing.min_time, execution_time),
                'max_time': max(existing.max_time, execution_time),
                'executions': existing.executions + 1,
            })
            # Trigger recompute for average
            existing._compute_average_time()
        else:
            Timing.create({
                'name': function_name,
                'min_time': execution_time,
                'max_time': execution_time,
                'total_time': execution_time,
                'executions': 1,
            })

    def _verify_api_key(self, token):
        """Check if the token belongs to a valid user"""
        return request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)

    @http.route('/api/start_work', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def start_work(self, **post):
        start_time = time.time()
        try:
            token = post.get('token')
            selfie_base64 = post.get('selfie')

            if not token:
                return {'success': False, 'message': 'Token is required', 'code': 403}
            if not selfie_base64:
                return {'success': False, 'message': 'Selfie is missing', 'code': 400}

            user = self._verify_api_key(token)
            if not user:
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

            return {
                'success': True,
                'message': 'Start selfie saved successfully',
                'session_id': session.id,
                'start_time_ist': ist_start_time,
                'code': 200
            }

        except Exception as e:
            return {'success': False, 'message': str(e), 'code': 500}
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('start_work', execution_time)

    @http.route('/api/end_work', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def end_work(self, **post):
        start_time = time.time()
        try:
            token = post.get('token')
            selfie_base64 = post.get('selfie')

            if not token:
                return {'success': False, 'message': 'Token is required', 'code': 403}
            if not selfie_base64:
                return {'success': False, 'message': 'Selfie is missing', 'code': 400}

            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            session = request.env['work.session'].sudo().search([
                ('user_id', '=', user.id),
                ('end_time', '=', False)
            ], order='start_time desc', limit=1)

            if not session:
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

            return {
                'success': True,
                'message': 'End selfie saved successfully',
                'session_id': session.id,
                'end_time_ist': ist_end_time,
                'code': 200
            }

        except Exception as e:
            return {'success': False, 'message': str(e), 'code': 500}
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('end_work', execution_time)

    @http.route('/api/user/today_selfies', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def get_today_selfies(self, **post):
        start_time = time.time()
        try:
            token = post.get('token')
            user_id = post.get('user_id')

            if not token or not user_id:
                return {'success': False, 'message': 'Token and User ID are required', 'code': 400}

            if not self._verify_api_key(token):
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
                start_time = session.start_time + timedelta(hours=5, minutes=30) if session.start_time else None
                end_time = session.end_time + timedelta(hours=5, minutes=30) if session.end_time else None

                selfie_sessions.append({
                    'session_id': session.id,
                    'start_time': str(start_time) if start_time else None,
                    'end_time': str(end_time) if end_time else None,
                    'start_selfie': f"data:image/png;base64,{session.start_selfie.decode('utf-8')}" if session.start_selfie else None,
                    'end_selfie': f"data:image/png;base64,{session.end_selfie.decode('utf-8')}" if session.end_selfie else None,
                })

            return {
                'success': True,
                'user_id': int(user_id),
                'date': str(today),
                'selfies': selfie_sessions,
                'code': 200
            }

        except Exception as e:
            return {'success': False, 'message': str(e), 'code': 500}
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('get_today_selfies', execution_time)

    @http.route('/api/all_pin_locations', type='json', auth='public', methods=['POST'], csrf=False)
    def get_all_pin_locations(self, **kwargs):
        start_time = time.time()
        try:
            token = kwargs.get('token')

            if not token:
                return {'success': False, 'message': 'Token is missing'}

            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token'}

            pins = request.env['pin.location'].sudo().search([])
            data = [{'id': p.id, 'name': p.name, 'code': p.code, 'location_name': p.location_name, 'phone':p.phone, 'unit_name':p.unit_name} for p in pins]

            return {'success': True, 'data': data}

        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('get_all_pin_locations', execution_time)

    @http.route('/api/Pin_location_asin', type='json', auth='public', methods=['POST'], csrf=False)
    def assign_pin_location(self, **kwargs):
        start_time = time.time()
        try:
            token = kwargs.get('token')
            user_id = kwargs.get('user_id')
            pin_location_id = kwargs.get('pin_lo_id')

            if not token or not user_id or not pin_location_id:
                return {'success': False, 'message': 'Missing token, user_id, or pin_lo_id'}

            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token'}

            target_user = request.env['res.users'].sudo().browse(int(user_id))
            pin_location = request.env['pin.location'].sudo().browse(int(pin_location_id))

            if not target_user.exists():
                return {'success': False, 'message': 'User not found'}
            if not pin_location.exists():
                return {'success': False, 'message': 'Pin location not found'}

            target_user.write({
                'pin_location_ids': [(4, pin_location.id)],
                'present_pin_id': pin_location.id,
            })

            return {
                'success': True,
                'message': f'Pin location {pin_location.location_name} assigned to user {target_user.name}'
            }

        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('assign_pin_location', execution_time)

    @http.route('/api/get_current_pin_location', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def get_current_pin_location_of_user(self, **kwargs):
        start_time = time.time()
        try:
            token = kwargs.get('token')

            if not token:
                return {'success': False, 'message': 'Token is required', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            pin = user.present_pin_id
            if not pin:
                return {'success': False, 'message': 'No current pin location assigned', 'code': 404}

            return {
                'success': True,
                'data': {
                    'id': pin.id,
                    'name': pin.name,
                    'location_name': pin.location_name,
                    'code': pin.code
                },
                'code': 200
            }

        except Exception as e:
            return {'success': False, 'message': str(e), 'code': 500}
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('get_current_pin_location_of_user', execution_time)

    @http.route('/api/create_pin_location', type='json', auth='public', methods=['POST'], csrf=False)
    def create_pin_location(self, **kwargs):
        start_time = time.time()
        try:
            # Token authentication
            token = kwargs.get('token')
            if not token:
                return {'success': False, 'message': 'Token is missing'}

            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token'}

            # Required fields
            required_fields = ['code', 'location_name', 'phone', 'unit_name']
            for field in required_fields:
                if not kwargs.get(field):
                    return {'success': False, 'message': f'Missing field: {field}'}

            # Create the record
            pin = request.env['pin.location'].sudo().create({
                'code': kwargs.get('code'),
                'location_name': kwargs.get('location_name'),
                'phone': kwargs.get('phone'),
                'unit_name': kwargs.get('unit_name'),
            })

            return {
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

        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('create_pin_location', execution_time)