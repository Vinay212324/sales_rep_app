# models/work_session.py

from odoo import models, fields, api
from datetime import datetime

class WorkSession(models.Model):
    _name = 'work.session'
    _description = 'Work Session with Selfies'
    _order = 'start_time desc'

    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.uid)
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    start_selfie = fields.Binary(string='Start Selfie')
    end_selfie = fields.Binary(string='End Selfie')
