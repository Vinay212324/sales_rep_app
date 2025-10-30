import logging
from odoo import http
from odoo.http import request
import time

_logger = logging.getLogger(__name__)

class localApi(http.Controller):

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

    @http.route('/get_created_staff', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def get_user_you_created(self, **kwargs):
        start_time = time.time()
        try:
            user = request.env.user
            user_id = user.id
            unit_name = user.unit_name
            users = request.env['res.users'].sudo().search([
                ('unit_name', '=', unit_name),
                ('role', '=', 'agent'),
                ('status', 'in', ['active', 'un_activ'])
            ])

            user_list = []
            agencies = request.env['pin.location'].sudo().search([('unit_name', '=', user.unit_name)])
            ags = []
            count = request.env['res.users'].sudo().search_count([('unit_name', '=', user.unit_name),('role','=','agent'),('status','=','active')])
            cu_count = request.env['customer.form'].sudo().search_count([('unit_name', '=', user.unit_name)])
            for agency in agencies:
                ags.append({
                    "id": agency.id,
                    "code":agency.code,
                    "location_name":agency.location_name,
                    "name":agency.name,
                    "phone":agency.phone,
                    "unit_name":agency.unit_name,
                })

            for user in users:
                user_list.append({
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'login': user.login,
                    'create_uid': user.create_uid.id if user.create_uid else False,
                    'unit_name': user.unit_name,
                    'phone': user.phone,
                    'state': user.state,
                    'pan_number': user.pan_number,
                    'aadhar_number': user.aadhar_number,
                    'role': user.role,
                    'status': user.status,
                })

            result = {'status': 200, 'users': user_list,'count':count,'cu_count': cu_count, 'agencies':ags, 'unit_name': unit_name}
            return result

        except Exception as e:
            result = {'error': 'Internal Server Error', 'message': str(e), 'code': 500}
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('get_user_you_created', execution_time)

    @http.route("/local/update/status", type="json", methods=['POST'], csrf=False, cors="*")
    def _update_status(self, **params):
        start_time = time.time()
        try:
            user_id = params.get("user_id")
            print(user_id)
            if not user_id:
                return {'error': 'User ID is required', "code": "403"}

            try:
                user_id = int(user_id)
            except ValueError:
                return {'error': 'Invalid User ID', "code": "403"}

            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                return {'error': 'User not found', "code": "403"}
            if params.get("status") not in ["active", "un_activ"]:
                return {'error': 'status is missing'}

            user.write({
                'status': params.get("status"),
            })
            if user.status == params.get("status"):
                result = {"success": True, "user_id": user.id, "code": "200"}
                return result
            else:
                result = {"success": False, "code": "403"}
                return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('_update_status', execution_time)

    @http.route('/create_staff', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def create_staff(self, **kwargs):
        start_time = time.time()
        try:
            print("vinay21212121aaaaaaaaaaaaaaaa")

            staff_data = kwargs.get('params', {})
            print(staff_data)
            print(staff_data.get('name'))
            user = request.env.user
            print(user.id)
            vals = {
                'name': staff_data.get('name'),
                'unit_name': staff_data.get('unit'),
                'email': staff_data.get('email'),
                'login': staff_data.get('user_id'),
                'password': staff_data.get('password'),
                'phone': staff_data.get('phone'),
                'aadhar_number': staff_data.get('adhaar'),
                'role': "agent",
                'status': 'active',
                'create_uid': user.id,
                # Add any other necessary values here
            }
            staff_user = request.env['res.users'].sudo().create(vals)
            print(staff_user.id,"vinay")
            result = {'status': 200, 'id': staff_user.id}
            return result
        except Exception as e:
            _logger.error("Staff Creation Error: %s", e)
            result = {'error': 'Internal Server Error', 'message': str(e), 'code': 500}
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('create_staff', execution_time)

    @http.route('/user_info', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def user_info(self, **kwargs):
        start_time = time.time()
        try:
            print("vinay21212121angngfnfgnfgnfgnftgnaaaaaaaaaaa")

            user = request.env.user
            print(user.id)
            vals = {
                'name': user.name,
                'unit_name': user.unit_name,
                'email': user.email,
                'login': user.login,
                'phone': user.phone,
                'aadhar_number': user.aadhar_number,
                'create_uid': user.id,
            }

            result = {'status': 200, 'user_info': vals}
            return result
        except Exception as e:
            _logger.error("Staff Creation Error: %s", e)
            result = {'error': 'Internal Server Error', 'message': str(e), 'code': 500}
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('user_info', execution_time)

    @http.route('/get_staff_details', type='json', auth='user')
    def get_staff_details(self, id):
        start_time = time.time()
        try:
            user = request.env['res.users'].sudo().browse(int(id))
            if not user.exists():
                result = {"status": 404, "message": "User not found"}
                return result

            result = {
                "status": 200,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "aadhar_number": user.aadhar_number,
                    "unit_name": user.unit_name or "",
                    "status": user.active and "Active" or "Inactive",
                }
            }
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('get_staff_details', execution_time)

    #for re head
    @http.route('/get_units_details', type='json', auth='user',methods=['POST'])
    def get_units_details(self):
        start_time = time.time()
        try:
            user = request.env.user
            if not user.exists():
                result = {"status": 404, "message": "User not found"}
                return result
            unit_names=[]
            for i in user.unit_name_ids:
                unit_names.append(i.name)

            result = {
                "status": 200,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "aadhar_number": user.aadhar_number,
                    "status": user.active and "Active" or "Inactive",
                    "unit_name_ids":unit_names,
                }
            }
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('get_units_details', execution_time)

    @http.route('/get_unit_information_users', type='json', auth='user', methods=['POST'])
    def get_unit_information(self, **params):
        start_time = time.time()
        try:
            unit_name = params.get('unit')
            print("Unit Name:", unit_name)

            users = request.env['res.users'].sudo().search([('unit_name', '=', unit_name)])

            if not users:
                result = {"status": 404, "message": "User not found"}
                return result

            user_names = {
                "circulation_incharge": [],
                "segment_incharge": [],
                "unit_manager":[],
                "Office_staff":[],
                "agent":[],
            }

            for user in users:
                if user.role == "circulation_incharge":
                    user_names["circulation_incharge"].append({
                        "id": user.id,
                        "name": user.name,
                        "role": "Circulation Incharge",
                        "email": user.email,
                        "phone": user.phone,
                        "aadhar_number": user.aadhar_number,
                        "status": "Active" if user.active else "Inactive",
                    })
                elif user.role == "segment_incharge":
                    user_names["segment_incharge"].append({
                        "id": user.id,
                        "name": user.name,
                        "role": "Segment Incharge",
                        "email": user.email,
                        "phone": user.phone,
                        "aadhar_number": user.aadhar_number,
                        "status": "Active" if user.active else "Inactive",
                    })
                elif user.role == "unit_manager":
                    user_names["unit_manager"].append({
                        "id": user.id,
                        "name": user.name,
                        "role": "Unit Manager",
                        "email": user.email,
                        "phone": user.phone,
                        "aadhar_number": user.aadhar_number,
                        "status": "Active" if user.active else "Inactive",
                    })
                elif user.role == "Office_staff":
                    user_names["Office_staff"].append({
                        "id": user.id,
                        "name": user.name,
                        "role": "Office Staff",
                        "email": user.email,
                        "phone": user.phone,
                        "aadhar_number": user.aadhar_number,
                        "status": "Active" if user.active else "Inactive",
                    })
                elif user.role == "agent":
                    user_names["agent"].append({
                        "id": user.id,
                        "name": user.name,
                        "role": "promoters",
                        "email": user.email,
                        "phone": user.phone,
                        "aadhar_number": user.aadhar_number,
                        "status": "Active" if user.active else "Inactive",
                    })

            return user_names
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('get_unit_information', execution_time)