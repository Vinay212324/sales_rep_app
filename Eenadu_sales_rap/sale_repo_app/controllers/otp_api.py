# controllers/otp_api.py
from odoo import http
from odoo.http import request
import random
import requests

class OTPController(http.Controller):

    def generate_otp(self, length=6):
        return ''.join(random.choices('0123456789', k=length))
    def _verify_api_key(self, token):
        """Check if the token belongs to a valid user"""
        return request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)

    @http.route('/api/send_otp', type='json', auth='public', methods=['POST'], csrf=False)
    def send_otp(self, **kwargs):
        try:
            token = post.get('token')
            if not token:
                return {'success': False, 'message': 'Token is required', 'code': 403}
            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            phone = kwargs.get('phone')
            if not phone:
                return {"error": "Phone number is required"}

            otp = self.generate_otp()
            message = f"One Time Password for EENADU (sales representation) Online Booking to Update Mobile is {otp}. Please use this OTP to Update Mobile.Regards EENADU"

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

            # Send request
            response = requests.post(url, data=payload, timeout=10)

            # Log and save OTP to DB
            if response.status_code == 200:
                existing = request.env['phone.otp.verification'].sudo().search([('phone', '=', phone)])
                if existing:
                    existing.write({'otp': otp, 'is_verified': False})
                else:
                    request.env['phone.otp.verification'].sudo().create({
                        'phone': phone,
                        'otp': otp,
                        'is_verified': False,
                    })
                return {"success": "OTP sent successfully", "otp": otp}  # remove otp in production
            else:
                return {"error": f"Failed to send OTP. Status: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    @http.route('/api/verify_otp', type='json', auth='public', methods=['POST'], csrf=False)
    def verify_otp(self, **kwargs):
        try:
            token = post.get('token')
            if not token:
                return {'success': False, 'message': 'Token is required', 'code': 403}
            user = self._verify_api_key(token)
            if not user:
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
            phone = kwargs.get('phone')
            otp = kwargs.get('otp')

            if not phone or not otp:
                return {"error": "Phone number and OTP are required"}

            record = request.env['phone.otp.verification'].sudo().search([('phone', '=', phone)], limit=1)

            if not record:
                return {"error": "Phone number not found"}

            if record.otp == otp:
                record.write({'is_verified': True})
                return {"success": "Phone number verified successfully"}
            else:
                return {"error": "Invalid OTP"}

        except Exception as e:
            return {"error": str(e)}
