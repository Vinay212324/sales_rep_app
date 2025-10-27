from odoo import http
from odoo.http import request
import random
import requests
import logging
from datetime import date
from datetime import datetime, timedelta, time
#from apscheduler.schedulers.background import BackgroundScheduler
from odoo.http import request
import time

_logger = logging.getLogger(__name__)

class OtpAPI(http.Controller):

    def _verify_api_key(self, token):
        start_time = time.time()
        try:
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            duration = time.time() - start_time
            if user:
                _logger.info(f"_verify_api_key completed successfully in {duration:.4f} seconds for user: {user.login}")
            else:
                _logger.info(f"_verify_api_key completed in {duration:.4f} seconds with no user found for token.")
            return user
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"_verify_api_key failed in {duration:.4f} seconds with error: {str(e)}")
            return False

    @http.route('/api/send_otp', auth='public', methods=['POST'], type='json', csrf=False)
    def send_otp(self, **post):
        start_time = time.time()
        try:
            token = post.get('token')
            if not token:
                duration = time.time() - start_time
                _logger.info(f"send_otp completed in {duration:.4f} seconds with error: Token is required")
                return {'success': False, 'message': 'Token is required', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"send_otp completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            phone = post.get('phone')
            if not phone:
                duration = time.time() - start_time
                _logger.info(f"send_otp completed in {duration:.4f} seconds with error: Phone number is required")
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

            response = requests.post(url, data=payload)
            _logger.info(f"response.text: {response.text}, response.status_code: {response.status_code}")
            if not(response.status_code):
                _logger.error(f"SMS sending failed: {response.text}")
                duration = time.time() - start_time
                _logger.error(f"send_otp failed in {duration:.4f} seconds: Failed to send OTP")
                return {'status': 'error', 'message': 'Failed to send OTP'}

            # Store OTP
            request.env['verification.otp'].sudo().create({
                'phone_number': phone,
                'otp_code': otp,
            })

            result = {'status': 'success', 'message': 'OTP sent successfully'}
            duration = time.time() - start_time
            _logger.info(f"send_otp completed successfully in {duration:.4f} seconds for phone: {phone}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            _logger.exception(f"send_otp failed in {duration:.4f} seconds: Error sending OTP - {str(e)}")
            _logger.exception("Error sending OTP")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/verify_otp', auth='public', methods=['POST'], type='json', csrf=False)
    def verify_otp(self, **post):
        start_time = time.time()
        try:
            token = post.get('token')
            if not token:
                duration = time.time() - start_time
                _logger.info(f"verify_otp completed in {duration:.4f} seconds with error: Token is required")
                return {'success': False, 'message': 'Token is required', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"verify_otp completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}

            phone = post.get('phone')
            otp = post.get('otp')

            if not phone or not otp:
                duration = time.time() - start_time
                _logger.info(f"verify_otp completed in {duration:.4f} seconds with error: Phone and OTP are required")
                return {'status': 'error', 'message': 'Phone and OTP are required'}

            record = request.env['verification.otp'].sudo().search([
                ('phone_number', '=', phone),
                ('otp_code', '=', otp),
                ('is_verified', '=', False)
            ], limit=1)

            if record:
                record.sudo().write({'is_verified': True})
                result = {'status': 'success', 'message': 'OTP verified'}
                duration = time.time() - start_time
                _logger.info(f"verify_otp completed successfully in {duration:.4f} seconds for phone: {phone}")
                return result
            else:
                duration = time.time() - start_time
                _logger.info(f"verify_otp completed in {duration:.4f} seconds with error: Invalid OTP")
                return {'status': 'error', 'message': 'Invalid OTP'}
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"verify_otp failed in {duration:.4f} seconds with error: {str(e)}")
            return {'status': 'error', 'message': str(e)}







    @http.route('/api/send_url_message', auth='public', methods=['POST'], type='json', csrf=False)
    def send_mes(self, **post):
        start_time = time.time()
        try:
            _logger.info("ppppppppp")
            token = post.get('token')
            if not token:
                duration = time.time() - start_time
                _logger.info(f"send_mes completed in {duration:.4f} seconds with error: Token is required")
                return {'success': False, 'message': 'Token is required', 'code': 403}

            user = self._verify_api_key(token)
            if not user:
                duration = time.time() - start_time
                _logger.info(f"send_mes completed in {duration:.4f} seconds with error: Invalid or expired token")
                return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
            unit_name = user.unit_name
            _logger.info(f"unit_name: {unit_name}")

            message_history = request.env['message.history'].create({
                'unit_name': unit_name,
                'date': date.today()
            })
            _logger.info(f"message_history.id: {message_history.id}")
            message_history.sudo().generate_token()
            total_agencies = request.env['pin.location'].sudo().search([('unit_name','=',unit_name)])
            total_agencies_filled_custon_forms_today = []
            for i in total_agencies:
                _logger.info(f"agency: {i}")
                count = request.env['customer.form'].sudo().search_count([('unit_name', '=', unit_name),('date','=',date.today()),('Agency','=',i.location_name)])
                if count>=1:
                    total_agencies_filled_custon_forms_today.append([i.location_name, i.phone])

            great = "happy"
            unit_number = "8885554879"
            head_office_number = "8885554879"
            for_main_mes = [unit_number,head_office_number]
            try:
                res = {}
                for i in for_main_mes:

                    _logger.info(f"message_history.unic_code: {message_history.unic_code}")
                    link = f"salesrep.esanchaya.com/daily-data/{date.today()}/{message_history.unic_code}"
                    _logger.info(f"link length: {len(link)}")
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
                    _logger.info(f"agencies: {agencies}")

                    response = requests.post(url, data=payload)

                    _logger.info(f"response.text: {response.text}, response.status_code: {response.status_code}")
                    if not (response.status_code):
                        _logger.error(f"SMS sending failed: {response.text}")
                        res[str(i)]= {'status': 'error', 'message': 'Failed to send OTP'}

                    res[str(i)]=  {'status': 'success', 'message': 'OTP sent successfully'}


                for i in total_agencies_filled_custon_forms_today:
                    unit_name = user.unit_name
                    _logger.info(f"unit_name: {unit_name}")

                    message_history = request.env['message.history'].create({
                        'unit_name': unit_name,
                        'date': date.today(),
                        'agency':i[0]
                    })
                    _logger.info(f"message_history.id: {message_history.id}")
                    message_history.sudo().generate_token()

                    link = f"salesrep.esanchaya.com/daily-data/{message_history.unic_code}"
                    msg = (
                        f"Hi,We are sharing the circulation subscribers details please click on the link {link} EENADU-CIRCULATION"
                    )
                    url = "https://www.smsstriker.com/API/sms.php"
                    _logger.info(f"agency details: {i}")
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
                    _logger.info(f"agencies: {agencies}")

                    response = requests.post(url, data=payload)

                    _logger.info(f"response.text: {response.text}, response.status_code: {response.status_code}")
                    if not (response.status_code):
                        _logger.error(f"SMS sending failed: {response.text}")
                        res[str(i)] = {'status': 'error', 'message': 'Failed to send OTP'}

                    res[str(i)] = {'status': 'success', 'message': 'OTP sent successfully'}
                else:
                    duration = time.time() - start_time
                    _logger.info(f"send_mes completed successfully in {duration:.4f} seconds")
                    return res
                _logger.info("SMS Response: %s %s", response.status_code, response.text)
            except Exception as inner_e:
                duration = time.time() - start_time
                _logger.exception(f"send_mes failed in {duration:.4f} seconds: Error sending OTP - {str(inner_e)}")
                _logger.exception("Error sending OTP")
                return {'status': 'error', 'message': str(inner_e)}
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"send_mes failed in {duration:.4f} seconds with error: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    # def check_and_run_on_restart(self):
    #     now = datetime.now()
    #     scheduled = time(19,0)
    #     if now.time()>scheduled:
    #         send_mes()
    #
    # if __name__ == "__main__":
    #     check_and_run_on_restart()
    #     t.sleep(60)