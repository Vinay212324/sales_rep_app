from odoo import http, fields
from odoo.http import request
import base64
import werkzeug


class SelfieController(http.Controller):

    def _verify_api_key(self, token):
        """Check if the token belongs to a valid user"""
        user = request.env['res.users'].sudo().search([('api_key', '=', token)], limit=1)
        return user if user else None

    @http.route('/api/start_work', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def start_work(self, **post):
        print("vinay")
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

            # Save work session
            session = request.env['work.session'].sudo().create({
                'user_id': user.id,
                'start_time': fields.Datetime.now(),
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

            # Find latest work session for user
            session = request.env['work.session'].sudo().search([
                ('user_id', '=', user.id),
                ('end_time', '=', False)
            ], order="start_time desc", limit=1)

            if not session:
                return {'success': False, 'message': 'No active session found', 'code': 404}

            session.write({
                'end_time': fields.Datetime.now(),
                'end_selfie': selfie_base64.encode('utf-8'),
            })

            return {
                'success': True,
                'message': 'End selfie saved successfully',
                'session_id': session.id,
                'code': 200
            }

        except Exception as e:
            return {'success': False, 'message': str(e), 'code': 500}
