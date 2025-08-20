from odoo import models, api, fields, _
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)
import requests

class CustomerForm(models.Model):
    _name = 'circulation_incharge.view'
    _description = 'Circulation Incharge View'

    show_buttons = fields.Boolean(string="Show History Buttons", default=False)
    show_staff_list_button = fields.Boolean(string="Show History Buttons", default=False)
    # New field to store the count
    customer_form_count = fields.Integer(string="Customer Forms Count", compute='_compute_customer_form_count')

    # New method to compute the count
    @api.depends()
    def _compute_customer_form_count(self):
        # Always use a loop, even for a single record.
        for record in self:
            # Reconfirm the model name. It must be the `_name` from the Python file.
            # Assuming 'sale.repo.app.customer.form' is the correct name.
            customer_form_model = self.env['customer.form'].sudo()
            record.customer_form_count = customer_form_model.search_count([])

    def view_all_customer_form(self):
        self.ensure_one()
        self.show_buttons = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Circulation Incharge View',
            'res_model': 'circulation_incharge.view',
            'res_id': self.id,
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'main',
        }

    def overall_history_action(self):
        """
        Opens the customer form view from the sale_repo_app module.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': _('Overall History'),
            'res_model': 'customer.form',  # Replace with the correct model name if different
            'view_mode': 'kanban,form',
            'domain': [],  # Add any domain filtering here if needed
            'context': {'edit': 0,'create': 0},
        }

    def today_history_action(self):
        """
        Opens the customer form view with a domain to show only today's records.
        """
        # Get the current date and time
        today_date = fields.Date.today()

        # The domain to filter records created today
        # 'create_date' is the field Odoo uses for creation date.
        domain = [('create_date', '>=', today_date)]

        return {
            'type': 'ir.actions.act_window',
            'name': _("Today's Customer Forms"),
            'res_model': 'customer.form',
            'view_mode': 'kanban,form',
            'domain': domain,
            'context': {'edit': 0,'create': 0},
        }


    def create_office_staff(self):
        """
        Opens the customer form view from the sale_repo_app module.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Office Staff'),
            'res_model': 'office.staff',  # Replace with the correct model name if different
            'view_mode': 'form',
            'domain': [],  # Add any domain filtering here if needed
        }

    def approved_staff_list(self):
        """
        Opens a list view of all staff records with the 'approved' state.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approved Staff List'),
            'res_model': 'office.staff',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'approved')],
            'context': {'edit': 0,'create': 0},
        }

    def waiting_for_approval_staff_list(self):
        """
        Opens a list view of all staff records with the 'approved' state.
        """

        return {
            'type': 'ir.actions.act_window',
            'name': _('Waiting For Approval Staff List'),
            'res_model': 'office.staff',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'waiting')],
            'context': {'edit': 0, 'create': 0},
        }

    def view_all_staff_record(self):
        """
        Opens the customer form view from the sale_repo_app module.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': _('All Office Staff Records'),
            'res_model': 'office.staff',  # Replace with the correct model name if different
            'view_mode': 'tree,form',
            'domain': [],  # Add any domain filtering here if needed
            'context': {'edit': 0, 'create': 0},
        }





