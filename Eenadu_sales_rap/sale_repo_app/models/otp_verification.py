# models/otp_verification.py
from odoo import models, fields, api
import random
import requests
from odoo.exceptions import ValidationError

class PhoneOTPVerification(models.Model):
    _name = 'phone.otp.verification'
    _description = 'Phone OTP Verification'

    phone = fields.Char(string="Phone Number", required=True)
    otp = fields.Char(string="OTP")
    is_verified = fields.Boolean(string="Verified", default=False)
