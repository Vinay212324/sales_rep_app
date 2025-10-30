from odoo import models, fields, api, _
from datetime import date
import requests
import logging
import time
import string
import secrets
from odoo import models, fields
from odoo.http import request
from odoo import http
from odoo.http import request
import random
import requests
import logging
from datetime import date
from odoo import models, fields,api,_
import requests
import logging
from datetime import date
import time

_logger = logging.getLogger(__name__)


class PhoneVerificationOTP(models.Model):
    _name = 'verification.otp'
    _description = 'OTP for phone verification'

    phone_number = fields.Char(string="Phone Number", required=True)
    otp_code = fields.Char(string="OTP")
    is_verified = fields.Boolean(string="Is Verified", default=False)
    otp_time = fields.Datetime(string="OTP Sent Time", default=fields.Datetime.now)

    def _update_function_timing(self, function_name, execution_time):
        """
        Helper method to update or create timing record for a function.
        """
        if execution_time < 0:
            return  # Skip invalid times

        Timing = self.env['function.timing'].sudo()
        existing = Timing.search([('name', '=', function_name)], limit=1)
        if existing:
            existing.write({
                'total_time': existing.total_time + execution_time,
                'min_time': min(existing.min_time, execution_time),
                'max_time': max(existing.max_time, execution_time),
                'executions': existing.executions + 1,
            })
            # Trigger recompute for average
            existing._compute_average_time()
        else:
            Timing.create({
                'name': function_name,
                'min_time': execution_time,
                'max_time': execution_time,
                'total_time': execution_time,
                'executions': 1,
            })

    @api.model
    def send_message_sales_rep(self):
        start_time = time.time()
        try:
            print("yyyyyyyyyyy")
            today = date.today()
            all_unit_names = request.env['res.users'].sudo().search([("role","=","circulation_incharge")])
            unit_set = []
            for res in all_unit_names:
                unit_set.append(res.unit_name)
            unit_set = set(unit_set)

            for res in unit_set:
                print(res)
                unit_name = res

                count = request.env['customer.form'].sudo().search_count(
                    [('unit_name', '=', unit_name), ('date', '=', date.today())])
                print(count)
                if count==0:
                    continue

                message_history = request.env['message.history'].create({
                    'unit_name': unit_name,
                    'date': today
                })
                message_history.sudo().generate_token()
                total_agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])
                total_agencies_filled_custon_forms_today = []
                print("hooo")
                for i in total_agencies:
                    agency_count = request.env['customer.form'].sudo().search_count(
                        [('unit_name', '=', unit_name), ('date', '=', today), ('Agency', '=', i.location_name)])
                    if agency_count >= 1:
                        print(agency_count, "vinay21vinnn")
                        total_agencies_filled_custon_forms_today.append([i.location_name, i.phone])


                great = "happy"
                head_office_number = "9642421753"  # FIXED: Moved definition before .get() to avoid UnboundLocalError
                unit_numbers={"HYD":"9121179317","warangal":"8008346594","unit01":"9642421753"}  # Include 'unit01' for safety
                unit_number = unit_numbers.get(unit_name, head_office_number)  # Now safe; uses head_office_number as fallback
                for_main_mes = [unit_number, head_office_number]
                res = {}
                for i in for_main_mes:


                    link = f"salesrep.esanchaya.com/daily-data/{date.today()}/{message_history.unic_code}"

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


                    response = requests.post(url, data=payload)


                    if not (response.status_code):
                        _logger.error(f"SMS sending failed: {response.text}")
                        res[str(i)] = {'status': 'error', 'message': 'Failed to send OTP'}

                    res[str(i)] = {'status': 'success', 'message': 'OTP sent successfully'}

                for i in total_agencies_filled_custon_forms_today:

                    message_history = request.env['message.history'].create({
                        'unit_name': unit_name,
                        'date': date.today(),
                        'agency': i[0]
                    })

                    message_history.sudo().generate_token()

                    link = f"salesrep.esanchaya.com/daily-data/{message_history.unic_code}"
                    msg = (
                        f"Hi,We are sharing the circulation subscribers details please click on the link {link} EENADU-CIRCULATION"
                    )
                    url = "https://www.smsstriker.com/API/sms.php"

                    payload = {
                        'username': 'EERETA',
                        'password': 'EERETA',
                        'from': 'EERETA',
                        'to': i[1],
                        'msg': msg,
                        'type': '1',
                        'template_id': '1407175507724602621'
                    }

                    response = requests.post(url, data=payload)
                    if not (response.status_code):
                        _logger.error(f"SMS sending failed: {response.text}")
                        res[str(i)] = {'status': 'error', 'message': 'Failed to send OTP'}

                    res[str(i)] = {'status': 'success', 'message': 'OTP sent successfully'}

                # _logger.info("SMS Response: %s %s", response.status_code, response.text)
        except Exception as e:
            _logger.exception("Error sending OTP")
            return {'status': 'error', 'message': str(e)}
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('send_message_sales_rep', execution_time)