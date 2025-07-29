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

    @http.route('/for/api/customer_form', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def apiCustomerForm(self, **kwargs):
        user = request.env.user
        print("vinayyyyyy2121232324")

        job_one = {
            "Central Job": "central_job",
            "PSU": "psu",
            "State Job": "state_job"
        }.get(kwargs.get('job_type_one'), "")

        customer = request.env['customer.form'].sudo().create({
            'agent_name': user.name,
            'agent_login': user.login,
            'unit_name': user.unit_name,
            'date': kwargs.get('date'),
            'time': kwargs.get('time'),
            'family_head_name': kwargs.get('family_head_name'),
            'father_name': kwargs.get('father_name'),
            'mother_name': kwargs.get('mother_name'),
            'spouse_name': kwargs.get('spouse_name'),
            'house_number': kwargs.get('house_number'),
            'street_number': kwargs.get('street_number'),
            'city': kwargs.get('city'),
            'pin_code': kwargs.get('pin_code'),
            'address': kwargs.get('address'),
            'mobile_number': kwargs.get('mobile_number'),
            'eenadu_newspaper': not (kwargs.get('eenadu_newspaper')),
            'feedback_to_improve_eenadu_paper': kwargs.get('feedback_to_improve_eenadu_paper'),
            'read_newspaper': kwargs.get('read_newspaper', False),
            'current_newspaper': kwargs.get('current_newspaper'),
            'reason_for_not_taking_eenadu_newsPaper': kwargs.get('reason_for_not_taking_eenadu_newsPaper'),
            'reason_not_reading': kwargs.get('reason_not_reading'),
            'free_offer_15_days': kwargs.get('free_offer_15_days', False),
            'reason_not_taking_offer': kwargs.get('reason_not_taking_offer'),
            'employed': not (kwargs.get('employed')),
            'job_type': kwargs.get('job_type'),
            'job_type_one': job_one,
            'job_profession': kwargs.get('job_profession'),
            'job_designation': kwargs.get('job_designation'),
            'company_name': kwargs.get('company_name'),
            'job_working_state': kwargs.get('job_working_state'),
            'job_working_location': kwargs.get('job_working_location'),
            'job_location_landmark': kwargs.get('job_location_landmark'),
            'profession': kwargs.get('profession'),
            'job_designation_one': kwargs.get('job_designation_one'),
            'latitude': kwargs.get('latitude'),
            'longitude': kwargs.get('longitude'),
            'location_address': kwargs.get('location_address'),
            'location_url': f"https://www.google.com/maps?q={kwargs.get('latitude')},{kwargs.get('longitude')}",
        })

        print("happpppp")

        return {
            'status': "success",
            'success': True,
            'message': 'Customer Form created successfully',
            'customer_id': customer.id,
            "code": "200"
        }
