from odoo import models, api, fields, _

class RootMap(models.Model):
    _name = "pin.location"
    _description = "For Pin Location"
    _order = "location_name"

    code = fields.Char(string="AGTCD")
    location_name = fields.Char(string="Place")
    name = fields.Char(string="Name")

