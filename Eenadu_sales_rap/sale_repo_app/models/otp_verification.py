from odoo import models, fields, http, _
from odoo.http import request
import random
import requests
from datetime import datetime
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class PhoneVerificationOTP(models.Model):
    _name = 'phone.verification.otp'
    _description = 'OTP for phone verification'

    phone_number = fields.Char(string="Phone Number", required=True)
    otp_code = fields.Char(string="OTP")
    otp_time = fields.Datetime(string="OTP Sent Time")
