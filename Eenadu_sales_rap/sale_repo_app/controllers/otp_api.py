# from odoo import http
# from odoo.http import request
# import random
# import requests
# from datetime import datetime
# import logging
#
# _logger = logging.getLogger(__name__)
#
# class OtpAPI(http.Controller):
#
#     def _verify_api_key(self, token):
#         """Check if the token belongs to a valid user"""
#         return request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
#
#     @http.route('/api/send_otp', auth='public', methods=['POST'], type='json', csrf=False)
#     def send_otp(self, **post):
#         try:
#             token = post.get('token')
#             phone = post.get('phone')
#
#             if not token:
#                 return {'success': False, 'message': 'Token is required', 'code': 403}
#             if not phone:
#                 return {'success': False, 'message': 'Phone number is required', 'code': 400}
#
#             user = self._verify_api_key(token)
#             if not user:
#                 return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
#
#             otp = str(random.randint(100000, 999999))
#             msg = f"EENADU Sales Representative Information Collection OTP is {otp}. Please do not share with anyone. Regards, EENADU."
#
#             url = "https://www.smsstriker.com/API/sms.php"
#             payload = {
#                 'username': 'EERETA',
#                 'password': 'EERETA',
#                 'from': 'EERETA',
#                 'to': phone,
#                 'msg': msg,
#                 'type': '1',
#                 'template_id': '1407169114591748105'
#             }
#
#             response = requests.post(url, data=payload, timeout=10)
#             _logger.info(f"SMS API response: {response.status_code} - {response.text}")
#
#             if response.status_code != 200 or 'Invalid' in response.text:
#                 return {'success': False, 'message': 'Failed to send OTP', 'code': 500}
#
#             # Save OTP in DB
#             otp_model = request.env['phone.verification.otp'].sudo()
#             existing = otp_model.search([('phone_number', '=', phone)], limit=1)
#
#             if existing:
#                 existing.write({
#                     'otp_code': otp,
#                     'is_verified': False,
#                     'otp_time': datetime.now()
#                 })
#             else:
#                 otp_model.create({
#                     'phone_number': phone,
#                     'otp_code': otp,
#                     'is_verified': False,
#                     'otp_time': datetime.now()
#                 })
#
#             return {'success': True, 'message': 'OTP sent successfully', 'code': 200}
#
#         except requests.exceptions.RequestException as e:
#             _logger.exception("SMS API request failed")
#             return {'success': False, 'message': f'SMS API Error: {str(e)}', 'code': 502}
#         except Exception as e:
#             _logger.exception("Unexpected error in send_otp")
#             return {'success': False, 'message': str(e), 'code': 500}
#
#     @http.route('/api/verify_otp', auth='public', methods=['POST'], type='json', csrf=False)
#     def verify_otp(self, **post):
#         try:
#             token = post.get('token')
#             phone = post.get('phone')
#             otp = post.get('otp')
#
#             if not token:
#                 return {'success': False, 'message': 'Token is required', 'code': 403}
#             if not phone or not otp:
#                 return {'success': False, 'message': 'Phone and OTP are required', 'code': 400}
#
#             user = self._verify_api_key(token)
#             if not user:
#                 return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
#
#             record = request.env['phone.verification.otp'].sudo().search([
#                 ('phone_number', '=', phone),
#                 ('otp_code', '=', otp),
#                 ('is_verified', '=', False)
#             ], limit=1)
#
#             if record:
#                 record.write({'is_verified': True})
#                 return {'success': True, 'message': 'OTP verified successfully', 'code': 200}
#             else:
#                 return {'success': False, 'message': 'Invalid OTP or already verified', 'code': 401}
#
#         except Exception as e:
#             _logger.exception("Unexpected error in verify_otp")
#             return {'success': False, 'message': str(e), 'code': 500}
#





from odoo import http
from odoo.http import request
import random
import requests
import logging

_logger = logging.getLogger(__name__)

class OtpAPI(http.Controller):

    def _verify_api_key(self, token):
        """Check if the token belongs to a valid user"""
        return request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)

    @http.route('/api/send_otp', auth='public', methods=['POST'], type='json', csrf=False)
    def send_otp(self, **post):
        token = post.get('token')

        if not token:
            return {'success': False, 'message': 'Token is required', 'code': 403}
        user = self._verify_api_key(token)
        if not user:
            return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
        phone = post.get('phone')
        if not phone:
            return {'status': 'error', 'message': 'Phone number is required'}

        otp = str(random.randint(100000, 999999))
        msg = f"One Time Password for EENADU (Advertisements) Online Booking to Update Mobile is {otp}. Please use this OTP to Update Mobile. Regards EENADU"

        url = "https://www.smsstriker.com/API/sms.php"
        payload = {
            'username': 'EERETA',
            'password': 'EERETA',
            'from': 'EERETA',
            'to': phone,
            'msg': msg,
            'type': '1',
            'template_id': '1407169114591748105'
        }

        try:
            response = requests.post(url, data=payload)
            if "Invalid" in response.text or response.status_code != 200:
                _logger.error(f"SMS sending failed: {response.text}")
                return {'status': 'error', 'message': 'Failed to send OTP'}

            request.env['phone.verification.otp'].sudo().create({
                'phone': phone,
                'otp': otp,
            })

            return {'status': 'success', 'message': 'OTP sent successfully'}
        except Exception as e:
            _logger.exception("Error sending OTP")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/verify_otp', auth='public', methods=['POST'], type='json', csrf=False)
    def verify_otp(self, **post):

        token = post.get('token')
        phone = post.get('phone')

        if not token:
            return {'success': False, 'message': 'Token is required', 'code': 403}
        user = self._verify_api_key(token)
        if not user:
            return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
        phone = post.get('phone')
        otp = post.get('otp')

        if not phone or not otp:
            return {'status': 'error', 'message': 'Phone and OTP are required'}

        record = request.env['otp.verification'].sudo().search([
            ('phone', '=', phone),
            ('otp', '=', otp),
            ('is_verified', '=', False)
        ], limit=1)

        if record:
            record.sudo().write({'phone.verification.otp': True})
            return {'status': 'success', 'message': 'OTP verified'}
        else:
            return {'status': 'error', 'message': 'Invalid OTP'}
