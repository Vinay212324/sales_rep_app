from odoo import models, fields, api
import random
import logging
_logger = logging.getLogger(__name__)

class OtpVerification(models.Model):
    _name = 'otp.verification'
    _description = 'OTP Verification'

    phone = fields.Char(required=True)
    otp = fields.Char(required=True)
    is_verified = fields.Boolean(default=False)
    created_at = fields.Datetime(auto_now_add=True)
