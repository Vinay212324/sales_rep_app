from odoo import models, fields
from odoo.http import request
from odoo import http
from odoo.http import request
import random
import requests
import logging
from datetime import date
from odoo import models, fields
import requests
import logging
from datetime import date

_logger = logging.getLogger(__name__)


class PhoneVerificationOTP(models.Model):
    _name = 'verification.otp'
    _description = 'OTP for phone verification'

    phone_number = fields.Char(string="Phone Number", required=True)
    otp_code = fields.Char(string="OTP")
    is_verified = fields.Boolean(string="Is Verified", default=False)
    otp_time = fields.Datetime(string="OTP Sent Time", default=fields.Datetime.now)

    def send_message_sales_rep(self):
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


            # great = "happy"  # Unused, removed
            unit_numbers={"HYD":"9121179317","warangal":"8008346594"}
            # FIXED: Use bracket notation for dict access with unit_name as key
            unit_number = unit_numbers.get(unit_name, '')  # Fallback to empty if key missing
            if not unit_number:
                _logger.warning(f"No phone number found for unit: {unit_name}")
                continue  # Skip if no number
            head_office_number = "9642421753"
            for_main_mes = [unit_number, head_office_number]
            try:
                res = {}
                for i in for_main_mes:


                    link = f"https://salesrep.esanchaya.com/daily-data/{date.today()}/{message_history.unic_code}"  # Added https://

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

                    agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])  # Unused? Kept for now


                    response = requests.post(url, data=payload)


                    # FIXED: Check for successful status code (e.g., 200)
                    if response.status_code != 200:
                        _logger.error(f"SMS sending failed for {i}: {response.status_code} - {response.text}")
                        res[str(i)] = {'status': 'error', 'message': 'Failed to send message'}
                    else:
                        res[str(i)] = {'status': 'success', 'message': 'Message sent successfully'}

                for i in total_agencies_filled_custon_forms_today:

                    message_history = request.env['message.history'].create({
                        'unit_name': unit_name,
                        'date': date.today(),
                        'agency': i[0]
                    })

                    message_history.sudo().generate_token()

                    link = f"https://salesrep.esanchaya.com/daily-data/{message_history.unic_code}"  # Added https:// and fixed date placeholder if needed
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
                    # FIXED: Same status check
                    if response.status_code != 200:
                        _logger.error(f"SMS sending failed for agency {i[0]}: {response.status_code} - {response.text}")
                        res[str(i[1])] = {'status': 'error', 'message': 'Failed to send message'}  # Use phone as key
                    else:
                        res[str(i[1])] = {'status': 'success', 'message': 'Message sent successfully'}

                # _logger.info("SMS Response: %s %s", response.status_code, response.text)  # Moved inside loops
                _logger.info(f"Messages sent for unit {unit_name}: %s", res)
            except Exception as e:
                _logger.exception("Error sending messages for unit %s: %s", unit_name, str(e))
                return {'status': 'error', 'message': str(e)}
        return {'status': 'success', 'message': 'All messages processed'}