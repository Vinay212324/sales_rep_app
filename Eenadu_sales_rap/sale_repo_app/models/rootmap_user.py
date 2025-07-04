from odoo import models, api, fields, _
from datetime import datetime, timedelta

class root_map(models.Model):
    _name = "root.map"

    user_ids = fields.One2many('res.users','root_name_id', string="user_id")
    root_name = fields.Char(string="Root Map")
    date = fields.Date(string="Date")
