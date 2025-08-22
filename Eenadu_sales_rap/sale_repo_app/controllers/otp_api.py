from odoo import http
from odoo.http import request
import random
import requests
import logging
from datetime import date
from datetime import datetime, timedelta
from odoo.http import request
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
        ot = ""
        otp = str(random.randint(100000, 999999))
        msg = (
            f"One Time Password for EENADU (Circulation) Online Booking is {ot} {otp} "
            f"Please use this OTP to confirm online booking. EENADU-CIRCULATION"
        )
        url = "https://www.smsstriker.com/API/sms.php"
        payload = {
            'username': 'EERETA',
            'password': 'EERETA',
            'from': 'EERETA',
            'to': phone,
            'msg': msg,
            'type': '1',
            'template_id': '1407175507692048299'
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







    @http.route('/api/send_url_message', auth='public', methods=['POST'], type='json', csrf=False)
    def send_mes(self, **post):
        print("ppppppppp")
        token = post.get('token')
        if not token:
            return {'success': False, 'message': 'Token is required', 'code': 403}

        user = self._verify_api_key(token)
        if not user:
            return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
        unit_name = user.unit_name
        print(unit_name)

        message_history = request.env['message.history'].create({
            'unit_name': unit_name,
            'date': date.today()
        })
        print("regreger",message_history.id)
        message_history.sudo().generate_token()
        total_agencies = request.env['pin.location'].sudo().search([('unit_name','=',unit_name)])
        total_agencies_filled_custon_forms_today = []
        for i in total_agencies:
            print(i,"vinay")
            count = request.env['customer.form'].sudo().search_count([('unit_name', '=', unit_name),('date','=',date.today()),('Agency','=',i.location_name)])
            if count>=1:
                total_agencies_filled_custon_forms_today.append([i.location_name, i.phone])

        great = "happy"
        unit_number = "9642421753"
        head_office_number = "9642421753"
        for_main_mes = [unit_number,head_office_number]
        try:
            res = {}
            for i in for_main_mes:

                print(message_history.unic_code,"      hoooooo0")
                link = f"salesrep.esanchaya.com/daily-data/{date.today()}/{message_history.unic_code}"
                print(len(link))
                msg = (
                    f"Hi,We are sharing the circulation subscribers details please click on the link {link} EENADU-CIRCULATION"
                )
                url = "https://www.smsstriker.com/API/sms.php"

                payload = {
                    'username': 'EERETA',
                    'password': 'EERETA',
                    'from': 'EERETA',
                    'to': i,
                    'msg': msg,
                    'type': '1',
                    'template_id': '1407175507724602621'
                }

                agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])
                print(agencies,"vinnnnn")

                response = requests.post(url, data=payload)

                print(response.text, response.status_code)
                if not (response.status_code):
                    _logger.error(f"SMS sending failed: {response.text}")
                    res[str(i)]= {'status': 'error', 'message': 'Failed to send OTP'}

                res[str(i)]=  {'status': 'success', 'message': 'OTP sent successfully'}


            for i in total_agencies_filled_custon_forms_today:
                unit_name = user.unit_name
                print(unit_name)

                message_history = request.env['message.history'].create({
                    'unit_name': unit_name,
                    'date': date.today(),
                    'agency':i[0]
                })
                print("regreger", message_history.id)
                message_history.sudo().generate_token()

                link = f"salesrep.esanchaya.com/daily-data/{message_history.unic_code}"
                msg = (
                    f"Hi,We are sharing the circulation subscribers details please click on the link {link} EENADU-CIRCULATION"
                )
                url = "https://www.smsstriker.com/API/sms.php"
                print(i)
                payload = {
                    'username': 'EERETA',
                    'password': 'EERETA',
                    'from': 'EERETA',
                    'to': i[1],
                    'msg': msg,
                    'type': '1',
                    'template_id': '1407175507724602621'
                }

                agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])
                print(agencies, "vinnnnn")

                response = requests.post(url, data=payload)

                print(response.text, response.status_code)
                if not (response.status_code):
                    _logger.error(f"SMS sending failed: {response.text}")
                    res[str(i)] = {'status': 'error', 'message': 'Failed to send OTP'}

                res[str(i)] = {'status': 'success', 'message': 'OTP sent successfully'}
            else:
                return res

        except Exception as e:
            _logger.exception("Error sending OTP")
            return {'status': 'error', 'message': str(e)}


