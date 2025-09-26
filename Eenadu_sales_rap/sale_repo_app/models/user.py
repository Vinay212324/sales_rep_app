from odoo import models, api, fields, _
from datetime import datetime, timedelta
import secrets
from odoo.exceptions import AccessDenied, ValidationError
from odoo.fields import Many2one
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font
import base64
from io import BytesIO
from odoo.http import request
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from odoo.tools import round


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
    name = fields.Char(string="Name")
    login = fields.Char(string="Login")
    password = fields.Char(string="Password")

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

    #for Customerforms xl report
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    dummy_file = fields.Binary("Excel File", readonly=True, attachment=True)
    dummy_file_name = fields.Char("File Name")
    unit_selection = fields.Selection([("HYD","HYD"),("warangal","warangal"),("All","All UNITS")])


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
    # for xl report
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from io import BytesIO
    import base64



    def download_xl_report(self):
        for_Dates = (str(self.start_date) if self.start_date else "") + " -- " + (str(self.end_date) if self.end_date else "")


        wb = Workbook()
        ws = wb.active
        ws.title = "Staff Analysis"

        # First row headings
        ws["A1"].value = "SN"
        ws["B1"].value = "UNIT NAME"

        # Merge for date range heading
        ws.merge_cells("C1:G1")
        main_heading_cell = ws["C1"]
        main_heading_cell.value = for_Dates
        main_heading_cell.alignment = Alignment(horizontal="center", vertical="center")
        main_heading_cell.font = Font(bold=True, size=12)

        # Merge for "PROMOTERES"
        ws.merge_cells("C2:G2")
        main_heading_cell = ws["C2"]
        main_heading_cell.value = "PROMOTERES"
        main_heading_cell.alignment = Alignment(horizontal="center", vertical="center")
        main_heading_cell.font = Font(bold=True, size=11)

        # Sub-headings in row 3
        ws["C3"].value = "MAN"
        ws["D3"].value = "CPS"
        ws["E3"].value = "SPOT"
        ws["F3"].value = "1st"
        ws["G3"].value = "AVG"

        # Make headers bold + bigger + centered
        header_cells = ["A1", "B1", "C3", "D3", "E3", "F3", "G3"]
        for cell_ref in header_cells:
            cell = ws[cell_ref]
            cell.font = Font(bold=True, size=12)
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Set column widths
        ws.column_dimensions["A"].width = 8
        ws.column_dimensions["B"].width = 20
        for col in ["C", "D", "E", "F", "G"]:
            ws.column_dimensions[col].width = 12

        # Center align ALL cells (headers + data)
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row,
                                min_col=1, max_col=ws.max_column):
            for cell in row:
                cell.alignment = Alignment(horizontal="center", vertical="center")

        user = user = request.env.user
        if not user.exists():
            return {"status": 404, "message": "User not found"}
        unit_names = []
        for i in user.unit_name_ids:
            unit_names.append(i.name)

        for i in range(1,len(unit_names)+1):
            num = 3 + i
            # inside your loop
            stats = self.env['customer.form'].get_customer_stats(
                start_date=self.start_date,
                end_date=self.end_date,
                unit_name=unit_names[i - 1]
            )
            forms = stats["forms"]  # actual recordset

            first_count = sum(1 for f in forms if f.Start_Circulating and f.Start_Circulating[-2:] == "01")
            sport_count = sum(1 for f in forms if f.Start_Circulating and f.Start_Circulating[-2:] != "01")
            aug = stats["total_forms"] / stats["unique_users"] if stats["unique_users"] else 0
            for j in range(1, 8):
                col_letter = chr(64 + j)
                cell = f"{col_letter}{num}"
                if j == 1:
                    ws[cell].value = str(i)  # SN
                elif j == 2:
                    ws[cell].value = unit_names[i - 1]  # Unit Name
                elif j == 3:
                    ws[cell].value = stats["unique_users"]  # Unique Users
                elif j == 4:
                    ws[cell].value = stats["total_forms"]  # Total Forms
                elif j == 5:
                    ws[cell].value = sport_count
                if j == 6:
                    ws[cell].value = first_count
                if j == 7:
                    ws[cell].value = float(f"{float(aug):.2f}") if aug not in (None, "") else 0.0






                    # Save to memory
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)

        # Save into wizard field
        file_data = base64.b64encode(file_stream.read())
        self.write({
            'dummy_file': file_data,
            'dummy_file_name': "staff_analysis.xlsx"
        })

        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model=users.wizard&id={self.id}&field=dummy_file&filename_field=dummy_file_name&download=true",
            'target': 'new',  # ensures download in new tab
        }

    def _get_daily_attendance(self, start_date, end_date, unit_name=None):
        """
        Returns a dict:
        {
            user_id: {
                date: {'attendance': 'P/Logged in' or 'A/Not Logged', 'copies': int},
                'total': int,
                'total_copies': int,
                'forms_count': int
            }
        }
        """
        users_domain = [("role", "=", "agent")]
        if unit_name and unit_name != "ALL UNITS":
            users_domain.append(("unit_name", "=", unit_name))

        users = self.env['res.users'].search(users_domain)
        sessions = self.env['work.session'].search([
            ('start_time', '>=', start_date),
            ('end_time', '<=', end_date),
        ])
        forms = self.env['customer.form'].search([  # <-- replace with your actual model for forms/copies
            ('date', '>=', start_date),
            ('date', '<=', end_date),
        ])

        result = {}
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        for user in users:
            result[user.id] = {}
            total_attendance = 0
            total_copies = 0

            for d in date_range:
                # Attendance check
                day_sessions = sessions.filtered(
                    lambda s: s.user_id == user and s.start_time.date() == d
                )
                attendance_val = "P/Logged in" if day_sessions else "A/Not Logged"
                if day_sessions:
                    total_attendance += 1

                # Copies count (forms filled that day)
                day_forms = forms.filtered(lambda f: f.agent_login == user.login and f.date == d)
                copies_val = len(day_forms)  # or f.copies if you have quantity field
                total_copies += copies_val

                result[user.id][d] = {
                    "attendance": attendance_val,
                    "copies": copies_val,
                }

            result[user.id]['total'] = total_attendance
            result[user.id]['total_copies'] = total_copies
            result[user.id]['forms_count'] = total_copies  # keep same for clarity

        return result

    def download_attendance_report(self):
        start_date = self.start_date
        end_date = self.end_date
        unit_name = self.unit_selection  # assuming you store Unit Selection here

        wb = Workbook()
        ws = wb.active
        ws.title = "Promoters Attendance"

        # --- Header row ---
        ws["A1"].value = "S.No"
        ws["B1"].value = "Name"
        ws.column_dimensions["B"].width = 18

        date_range = [start_date + timedelta(days=i)
                      for i in range((end_date - start_date).days + 1)]

        col = 3  # start column for dates
        for d in date_range:
            left_col = col
            right_col = col + 1

            # Merge date cells
            ws.merge_cells(start_row=1, start_column=left_col, end_row=1, end_column=right_col)

            # Date header
            top_cell = ws.cell(row=1, column=left_col)
            top_cell.value = d.strftime("%d-%m-%Y")
            top_cell.alignment = Alignment(horizontal="center", vertical="center")
            top_cell.font = Font(bold=True, size=10)

            # Sub-headers
            in_cell = ws.cell(row=2, column=left_col)
            out_cell = ws.cell(row=2, column=right_col)
            in_cell.value = "Attendance"
            out_cell.value = "Copies"
            for c in (in_cell, out_cell):
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.font = Font(bold=True, size=9)

            # Column widths
            ws.column_dimensions[get_column_letter(left_col)].width = 12
            ws.column_dimensions[get_column_letter(right_col)].width = 12

            col += 2

        # --- Totals ---
        ws.merge_cells(start_row=1, start_column=col, end_row=1, end_column=col + 1)
        ws.cell(row=1, column=col).value = "Total Count"
        ws.cell(row=1, column=col).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=1, column=col).font = Font(bold=True, size=10)
        ws.column_dimensions[get_column_letter(col)].width = 16
        ws.column_dimensions[get_column_letter(col + 1)].width = 16

        in_cell = ws.cell(row=2, column=col)
        out_cell = ws.cell(row=2, column=col + 1)
        in_cell.value = "Total Attendance"
        out_cell.value = "Total Copies"

        # --- UNIT ---
        unit_col = col + 2
        ws.cell(row=1, column=unit_col).value = "UNIT"
        ws.cell(row=1, column=unit_col).alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(unit_col)].width = 14

        # --- Forms Count ---
        forms_col = unit_col + 1
        ws.cell(row=1, column=forms_col).value = "Forms Count"
        ws.cell(row=1, column=forms_col).alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(forms_col)].width = 16

        for c in (in_cell, out_cell):
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.font = Font(bold=True, size=9)

        # --- Attendance data ---
        data = self._get_daily_attendance(start_date, end_date, unit_name)
        users_domain = [("role", "=", "agent")]
        if unit_name and unit_name != "ALL UNITS":
            users_domain.append(("unit_name", "=", unit_name))
        users = self.env['res.users'].search(users_domain)

        row = 3
        for idx, user in enumerate(users, start=1):
            ws.cell(row=row, column=1).value = idx
            ws.cell(row=row, column=2).value = user.name

            col_ptr = 3
            for d in date_range:
                ws.cell(row=row, column=col_ptr).value = data[user.id][d]["attendance"]  # Attendance
                ws.cell(row=row, column=col_ptr + 1).value = data[user.id][d]["copies"]  # Copies
                col_ptr += 2

            ws.cell(row=row, column=col_ptr).value = data[user.id]['total']
            ws.cell(row=row, column=col_ptr + 1).value = data[user.id]['total_copies']
            ws.cell(row=row, column=unit_col).value = user.unit_name or ""
            ws.cell(row=row, column=forms_col).value = data[user.id]['forms_count']

            row += 1

        # --- Save file ---
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        file_data = base64.b64encode(file_stream.read())

        self.write({
            'dummy_file': file_data,
            'dummy_file_name': "attendance_report.xlsx"
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model=users.wizard&id={self.id}&field=dummy_file&filename_field=dummy_file_name&download=true",
            'target': 'new',
        }