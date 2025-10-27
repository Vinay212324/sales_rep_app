from odoo import models, api, fields, _
from datetime import datetime, date, timedelta
import logging
import time

_logger = logging.getLogger(__name__)
import requests

class CustomerForm(models.Model):
    _name = 'office.staff'
    _description = 'Create Office Staff'

    # show_buttons = fields.Boolean(string="Show History Buttons", default=False)
    name = fields.Char(string="Name")
    unit_name = fields.Char(string="Unit")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email/User Id")
    password = fields.Char(string="Password")
    address = fields.Char(string="Address")
    aadhar = fields.Char(string="Aadhar Number")
    aadhar_photo = fields.Binary(string="Upload Aadhar")
    pan = fields.Char(string="PAN")
    pan_photo = fields.Binary(string="Upload PAN")

    # New state field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting for Approval'),
        ('approved', 'Approved'),
    ], string='Status', default='draft')

    def waiting_for_approve(self):
        start_time = time.time()
        self.ensure_one()
        self.state = 'waiting'
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function waiting_for_approve took {duration:.2f} seconds")

    def approved_staff(self):
        start_time = time.time()
        self.ensure_one()
        self.state = 'approved'
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function approved_staff took {duration:.2f} seconds")

    def create_record(self):
        start_time = time.time()
        """
        Saves the record automatically and returns a success notification.
        """
        self.ensure_one()

        result = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Success!",
                'message': "User created successfully.",
                'type': 'success',
                'sticky': False,
            }
        }
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function create_record took {duration:.2f} seconds")
        return result