from odoo import models, api, fields, _
from datetime import datetime, timedelta
import secrets
from odoo.exceptions import AccessDenied, ValidationError
from odoo.fields import Many2one


class unit_names_sales(models.Model):
    _name = 'unit.names'

    unit_name = fields.Char(string="Unit Name")
    phone_number = fields.Char(string="Phone Number")

