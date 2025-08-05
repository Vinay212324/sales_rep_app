from odoo import models, fields

class PhoneVerificationOTP(models.Model):
    _name = 'phone.verification.otp'
    _description = 'OTP for phone verification'

    phone_number = fields.Char(string="Phone Number", required=True)
    otp_code = fields.Char(string="OTP")
    is_verified = fields.Boolean(default=False)
    otp_time = fields.Datetime(string="OTP Sent Time")
