# controllers/otp_api.py

from odoo import http
from odoo.http import request
import random
import requests
import urllib.parse
import logging

_logger = logging.getLogger(__name__)

class OTPController(http.Controller):

    def generate_otp(self, length=6):
        return ''.join(random.choices('0123456789', k=length))

    def _verify_api_key(self, token):
        """Check if the token belongs to a valid user."""
        return request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)

    @http.route('/api/send_otp', type='json', auth='public', methods=['POST'], csrf=False)
    def send_otp(self, **kwargs):
        try:
            token = kwargs.get('token')
            if not token:
                return {'success': False, 'message': 'Token is required', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            phone = kwargs.get('phone')
            if not phone:
                return {'success': False, 'message': 'Phone number is required', 'code': 400}

            # Generate OTP
            otp = self.generate_otp()

            # Construct message
            message = (
                f"One Time Password for EENADU (sales representation) Online Booking to Update "
                f"Mobile is {otp}. Please use this OTP to Update Mobile. Regards EENADU"
            )

            payload = {
                'username': 'EERETA',
                'password': 'EERETA',
                'from': 'EERETA',
                'to': phone,
                'msg': message,
                'type': '1',
                'template_id': '1407169114591748105'
            }

            url = 'https://www.smsstriker.com/API/sms.php'
            encoded_payload = urllib.parse.urlencode(payload)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            response = requests.post(url, data=encoded_payload, headers=headers, timeout=10)

            _logger.info(f"SMS API response: {response.status_code} - {response.text}")

            # Save OTP to DB if SMS was sent
            if response.status_code == 200 and any(x in response.text.lower() for x in ['success', 'sent', 'ok']):
                otp_model = request.env['phone.otp.verification'].sudo()
                record = otp_model.search([('phone', '=', phone)], limit=1)
                if record:
                    record.write({'otp': otp, 'is_verified': False})
                else:
                    otp_model.create({'phone': phone, 'otp': otp, 'is_verified': False})

                return {
                    'success': True,
                    'message': 'OTP sent successfully',
                    'code': 200,
                    # 'otp': otp  # Optional: For testing only. Remove in production.
                }

            return {
                'success': False,
                'message': f"Failed to send OTP. SMS API response: {response.text}",
                'code': response.status_code
            }

        except Exception as e:
            _logger.exception("Error in send_otp")
            return {'success': False, 'message': str(e), 'code': 500}

    @http.route('/api/verify_otp', type='json', auth='public', methods=['POST'], csrf=False)
    def verify_otp(self, **kwargs):
        try:
            token = kwargs.get('token')
            if not token:
                return {'success': False, 'message': 'Token is required', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            phone = kwargs.get('phone')
            otp = kwargs.get('otp')

            if not phone or not otp:
                return {'success': False, 'message': 'Phone number and OTP are required', 'code': 400}

            record = request.env['phone.otp.verification'].sudo().search([('phone', '=', phone)], limit=1)

            if not record:
                return {'success': False, 'message': 'Phone number not found', 'code': 404}

            if record.otp == otp:
                record.write({'is_verified': True})
                return {'success': True, 'message': 'Phone number verified successfully', 'code': 200}
            else:
                return {'success': False, 'message': 'Invalid OTP', 'code': 401}

        except Exception as e:
            _logger.exception("Error in verify_otp")
            return {'success': False, 'message': str(e), 'code': 500}
