from odoo import models, fields, api, _
from datetime import datetime
import pytz  # Odoo 16 includes pytz; fallback for timezone handling (replaces zoneinfo for Python <3.9)
import requests
import logging

_logger = logging.getLogger(__name__)


class PhoneVerificationOTP(models.Model):
    _name = 'verification.otp'
    _description = 'OTP for phone verification'

    phone_number = fields.Char(string="Phone Number", required=True)
    otp_code = fields.Char(string="OTP")
    is_verified = fields.Boolean(string="Is Verified", default=False)
    otp_time = fields.Datetime(string="OTP Sent Time", default=fields.Datetime.now)

    @api.model
    def send_message_sales_rep(self):
        # Time check: Execute only at 7:30 PM IST
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        if now_ist.hour != 19 or now_ist.minute != 30:
            _logger.info("Cron triggered but not 7:30 PM IST (current: %s). Skipping execution.",
                         now_ist.strftime('%H:%M IST'))
            return  # Early exit if not the exact time

        _logger.info("Starting daily sales message dispatch at 7:30 PM IST")
        today = fields.Date.today()
        all_unit_names = self.env['res.users'].sudo().search([("role", "=", "circulation_incharge")])
        unit_set = list(set(all_unit_names.mapped('unit_name')))

        for unit_name in unit_set:
            _logger.info("Processing unit: %s", unit_name)
            count = self.env['customer.form'].sudo().search_count(
                [('unit_name', '=', unit_name), ('date', '=', today)])
            if count == 0:
                continue

            message_history = self.env['message.history'].sudo().create({
                'unit_name': unit_name,
                'date': today
            })
            message_history.sudo().generate_token()
            total_agencies = self.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])
            total_agencies_filled_custon_forms_today = []

            for agency in total_agencies:
                agency_count = self.env['customer.form'].sudo().search_count(
                    [('unit_name', '=', unit_name), ('date', '=', today), ('Agency', '=', agency.location_name)])
                if agency_count >= 1:
                    total_agencies_filled_custon_forms_today.append([agency.location_name, agency.phone])

            head_office_number = "703299504"
            unit_numbers = {"HYD": "9121179317", "warangal": "8008346594", "unit01": "9642421753"}
            unit_number = unit_numbers.get(unit_name, head_office_number)
            for_main_mes = [unit_number, head_office_number]

            res = {}
            try:
                for phone in for_main_mes:
                    link = f"salesrep.esanchaya.com/daily-data/{today}/{message_history.unic_code}"
                    msg = f"Hi, We are sharing the circulation subscribers details please click on the link {link} EENADU-CIRCULATION"
                    url = "https://www.smsstriker.com/API/sms.php"
                    payload = {
                        'username': 'EERETA',
                        'password': 'EERETA',
                        'from': 'EERETA',
                        'to': phone,
                        'msg': msg,
                        'type': '1',
                        'template_id': '1407175507724602621'
                    }
                    response = requests.post(url, data=payload)
                    if response.status_code != 200:
                        _logger.error(f"SMS sending failed for {phone}: {response.text}")
                        res[str(phone)] = {'status': 'error', 'message': 'Failed to send message'}
                    else:
                        res[str(phone)] = {'status': 'success', 'message': 'Message sent successfully'}

                for agency_data in total_agencies_filled_custon_forms_today:
                    agency_name, agency_phone = agency_data
                    agency_message_history = self.env['message.history'].sudo().create({
                        'unit_name': unit_name,
                        'date': today,
                        'agency': agency_name
                    })
                    agency_message_history.sudo().generate_token()
                    link = f"salesrep.esanchaya.com/daily-data/{agency_message_history.unic_code}"
                    msg = f"Hi, We are sharing the circulation subscribers details please click on the link {link} EENADU-CIRCULATION"
                    url = "https://www.smsstriker.com/API/sms.php"
                    payload = {
                        'username': 'EERETA',
                        'password': 'EERETA',
                        'from': 'EERETA',
                        'to': agency_phone,
                        'msg': msg,
                        'type': '1',
                        'template_id': '1407175507724602621'
                    }
                    response = requests.post(url, data=payload)
                    if response.status_code != 200:
                        _logger.error(f"SMS sending failed for agency {agency_name}: {response.text}")
                        res[str(agency_phone)] = {'status': 'error', 'message': 'Failed to send message'}
                    else:
                        res[str(agency_phone)] = {'status': 'success', 'message': 'Message sent successfully'}

                _logger.info("Daily SMS dispatch completed for unit %s: %s", unit_name, res)
            except Exception as e:
                _logger.exception("Error in send_message_sales_rep for unit %s: %s", unit_name, str(e))
                return {'status': 'error', 'message': str(e)}

        _logger.info("Daily sales message dispatch finished for all units at 7:30 PM IST")