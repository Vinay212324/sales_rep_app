from odoo import models, api, fields, _

class RootMap(models.Model):
    _name = "pin.location"
    _description = "For Pin Location"
    _order = "location_name"

    code = fields.Char(string="Code")
    location_name = fields.Char(string="Location Name")

