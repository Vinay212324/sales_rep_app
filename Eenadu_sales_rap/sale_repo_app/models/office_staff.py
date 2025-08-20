from odoo import models, api, fields, _
from datetime import datetime, date, timedelta
import logging

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
        self.ensure_one()
        self.state = 'waiting'

    def approved_staff(self):
        self.ensure_one()
        self.state = 'approved'


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
                'message': "Record created successfully.",
                'type': 'success',
                'sticky': False,
            }
        }


