from odoo import models, fields

class PhoneVerificationOTP(models.Model):
    _name = 'verification.otp'
    _description = 'OTP for phone verification'

    phone_number = fields.Char(string="Phone Number", required=True)
    otp_code = fields.Char(string="OTP")
    is_verified = fields.Boolean(string="Is Verified", default=False)
    otp_time = fields.Datetime(string="OTP Sent Time", default=fields.Datetime.now)
