from odoo import models, api, fields, _
from datetime import datetime, timedelta
import secrets
from odoo.exceptions import AccessDenied, ValidationError
from odoo.fields import Many2one


class Users(models.Model):
    _inherit = 'res.users'

    role = fields.Selection(
        [('agent', 'Staff'),
         ('Office_staff', 'Office staff'),
         ('unit_manager', 'unit manager'),
         ('segment_incharge', 'segment incharge'),
         ('circulation_incharge', 'circulation incharge'),
         ('region_head', 'region head'),
         ('circulation_head', 'circulation head'),('admin','admin')],
        string="Role", required=True, default="Office_staff"
    )
    unit_name_ids = fields.One2many('unit.name','unit_name_id')
    status = fields.Selection(
        [('un_activ', 'Waiting For Approve'),
         ('active', 'Approved'),
      ],
        string="Role", required=True, default="un_activ"
    )

    def waiting_for_approve(self):
        self.ensure_one()
        self.status = 'un_activ'

    def approved_staff(self):
        self.ensure_one()
        self.status = 'active'

    pin_location_ids = fields.Many2many('pin.location','user_id')
    present_pin_id = fields.Many2one("pin.location")
    aadhar_number = fields.Char(string="Aadhar")
    root_name_id = fields.Many2one('root.map', string="Root Map")
    pan_number = fields.Char(string="PAN")
    state = fields.Char(string="state")
    phone = fields.Char(string="phone")
    user_id = fields.Integer(string="User ID")
    unit_name = fields.Char(string="Unit Name")
    create_uid = fields.Many2one(string="Created By",readonly=0)
    api_token = fields.Char(string="API Token", readonly=True)
    token_expiry = fields.Datetime(string="Token Expiry")
    aadhar_base64 = fields.Binary(string="Aadhar image")
    Pan_base64 = fields.Binary(string="Pan image")
    target = fields.Char(string="Target")
    edit_boll = fields.Boolean(string="Edit Allowed", compute="_compute_sale_user_readonly", store=False)
    # created_by = fields.Many2one('res.users', string="Created By", related="create_uid", store=True, readonly=False)

    created_by = fields.Many2one(
        'res.users',
        string="Created By",
        related="create_uid",
        store=True,
        readonly=False,  # make it editable
        inverse="_inverse_created_by"
    )

    def _inverse_created_by(self):
        for rec in self:
            if rec.created_by:
                rec.write({'create_uid': rec.created_by.id})

    @api.depends_context('uid')
    def _compute_sale_user_readonly(self):
        current_user_in_group = self.env.user.has_group('sale_repo_app.circulation_incharge_group')
        for rec in self:
            rec.edit_boll = current_user_in_group

    def create_record(self):
        """
        Saves the record automatically and returns a success notification.
        """
        self.ensure_one()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Success!",
                'message': "User created successfully.",
                'type': 'success',
                'sticky': False,
            }
        }

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


    ROLE_GROUP_MAPPING = {
        'admin': 'sale_repo_app.admin_group',
        'circulation_head': 'sale_repo_app.circulation_head_group',
        'region_head': 'sale_repo_app.region_head_group',
        'unit_manager': 'sale_repo_app.unit_manager_group',
        'segment_incharge': 'sale_repo_app.segment_incharge_group',
        'circulation_incharge': 'sale_repo_app.circulation_incharge_group',
        'Office_staff': 'sale_repo_app.office_staff_group',
        'agent': 'sale_repo_app.agent_group',
    }

    # --- Create override to assign group by role ---
    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        for user in users:
            user._update_user_group_by_role()
        return users

    # --- Write override to reassign group if role changes ---
    def write(self, vals):
        res = super().write(vals)
        if 'role' in vals:
            for user in self:
                user._update_user_group_by_role()
        return res

    # --- Core logic: remove all mapped groups and assign only current role group ---
    def _update_user_group_by_role(self):
        if not self.role:
            return

        group_ids = []
        for group_xml_id in self.ROLE_GROUP_MAPPING.values():
            try:
                group = self.env.ref(group_xml_id, raise_if_not_found=False)
                if group:
                    group_ids.append(group.id)
            except Exception:
                continue

        # Remove all role-based groups
        self.groups_id = [(3, gid) for gid in group_ids]

        # Assign new group based on selected role
        new_group_xml_id = self.ROLE_GROUP_MAPPING.get(self.role)
        if new_group_xml_id:
            new_group = self.env.ref(new_group_xml_id, raise_if_not_found=False)
            if new_group:
                self.groups_id = [(4, new_group.id)]

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields_res = super().fields_get(allfields=allfields, attributes=attributes)
        if 'role' in fields_res:
            if not (self.env.user.has_group('sale_repo_app.region_head_group') or
                    self.env.user.has_group('sale_repo_app.circulation_head_group')):
                fields_res['role']['readonly'] = True
        return fields_res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type,
                                      toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            doc = etree.XML(res['arch'])
            role_field = doc.xpath("//field[@name='role']")
            if role_field:
                # Example: only show 'role' if current user is region_head or circulation_head
                if not self.env.user.has_group('sale_repo_app.region_head_group') and \
                        not self.env.user.has_group('sale_repo_app.circulation_head_group'):
                    for node in role_field:
                        node.set('modifiers', '{"invisible": true}')
                        node.set('readonly', "1")

            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

class unit_names(models.Model):
    _name = 'unit.name'

    name = fields.Char(string="Name")
    unit_name_id = fields.Many2one('res.users')




from odoo import models, fields, _

class UsersWizard(models.TransientModel):
    _name = "users.wizard"
    _description = "Users Wizard"

    # For creating a new res.users
    name = fields.Char(string="Name", required=True)
    login = fields.Char(string="Login", required=True)
    password = fields.Char(string="Password", required=True)

    # Custom fields
    role = fields.Selection(
        [
            ('agent', 'Staff'),
            ('Office_staff', 'Office staff'),
            ('unit_manager', 'Unit manager'),
            ('segment_incharge', 'Segment incharge'),
            ('circulation_incharge', 'Circulation incharge'),
            ('region_head', 'Region head'),
        ],
        string="Role",
        required=True,
    )
    status = fields.Selection(
        [('un_activ', 'Waiting For Approve'),
         ('active', 'Approved')],
        string="Status",
        default="un_activ",
        required=True,
    )
    unit_name_id = fields.Many2one('unit.name', string="Unit Name")
    aadhar_number = fields.Char(string="Aadhar")
    pan_number = fields.Char(string="PAN")
    phone = fields.Char(string="Phone")
    state = fields.Char(string="State")

    def action_create_user(self):
        self.ensure_one()

        vals = {
            'name': self.name,
            'login': self.login,
            'password': self.password,
            'role': self.role,
            'status': self.status,
            'unit_name': self.unit_name_id.name if self.unit_name_id else False,
            'aadhar_number': self.aadhar_number,
            'pan_number': self.pan_number,
            'phone': self.phone,
            'state': self.state,
        }

        # Create the user with sudo
        user = self.env['res.users'].sudo().create(vals)

        # Show a success notification
        self.env.cr.commit()  # ensure transaction commit before redirect
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Success",
                'message': f"User {user.name} created successfully!",
                'type': 'success',
                'sticky': False,
            }
        }, {
            # Redirect back to Users tree view
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'target': 'current',
        }
