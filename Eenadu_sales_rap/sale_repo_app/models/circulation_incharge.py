from odoo import models, api, fields, _
from datetime import datetime, date, timedelta
import logging
import time

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
        start_time = time.time()
        # Always use a loop, even for a single record.
        for record in self:
            # Reconfirm the model name. It must be the `_name` from the Python file.
            # Assuming 'sale.repo.app.customer.form' is the correct name.
            customer_form_model = self.env['customer.form'].sudo()
            record.customer_form_count = customer_form_model.search_count([])
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function _compute_customer_form_count took {duration:.2f} seconds")

    def action_save_and_notify(self):
        start_time = time.time()
        """
        Saves the record and displays a success notification.
        """
        self.ensure_one()

        result = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Success!",
                'message': "Staff created successfully.",
                'type': 'success',
                'sticky': False,
            }
        }
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function action_save_and_notify took {duration:.2f} seconds")
        return result

    def view_all_customer_form(self):
        start_time = time.time()
        self.ensure_one()
        self.show_buttons = True
        result = {
            'type': 'ir.actions.act_window',
            'name': 'Circulation Incharge View',
            'res_model': 'circulation_incharge.view',
            'res_id': self.id,
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'main',
        }
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function view_all_customer_form took {duration:.2f} seconds")
        return result

    def overall_history_action(self):
        start_time = time.time()
        """
        Opens the customer form view from the sale_repo_app module.
        """
        result = {
            'type': 'ir.actions.act_window',
            'name': _('Overall History'),
            'res_model': 'customer.form',  # Replace with the correct model name if different
            'view_mode': 'kanban,form',
            'domain': [],  # Add any domain filtering here if needed
            'context': {'edit': 0,'create': 0},
        }
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function overall_history_action took {duration:.2f} seconds")
        return result

    def today_history_action(self):
        start_time = time.time()
        """
        Opens the customer form view with a domain to show only today's records.
        """
        # Get the current date and time
        today_date = fields.Date.today()

        # The domain to filter records created today
        # 'create_date' is the field Odoo uses for creation date.
        domain = [('create_date', '>=', today_date)]

        result = {
            'type': 'ir.actions.act_window',
            'name': _("Today's Customer Forms"),
            'res_model': 'customer.form',
            'view_mode': 'kanban,form',
            'domain': domain,
            'context': {'edit': 0,'create': 0},
        }
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function today_history_action took {duration:.2f} seconds")
        return result

    def create_office_staff(self):
        start_time = time.time()
        """
        Opens the specific custom form view for creating office staff.
        """
        self.ensure_one()
        # Reference the new action record you created
        action = self.env.ref('sale_repo_app.action_create_office_staff_custom_form').read()[0]
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function create_office_staff took {duration:.2f} seconds")
        return action

    def approved_staff_list(self):
        start_time = time.time()
        """
        Opens a list view of all staff records with the 'approved' state.
        """
        self.ensure_one()
        # Reference the new action record you created
        action = self.env.ref('sale_repo_app.action_approved_staff_list').read()[0]
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function approved_staff_list took {duration:.2f} seconds")
        return action

    def waiting_for_approval_staff_list(self):
        start_time = time.time()
        """
        Opens a list view of all staff records with the 'approved' state.
        """

        self.ensure_one()
        # Reference the new action record you created
        action = self.env.ref('sale_repo_app.action_waiting_for_approve_staff_list').read()[0]
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function waiting_for_approval_staff_list took {duration:.2f} seconds")
        return action

    def view_all_staff_record(self):
        start_time = time.time()
        """
        Opens the customer form view from the sale_repo_app module.
        """
        self.ensure_one()
        # Reference the new action record you created
        action = self.env.ref('sale_repo_app.action_res_users_view0').read()[0]
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function view_all_staff_record took {duration:.2f} seconds")
        return action