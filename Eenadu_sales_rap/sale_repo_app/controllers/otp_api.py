from odoo import http
from odoo.http import request
from datetime import datetime
import random
import requests

class PhoneVerificationController(http.Controller):

    @http.route('/api/send_otp', type='json', auth='public', methods=['POST'], csrf=False)
    def send_otp(self, **kwargs):
        try:
            phone = kwargs.get('phone')
            if not phone:
                return {"success": False, "message": "Phone number is required"}

            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))

            # Custom Message
            msg = f"One Time Password for EENADU Sales Representative for Information Collection is {otp}. Please use this OTP to proceed. Regards EENADU."

            url = f"https://www.smsstriker.com/API/sms.php"
            payload = {
                'username': 'EERETA',
                'password': 'EERETA',
                'from': 'EERETA',
                'to': phone,
                'msg': msg,
                'type': '1',
                'template_id': '1407169114591748105',
            }

            response = requests.post(url, data=payload)

            # Log response
            _logger.info(f"SMS Response: {response.text}")

            # Save OTP
            request.env['phone.verification.otp'].sudo().create({
                'phone_number': phone,
                'otp_code': otp,
                'otp_time': datetime.now(),
            })

            return {"success": True, "message": "OTP sent successfully"}

        except Exception as e:
            return {"success": False, "message": str(e)}

    @http.route('/api/verify_otp', type='json', auth='public', methods=['POST'], csrf=False)
    def verify_otp(self, **kwargs):
        try:
            phone = kwargs.get('phone')
            otp = kwargs.get('otp')

            if not phone or not otp:
                return {"success": False, "message": "Phone and OTP are required"}

            # Search for latest OTP
            otp_record = request.env['phone.verification.otp'].sudo().search([
                ('phone_number', '=', phone),
                ('otp_code', '=', otp)
            ], order='otp_time desc', limit=1)

            if otp_record:
                return {"success": True, "message": "OTP verified successfully"}
            else:
                return {"success": False, "message": "Invalid OTP"}

        except Exception as e:
            return {"success": False, "message": str(e)}
