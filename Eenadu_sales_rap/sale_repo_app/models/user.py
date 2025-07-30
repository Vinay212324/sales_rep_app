from odoo import models, api, fields, _
from datetime import datetime, timedelta
import secrets
from odoo.exceptions import AccessDenied, ValidationError


class Users(models.Model):
    _inherit = 'res.users'

    role = fields.Selection(
        [('agent', 'agent'),
         ('Office_staff', 'Office staff'),
         ('unit_manager', 'unit manager'),
         ('segment_incharge', 'segment incharge'),
         ('circulation_incharge', 'circulation incharge'),
         ('region_head', 'region head'),
         ('circulation_head', 'circulation head'),('admin','admin')],
        string="Role", required=True, default="agent"
    )
    unit_name_ids = fields.One2many('unit.name','unit_name_id')
    status = fields.Selection(
        [('un_activ', 'un active'),
         ('active', 'Active'),
      ],
        string="Role", required=True, default="un_activ"
    )
    aadhar_number = fields.Char(string="Aadhar")
    root_name_id = fields.Many2one('root.map', string="Root Map")
    pan_number = fields.Char(string="PAN")
    state = fields.Char(string="state")
    phone = fields.Char(string="phone")
    user_id = fields.Integer(string="User ID")
    unit_name = fields.Char(string="Unit Name")
    # create_uid = fields.Integer(string="create_uid ID")
    api_token = fields.Char(string="API Token", readonly=True)
    token_expiry = fields.Datetime(string="Token Expiry")
    aadhar_base64 = fields.Binary(string="Aadhar image")
    Pan_base64 = fields.Binary(string="Pan image")
    target = fields.Char(string="Target")
    edit_boll = fields.Boolean(string="Edit Allowed", compute="_compute_sale_user_readonly", store=False)

    @api.depends_context('uid')
    def _compute_sale_user_readonly(self):
        current_user_in_group = self.env.user.has_group('sale_repo_app.circulation_incharge_group')
        for rec in self:
            rec.edit_boll = current_user_in_group

    def generate_token(self):
        """ Generate a unique API token and set an expiration time. """
        self.api_token = secrets.token_hex(32)  # Generates a unique 32-character token
        self.token_expiry = fields.Datetime.now() + timedelta(hours=10)  # Expires in 1 hour
        self.sudo().write({'api_token': self.api_token, 'token_expiry': self.token_expiry})  # Save token

    def authenticate_by_token(self, token):
        """ Validate the user using the API token. """
        user = self.sudo().search([('api_token', '=', token)], limit=1)
        if not user:
            raise AccessDenied(_("Invalid token!"))

        if user.token_expiry and user.token_expiry < fields.Datetime.now():
            raise AccessDenied(_("Token has expired! Please log in again."))

        return user

    def clear_token(self):
        """ Clear the token when the user logs out. """
        self.sudo().write({'api_token': False, 'token_expiry': False})

class unit_names(models.Model):
    _name = 'unit.name'

    name = fields.Char(string="Name")
    unit_name_id = fields.Many2one('res.users')