from odoo import models, api, fields, _
from datetime import datetime, timedelta

class RootMap(models.Model):
    _name = "root.map"
    _description = "Root Map"
    _order = "stage_dd"

    root_name = fields.Char(string="Root Map")
    date = fields.Date( string="Date")

    for_fromto_ids = fields.Many2many("fromto.rootmap", "fromto_ids",string="For FROM TO roots")

    user_id = fields.Many2many('res.users', string='Vinay')
    user_ids = fields.One2many('res.users', 'root_name_id', string="user_id")

    # stage = fields.Selection([
    #     ('assigned', 'Assigned'),
    #     ('working', 'Working'),
    #     ('done', 'Done')
    # ], string="Stage", default='assigned')

    # stagess = fields.Selection([('vinay',"Vinay"),('not working','Working'),('workingg','yess')], string="Stagess")
    # stagess_dd = fields.Selection([('not_working','Assigned'),('vinay',"Working"),('workingg','Done')],
    #                               string="Stagess",default='not_working', required=True)
    stage_dd = fields.Selection([('not_working','Assigned'),('vinay',"Working"),('workingg','Done')],
                                  string="Stages",default='not_working', )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if 'user_id' in vals:
            users = self.env['res.users'].browse(vals['user_id'][0][2])
            users.write({'root_name_id': record.id})
        return record

    def write(self, vals):
        res = super().write(vals)
        if 'user_id' in vals:
            for rec in self:
                users = rec.user_id
                users.write({'root_name_id': rec.id})
        return res
class From_and_to_rootmap(models.Model):
    _name = "fromto.rootmap"
    _description = "Rote Map from to"

    from_location = fields.Char(string="From location")
    to_location = fields.Char(string="To location")
    extra_point = fields.Char(string="Add a point")
    extra_point_ids = fields.Many2many('extra.point', string="Extra Points")
    fromto_ids = fields.Many2many("root.map", string="From to rotes")



class ExtraPoint(models.Model):
    _name = 'extra.point'
    _description = 'Extra Point'

    name = fields.Char(string='Point Name', required=True)
