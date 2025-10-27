from odoo import models, api, fields, _
import secrets
import string
import logging
import time

_logger = logging.getLogger(__name__)

class RootMap(models.Model):
    _name = "message.history"
    _description = "For message history"

    unit_name = fields.Char()
    agency = fields.Char()
    date = fields.Date()
    unic_code = fields.Char()
    time = fields.Datetime(default=fields.Datetime.now)

    def generate_token(self):
        start_time = time.time()
        """Generate a short 7-character alphanumeric token and set it as unic_code."""
        characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
        token = ''.join(secrets.choice(characters) for _ in range(35))
        self.sudo().write({'unic_code': token})
        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function generate_token took {duration:.2f} seconds")