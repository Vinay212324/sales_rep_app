from odoo import http, fields
from odoo.http import request
import base64
import werkzeug
from odoo import http, fields
from odoo.http import request
from datetime import datetime, date
from datetime import datetime
import pytz



class SelfieController(http.Controller):

    def _verify_api_key(self, token):
        """Check if the token belongs to a valid user"""
        user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        return user if user else None

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

            # Convert to IST time
            utc_now = datetime.utcnow()
            ist_tz = pytz.timezone('Asia/Kolkata')
            ist_now = pytz.utc.localize(utc_now).astimezone(ist_tz)

            # Save work session
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

            # Find the latest open session for the user
            session = request.env['work.session'].sudo().search([
                ('user_id', '=', user.id),
                ('end_time', '=', False)
            ], order='start_time desc', limit=1)

            if not session:
                return {'success': False, 'message': 'No active session found', 'code': 404}

            # Convert UTC now to IST
            utc_now = datetime.utcnow()
            ist_tz = pytz.timezone('Asia/Kolkata')
            ist_now = pytz.utc.localize(utc_now).astimezone(ist_tz)

            # Update the session
            session.write({
                'end_time': ist_now,
                'end_selfie': selfie_base64  # Do not encode again if already base64
            })

            return {
                'success': True,
                'message': 'End selfie saved successfully',
                'session_id': session.id,
                'code': 200
            }

        except Exception as e:
            return {'success': False, 'message': str(e), 'code': 500}

    # @http.route('/api/user/selfies', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    # def get_user_selfies(self, **post):
    #     try:
    #         token = post.get('token')
    #         if not token:
    #             return {'success': False, 'message': 'Token is required', 'code': 403}
    #
    #         user = self._verify_api_key(token)
    #         if not user:
    #             return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
    #
    #         sessions = request.env['work.session'].sudo().search([
    #             ('user_id', '=', user.id)
    #         ], order='start_time desc')
    #
    #         session_list = []
    #         for session in sessions:
    #             session_list.append({
    #                 'session_id': session.id,
    #                 'start_time': session.start_time,
    #                 'end_time': session.end_time,
    #                 'start_selfie': f"data:image/png;base64,{session.start_selfie.decode('utf-8')}" if session.start_selfie else None,
    #                 'end_selfie': f"data:image/png;base64,{session.end_selfie.decode('utf-8')}" if session.end_selfie else None,
    #             })
    #
    #         return {
    #             'success': True,
    #             'user_id': user.id,
    #             'user_name': user.name,
    #             'sessions': session_list,
    #             'code': 200
    #         }
    #
    #     except Exception as e:
    #         return {
    #             'success': False,
    #             'message': str(e),
    #             'code': 500
    #         }

    def _verify_api_key(self, token):
        """Validates token and returns the user"""
        return request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)

    @http.route('/api/user/today_selfies', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def get_today_selfies(self, **post):
        try:
            token = post.get('token')
            user_id = post.get('user_id')

            if not token:
                return {'success': False, 'message': 'Token is required', 'code': 403}
            if not user_id:
                return {'success': False, 'message': 'User ID is required', 'code': 400}

            requesting_user = self._verify_api_key(token)
            if not requesting_user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            # Get IST timezone-aware datetime for today
            ist = pytz.timezone("Asia/Kolkata")
            today = datetime.now(ist).date()
            start_of_day = ist.localize(datetime.combine(today, time.min))
            end_of_day = ist.localize(datetime.combine(today, time.max))

            # Get user's sessions today
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
        ensure_db()
        token = kwargs.get('token')

        if not token:
            return {'error': 'Token is missing'}

        # Validate token
        user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        if not user or not user.token_expiry or user.token_expiry < fields.Datetime.now():
            return {'error': 'Invalid or expired token'}

        # Fetch all pin location records
        pin_locations = request.env['pin.location'].sudo().search([])

        data = []
        for loc in pin_locations:
            data.append({
                'id': loc.id,
                'name': loc.name,
                'code': loc.code,
                'location_name': loc.location_name,
            })

        return {'success': True, 'data': data}

    @http.route('/api/Pin_location_asin', type='json', auth='public', methods=['POST'], csrf=False)
    def Pin_location_asin(self, **kwargs):
        token = kwargs.get('token')
        user_id = kwargs.get('user_id')
        pin_location_id = kwargs.get('pin_lo_id')

        # Validate inputs
        if not token or not user_id or not pin_location_id:
            return {'error': 'Missing token, user_id, or pin_lo_id'}

        # Validate token
        auth_user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        if not auth_user or not auth_user.token_expiry or auth_user.token_expiry < fields.Datetime.now():
            return {'error': 'Invalid or expired token'}

        # Fetch the user and pin location
        user = request.env['res.users'].sudo().browse(int(user_id))
        pin_location = request.env['pin.location'].sudo().browse(int(pin_location_id))

        if not user.exists():
            return {'error': f'User with ID {user_id} not found'}

        if not pin_location.exists():
            return {'error': f'Pin location with ID {pin_location_id} not found'}

        # Assign the pin location
        user.write({
            'pin_location_ids': [(4, pin_location.id)],
            'present_pin_id': pin_location.id,
        })

        return {
            'success': True,
            'message': f'Pin location {pin_location.location_name} assigned to user {user.name}'
        }

    @http.route('/api/get_current_pin_location', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def get_current_pin_location(self, **kwargs):
        token = kwargs.get('token')

        if not token:
            return {'success': False, 'message': 'Token is required', 'code': 403}

        # Authenticate user
        user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        if not user or not user.token_expiry or user.token_expiry < fields.Datetime.now():
            return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

        pin = user.present_pin_id

        if not pin:
            return {'success': False, 'message': 'No current pin location assigned', 'code': 404}

        # Return pin location info
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


