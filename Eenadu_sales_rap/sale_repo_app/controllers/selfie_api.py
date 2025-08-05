from odoo import http, fields
from odoo.http import request
from datetime import datetime, date, time
import pytz

class SelfieController(http.Controller):

    def _verify_api_key(self, token):
        """Check if the token belongs to a valid user"""
        return request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)

    @http.route('/api/start_work', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def start_work(self, **post):
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

            ist_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)

            session = request.env['work.session'].sudo().create({
                'user_id': user.id,
                'start_time': ist_now,
                'start_selfie': selfie_base64.encode('utf-8'),
            })

            return {
                'success': True,
                'message': 'Start selfie saved successfully',
                'session_id': session.id,
                'code': 200
            }

        except Exception as e:
            return {'success': False, 'message': str(e), 'code': 500}

    @http.route('/api/end_work', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def end_work(self, **post):
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

            ist_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)

            session.write({
                'end_time': ist_now,
                'end_selfie': selfie_base64.encode('utf-8')
            })

            return {
                'success': True,
                'message': 'End selfie saved successfully',
                'session_id': session.id,
                'code': 200
            }

        except Exception as e:
            return {'success': False, 'message': str(e), 'code': 500}

    @http.route('/api/user/today_selfies', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def get_today_selfies(self, **post):
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
                ('start_time', '>=', start_of_day),
                ('start_time', '<=', end_of_day),
            ])

            selfie_sessions = []
            for session in sessions:
                selfie_sessions.append({
                    'session_id': session.id,
                    'start_time': str(session.start_time),
                    'end_time': str(session.end_time) if session.end_time else None,
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

    @http.route('/api/all_pin_locations', type='json', auth='public', methods=['POST'], csrf=False)
    def get_all_pin_locations(self, **kwargs):
        try:
            token = kwargs.get('token')

            if not token:
                return {'success': False, 'message': 'Token is missing'}

            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token'}

            pins = request.env['pin.location'].sudo().search([])
            data = [{'id': p.id, 'name': p.name, 'code': p.code, 'location_name': p.location_name} for p in pins]

            return {'success': True, 'data': data}

        except Exception as e:
            return {'success': False, 'message': str(e)}

    @http.route('/api/Pin_location_asin', type='json', auth='public', methods=['POST'], csrf=False)
    def assign_pin_location(self, **kwargs):
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

    @http.route('/api/get_current_pin_location', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def get_current_pin_location_of_user(self, **kwargs):
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
