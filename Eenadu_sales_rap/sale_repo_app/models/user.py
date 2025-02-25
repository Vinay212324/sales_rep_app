from odoo import models, api, fields, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class Users(models.Model):
    _inherit = 'res.users'

    role = fields.Selection(
        [('lecel1', 'Level1'),
         ('level2', 'Level2'), ('level3', 'Level3'), ('level4', 'Level4'),],
        string="Role", required=True, default="lecel1"
    )

    user_id = fields.Integer(string="user_id")
    unit_name = fields.Char(string="unit name", default="terupati")


