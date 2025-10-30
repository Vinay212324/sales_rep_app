from odoo import models, fields, _

class FunctionTiming(models.Model):
    _name = 'function.timing'
    _description = 'Function Execution Timing'
    _rec_name = 'name'

    name = fields.Char(string='Function Name', required=True, help='Name of the function being tracked')
    max_time = fields.Float(string='Maximum Execution Time (seconds)', required=True, default=0.0)
    min_time = fields.Float(string='Minimum Execution Time (seconds)', required=True, default=0.0)
    executions = fields.Integer(string='Number of Executions', default=1, help='Total times this function has been executed')
    average_time = fields.Float(string='Average Execution Time (seconds)', compute='_compute_average_time', store=True)
    total_time = fields.Float(string='Total Execution Time (seconds)', default=0.0, help='Sum of all execution times for average calculation')

    def _compute_average_time(self):
        for record in self:
            if record.executions > 0:
                record.average_time = record.total_time / record.executions
            else:
                record.average_time = 0.0

    def update_timing(self, new_time):
        """
        Update or create timing record for a function with a new execution time.
        :param new_time: float - The new execution time in seconds.
        :return: The updated or created record.
        """
        if new_time < 0:
            raise ValueError(_('Execution time cannot be negative.'))

        # Search for existing record
        existing = self.search([('name', '=', self.name)], limit=1)
        if existing:
            # Update existing
            existing.total_time += new_time
            existing.min_time = min(existing.min_time, new_time)
            existing.max_time = max(existing.max_time, new_time)
            existing.executions += 1
            existing._compute_average_time()  # Trigger recompute
            return existing
        else:
            # Create new (assuming self.name is set, or pass name as param in real use)
            return self.create({
                'name': self.name or 'Unnamed Function',
                'min_time': new_time,
                'max_time': new_time,
                'total_time': new_time,
                'executions': 1,
            })