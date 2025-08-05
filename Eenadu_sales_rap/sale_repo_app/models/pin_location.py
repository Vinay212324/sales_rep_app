from odoo import models, api, fields, _

class RootMap(models.Model):
    _name = "pin.location"
    _description = "For Pin Location"
    _order = "location_name"

    user_id = fields.Many2many('res.users',"pin_location_ids")
    code = fields.Char(string="AGTCD")
    location_name = fields.Char(string="Place")
    name = fields.Char(string="Name")


