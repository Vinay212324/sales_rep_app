from datetime import datetime
from odoo import api, SUPERUSER_ID
from odoo import models, fields, api
import pytz

class WorkSession(models.Model):
    _name = 'work.session'
    _description = 'Work Session with Selfies'
    _order = 'start_time desc'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.uid
    )
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    start_selfie = fields.Binary(string='Start Selfie')
    end_selfie = fields.Binary(string='End Selfie')

    duration = fields.Float(
        string="Duration (Hours)",
        compute="_compute_duration",
        store=True
    )

    # Convert start/end time into IST before saving
    @api.model
    def create(self, vals):
        ist = pytz.timezone('Asia/Kolkata')
        if vals.get('start_time'):
            dt = fields.Datetime.from_string(vals['start_time'])
            vals['start_time'] = fields.Datetime.to_string(dt.astimezone(ist))
        if vals.get('end_time'):
            dt = fields.Datetime.from_string(vals['end_time'])
            vals['end_time'] = fields.Datetime.to_string(dt.astimezone(ist))
        return super().create(vals)

    def write(self, vals):
        ist = pytz.timezone('Asia/Kolkata')
        if vals.get('start_time'):
            dt = fields.Datetime.from_string(vals['start_time'])
            vals['start_time'] = fields.Datetime.to_string(dt.astimezone(ist))
        if vals.get('end_time'):
            dt = fields.Datetime.from_string(vals['end_time'])
            vals['end_time'] = fields.Datetime.to_string(dt.astimezone(ist))
        return super().write(vals)

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                delta = rec.end_time - rec.start_time
                rec.duration = delta.total_seconds() / 3600.0
            else:
                rec.duration = 0.0
