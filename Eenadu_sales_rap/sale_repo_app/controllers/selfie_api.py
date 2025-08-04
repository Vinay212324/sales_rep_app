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
        return request.env['res.users'].sudo().search([('api_key', '=', token)], limit=1)

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

            # Filter sessions by today's date
            today = date.today()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())

            sessions = request.env['work.session'].sudo().search([
                ('user_id', '=', int(user_id)),
                ('start_time', '>=', start_of_day),
                ('start_time', '<=', end_of_day)
            ])

            selfie_sessions = []
            for session in sessions:
                selfie_sessions.append({
                    'session_id': session.id,
                    'start_time': session.start_time,
                    'end_time': session.end_time,
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
