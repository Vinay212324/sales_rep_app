from odoo import models, api, fields, _
import secrets
import string
import time

class RootMap(models.Model):
    _name = "message.history"
    _description = "For message history"

    unit_name = fields.Char()
    agency = fields.Char()
    date = fields.Date()
    unic_code = fields.Char()
    time = fields.Datetime(default=fields.Datetime.now)

    def _update_function_timing(self, function_name, execution_time):
        """
        Helper method to update or create timing record for a function.
        """
        if execution_time < 0:
            return  # Skip invalid times

        Timing = self.env['function.timing'].sudo()
        existing = Timing.search([('name', '=', function_name)], limit=1)
        if existing:
            existing.write({
                'total_time': existing.total_time + execution_time,
                'min_time': min(existing.min_time, execution_time),
                'max_time': max(existing.max_time, execution_time),
                'executions': existing.executions + 1,
            })
            # Trigger recompute for average
            existing._compute_average_time()
        else:
            Timing.create({
                'name': function_name,
                'min_time': execution_time,
                'max_time': execution_time,
                'total_time': execution_time,
                'executions': 1,
            })

    def generate_token(self):
        start_time = time.time()
        try:
            """Generate a short 7-character alphanumeric token and set it as unic_code."""
            characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
            token = ''.join(secrets.choice(characters) for _ in range(35))
            self.sudo().write({'unic_code': token})
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('generate_token', execution_time)