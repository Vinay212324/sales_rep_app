import logging
from odoo import http
from odoo.http import request
from datetime import date
import time

_logger = logging.getLogger(__name__)

class CustomerFormAPI(http.Controller):

    def _update_function_timing(self, function_name, execution_time):
        """
        Helper method to update or create timing record for a function.
        """
        if execution_time < 0:
            return  # Skip invalid times

        Timing = request.env['function.timing'].sudo()
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

    @http.route('/api/dashboard_data', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def dashboard_data(self, **kwargs):
        start_time = time.time()
        try:
            user = request.env.user
            name = user.name
            target = user.target or 0
            agent_login = user.login
            from datetime import date
            today_date = date.today()

            today_customer_forms_count = request.env['customer.form'].sudo().search_count([
                ('agent_login', '=', agent_login),
                ('date', '=', today_date)
            ])

            target_left = max(0, int(target) - today_customer_forms_count)

            result = {
                "success": True,
                "name": name,
                "target": target,
                "today_customer_forms_count": today_customer_forms_count,
                "target_left": target_left,
                # You can add other fields here as needed
                "subscribed_count": getattr(user, 'subscribed_count', 0),
                "shift_start_time": getattr(user, 'shift_start_time', ''),
            }
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('dashboard_data', execution_time)

    @http.route('/get_all_agencies_web', type='json', auth='user', methods=['GET', 'POST'], csrf=True)
    def get_all_agencies_web(self, **kwargs):
        start_time = time.time()
        try:
            pins = request.env['pin.location'].sudo().search([])
            data = [{'id': p.id, 'name': p.name, 'code': p.code, 'location_name': p.location_name} for p in pins]
            result = {'success': True, 'data': data}
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('get_all_agencies_web', execution_time)

    @http.route('/assign_agency_web', type='json', auth='user', methods=['POST'], csrf=True)
    def assign_agency_web(self, pin_lo_id=None, **kwargs):
        start_time = time.time()
        try:
            user = request.env.user
            if not pin_lo_id:
                return {'success': False, 'message': 'Please select an agency.'}
            pin_location = request.env['pin.location'].sudo().browse(int(pin_lo_id))
            if not pin_location.exists():
                return {'success': False, 'message': 'Selected agency was not found.'}

            user.sudo().write({
                'present_pin_id': pin_location.id,
            })

            result = {'success': True,
                      'message': f'Agency {pin_location.location_name or pin_location.name} assigned to {user.name}.'}
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('assign_agency_web', execution_time)

    @http.route('/get_current_agency_web', type='json', auth='user', methods=['GET', 'POST'], csrf=True)
    def get_current_agency_web(self, **kwargs):
        start_time = time.time()
        try:
            user = request.env.user
            pin = user.present_pin_id
            if not pin:
                return {'success': False, 'message': 'No current agency assigned.'}
            pin = request.env['pin.location'].sudo().browse(int(pin))
            if not pin.exists():
                return {'success': False, 'message': 'Current agency not found.'}
            result = {
                'success': True,
                'data': {
                    'id': pin.id,
                    'name': pin.name,
                    'location_name': pin.location_name,
                    'code': pin.code,
                }
            }
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('get_current_agency_web', execution_time)

    @http.route('/for/api/customer_form', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def apiCustomerForm(self, **kwargs):
        start_time = time.time()
        try:
            user = request.env.user
            print("vinayyyyyy2121232324")

            job_one = {
                "Central Job": "central_job",
                "PSU": "psu",
                "State Job": "state_job"
            }.get(kwargs.get('job_type_one'), "")

            customer = request.env['customer.form'].sudo().create({
                'agent_name': user.name,
                'Agency': user.present_pin_id.location_name,
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

            result = {
                'status': "success",
                'success': True,
                'message': 'Customer Form created successfully',
                'customer_id': customer.id,
                "code": "200"
            }
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('apiCustomerForm', execution_time)