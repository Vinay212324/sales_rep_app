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
        msg = "One Time Password for EENADU (Advertisements) Online Booking to Update Mobile is " + str(otp) + ". Please use this OTP to Update Mobile.Regards EENADU"

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
            print(response.text, response.status_code )
            if not(response.status_code) :
                _logger.error(f"SMS sending failed: {response.text}")
                return {'status': 'error', 'message': 'Failed to send OTP'}

            # Store OTP
            request.env['verification.otp'].sudo().create({
                'phone_number': phone,
                'otp_code': otp,
            })

            return {'status': 'success', 'message': 'OTP sent successfully'}
        except Exception as e:
            _logger.exception("Error sending OTP")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/verify_otp', auth='public', methods=['POST'], type='json', csrf=False)
    def verify_otp(self, **post):
        token = post.get('token')
        if not token:
            return {'success': False, 'message': 'Token is required', 'code': 403}

        user = self._verify_api_key(token)
        if not user:
            return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

        phone = post.get('phone')
        otp = post.get('otp')

        if not phone or not otp:
            return {'status': 'error', 'message': 'Phone and OTP are required'}

        record = request.env['verification.otp'].sudo().search([
            ('phone_number', '=', phone),
            ('otp_code', '=', otp),
            ('is_verified', '=', False)
        ], limit=1)

        if record:
            record.sudo().write({'is_verified': True})
            return {'status': 'success', 'message': 'OTP verified'}
        else:
            return {'status': 'error', 'message': 'Invalid OTP'}
