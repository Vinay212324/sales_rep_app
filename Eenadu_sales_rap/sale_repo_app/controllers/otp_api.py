from odoo import http
from odoo.http import request
import random
import requests
import logging

_logger = logging.getLogger(__name__)

class OtpAPI(http.Controller):

    @http.route('/api/send_otp', auth='public', methods=['POST'], type='json', csrf=False)
    def send_otp(self, **post):
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

            request.env['otp.verification'].sudo().create({
                'phone': phone,
                'otp': otp,
            })

            return {'status': 'success', 'message': 'OTP sent successfully'}
        except Exception as e:
            _logger.exception("Error sending OTP")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/verify_otp', auth='public', methods=['POST'], type='json', csrf=False)
    def verify_otp(self, **post):
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
            record.sudo().write({'is_verified': True})
            return {'status': 'success', 'message': 'OTP verified'}
        else:
            return {'status': 'error', 'message': 'Invalid OTP'}
