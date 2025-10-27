from odoo import models, api, fields, _
from datetime import datetime, timedelta
import logging
import time

_logger = logging.getLogger(__name__)

class RootMap(models.Model):
    _name = "root.map"
    _description = "Rote Map"
    _order = "stage_dd"

    root_name = fields.Char(string="Rote assigner")
    date = fields.Date( string="Date")

    for_fromto_ids = fields.Many2many("fromto.rootmap", "fromto_ids",string="For From-To Rote")

    user_id = fields.Many2many('res.users', string='user information')
    user_ids = fields.One2many('res.users', 'root_name_id', string="user_id")

    # stage = fields.Selection([
    #     ('assigned', 'Assigned'),
    #     ('working', 'Working'),
    #     ('done', 'Done')
    # ], string="Stage", default='assigned')

    # stagess = fields.Selection([('vinay',"Vinay"),('not working','Working'),('workingg','yess')], string="Stagess")
    # stagess_dd = fields.Selection([('not_working','Assigned'),('vinay',"Working"),('workingg','Done')],
    #                               string="Stagess",default='not_working', required=True)
    stage_dd = fields.Selection([('not_working','Assigned'),('workingg','Done')],
                                  string="Stages",default='not_working', )

    @api.model
    def create(self, vals):
        start_time = time.time()
        record = super().create(vals)
        if 'user_id' in vals:
            users = self.env['res.users'].browse(vals['user_id'][0][2])
            users.write({'root_name_id': record.id})
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function create took {duration:.2f} seconds")
        return record

    def write(self, vals):
        start_time = time.time()
        res = super().write(vals)
        if 'user_id' in vals:
            for rec in self:
                users = rec.user_id
                users.write({'root_name_id': rec.id})
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function write took {duration:.2f} seconds")
        return res

    @api.model
    def default_get(self, fields_list):
        start_time = time.time()
        """Auto-fill fields when opening the form"""
        res = super().default_get(fields_list)
        user = self.env.user
        if 'root_name' in fields_list:
            res['root_name'] = user.name
        if 'date' in fields_list:
            res['date'] = datetime.now().date()

        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function default_get took {duration:.2f} seconds")
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