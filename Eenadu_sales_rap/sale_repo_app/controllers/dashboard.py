import logging
from odoo import http
from odoo.http import request
from datetime import date
import time

_logger = logging.getLogger(__name__)

class CustomerFormAPI(http.Controller):

    @http.route('/api/dashboard_data', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def dashboard_data(self, **kwargs):
        user = request.env.user  # Gets the currently logged-in user
        role = user.role or 'unknown'  # Access your custom 'role' field
        name = user.name
        target = user.target
        agent_login = user.login
        today_date = date.today()

        now = time.time()

        today_customer_forms_count = request.env['customer.form'].sudo().search_count([
            ('agent_login', '=', agent_login),
            ('date', '=', today_date)
        ])

        target_left = int(target) - today_customer_forms_count

        return {
            "success": True,
            "name": name,
            "role": role,
            "target":target,
            "today_customer_forms_count":today_customer_forms_count,
            "target_left":target_left,
        }
