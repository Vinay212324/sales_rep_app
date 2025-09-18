from odoo import models, fields, api
from datetime import datetime, timedelta
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

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        ist = pytz.timezone('Asia/Kolkata')  # ✅ IST timezone
        for rec in self:
            if rec.start_time and rec.end_time:
                # Convert to IST
                start_ist = rec.start_time.astimezone(ist)
                end_ist = rec.end_time.astimezone(ist)

                delta = end_ist - start_ist
                rec.duration = delta.total_seconds() / 3600.0
            else:
                rec.duration = 0.0
