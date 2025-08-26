from odoo import models, fields
from odoo.http import request
from odoo import http
from odoo.http import request
import random
import requests
import logging
from datetime import date

class PhoneVerificationOTP(models.Model):
    _name = 'verification.otp'
    _description = 'OTP for phone verification'

    phone_number = fields.Char(string="Phone Number", required=True)
    otp_code = fields.Char(string="OTP")
    is_verified = fields.Boolean(string="Is Verified", default=False)
    otp_time = fields.Datetime(string="OTP Sent Time", default=fields.Datetime.now)

    def send_message(self):
        print("ppppppppp")
        all_unit_names = request.env['res.users'].sudo().search([("role","=","unit_manager"),("status","=","active")])
        unit_set = []
        print(all_unit_names)
        for res in all_unit_names:
            print(res.unit_name)
            unit_set.append(res.unit_name)
            print(unit_set)
        unit_set = set(unit_set)
        print(unit_set)
        for res in unit_set:
            unit_name = res
            message_history = request.env['message.history'].create({
                'unit_name': unit_name,
                'date': date.today()
            })
            print("regreger", message_history.id)
            message_history.sudo().generate_token()
            total_agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])
            total_agencies_filled_custon_forms_today = []
            for i in total_agencies:
                print(i, "vinay")
                count = request.env['customer.form'].sudo().search_count(
                    [('unit_name', '=', unit_name), ('date', '=', date.today()), ('Agency', '=', i.location_name)])
                if count >= 1:
                    total_agencies_filled_custon_forms_today.append([i.location_name, i.phone])

            great = "happy"
            unit_number = "9642421753"
            head_office_number = "9642421753"
            for_main_mes = [unit_number, head_office_number]
            try:
                res = {}
                for i in for_main_mes:

                    print(message_history.unic_code, "      hoooooo0")
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
                    print(agencies, "vinnnnn")

                    response = requests.post(url, data=payload)

                    print(response.text, response.status_code)
                    if not (response.status_code):
                        _logger.error(f"SMS sending failed: {response.text}")
                        res[str(i)] = {'status': 'error', 'message': 'Failed to send OTP'}

                    res[str(i)] = {'status': 'success', 'message': 'OTP sent successfully'}

                for i in total_agencies_filled_custon_forms_today:
                    unit_name = user.unit_name
                    print(unit_name)

                    message_history = request.env['message.history'].create({
                        'unit_name': unit_name,
                        'date': date.today(),
                        'agency': i[0]
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
                _logger.info("SMS Response: %s %s", response.status_code, response.text)
            except Exception as e:
                _logger.exception("Error sending OTP")
                return {'status': 'error', 'message': str(e)}
