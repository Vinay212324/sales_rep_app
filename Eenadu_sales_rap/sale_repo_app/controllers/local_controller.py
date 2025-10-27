import logging
from odoo import http
from odoo.http import request
import time

_logger = logging.getLogger(__name__)

class localApi(http.Controller):

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
            duration = time.time() - start_time
            _logger.info(f"get_user_you_created completed successfully in {duration:.4f} seconds for unit: {unit_name}, returned {len(user_list)} users")
            return result

        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_user_you_created failed in {duration:.4f} seconds with error: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route("/local/update/status", type="json", methods=['POST'], csrf=False, cors="*")
    def _update_status(self, **params):
        start_time = time.time()
        try:
            user_id = params.get("user_id")
            _logger.info(f"user_id: {user_id}")
            if not user_id:
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: User ID is required")
                return {'error': 'User ID is required', "code": "403"}

            try:
                user_id = int(user_id)
            except ValueError:
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: Invalid User ID")
                return {'error': 'Invalid User ID', "code": "403"}

            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: User not found")
                return {'error': 'User not found', "code": "403"}
            if params.get("status") not in ["active", "un_activ"]:
                duration = time.time() - start_time
                _logger.info(f"_update_status completed in {duration:.4f} seconds with error: status is missing")
                return {'error': 'status is missing'}

            user.write({
                'status': params.get("status"),
            })
            if user.status == params.get("status"):
                result = {"success": True, "user_id": user.id, "code": "200"}
                duration = time.time() - start_time
                _logger.info(f"_update_status completed successfully in {duration:.4f} seconds for user: {user_id}")
                return result
            else:
                duration = time.time() - start_time
                _logger.warning(f"_update_status completed in {duration:.4f} seconds but status update failed for user: {user_id}")
                return {"success": False, "code": "403"}
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"_update_status failed in {duration:.4f} seconds with error: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route('/create_staff', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def create_staff(self, **kwargs):
        start_time = time.time()
        try:
            _logger.info("vinay21212121aaaaaaaaaaaaaaaa")
            staff_data = kwargs.get('params', {})
            _logger.info(f"staff_data: {staff_data}")
            _logger.info(f"name: {staff_data.get('name')}")
            user = request.env.user
            _logger.info(f"current user id: {user.id}")
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
            _logger.info(f"staff_user id: {staff_user.id}, vinay")
            result = {'status': 200, 'id': staff_user.id}
            duration = time.time() - start_time
            _logger.info(f"create_staff completed successfully in {duration:.4f} seconds for staff: {staff_data.get('name')}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"create_staff failed in {duration:.4f} seconds with error: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}


    @http.route('/user_info', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def user_info(self, **kwargs):
        start_time = time.time()
        try:
            _logger.info("vinay21212121angngfnfgnfgnfgnftgnaaaaaaaaaaa")
            user = request.env.user
            _logger.info(f"user id: {user.id}")
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
            duration = time.time() - start_time
            _logger.info(f"user_info completed successfully in {duration:.4f} seconds for user: {user.name}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"user_info failed in {duration:.4f} seconds with error: {str(e)}")
            return {'error': 'Internal Server Error', 'message': str(e), 'code': 500}

    @http.route('/get_staff_details', type='json', auth='user')
    def get_staff_details(self, id):
        start_time = time.time()
        try:
            user = request.env['res.users'].sudo().browse(int(id))
            if not user.exists():
                duration = time.time() - start_time
                _logger.info(f"get_staff_details completed in {duration:.4f} seconds with error: User not found")
                return {"status": 404, "message": "User not found"}

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
            duration = time.time() - start_time
            _logger.info(f"get_staff_details completed successfully in {duration:.4f} seconds for user: {id}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_staff_details failed in {duration:.4f} seconds with error: {str(e)}")
            return {"status": 500, "message": "Internal Server Error"}


    #for re head
    @http.route('/get_units_details', type='json', auth='user',methods=['POST'])
    def get_units_details(self):
        start_time = time.time()
        try:
            user = request.env.user
            if not user.exists():
                duration = time.time() - start_time
                _logger.info(f"get_units_details completed in {duration:.4f} seconds with error: User not found")
                return {"status": 404, "message": "User not found"}
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
            duration = time.time() - start_time
            _logger.info(f"get_units_details completed successfully in {duration:.4f} seconds for user: {user.name}")
            return result
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_units_details failed in {duration:.4f} seconds with error: {str(e)}")
            return {"status": 500, "message": "Internal Server Error"}

    @http.route('/get_unit_information_users', type='json', auth='user', methods=['POST'])
    def get_unit_information(self, **params):
        start_time = time.time()
        try:
            unit_name = params.get('unit')
            _logger.info(f"Unit Name: {unit_name}")

            users = request.env['res.users'].sudo().search([('unit_name', '=', unit_name)])

            if not users:
                duration = time.time() - start_time
                _logger.info(f"get_unit_information completed in {duration:.4f} seconds with error: User not found")
                return {"status": 404, "message": "User not found"}

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

            duration = time.time() - start_time
            total_users = sum(len(lst) for lst in user_names.values())
            _logger.info(f"get_unit_information completed successfully in {duration:.4f} seconds for unit: {unit_name}, total users: {total_users}")
            return user_names
        except Exception as e:
            duration = time.time() - start_time
            _logger.error(f"get_unit_information failed in {duration:.4f} seconds with error: {str(e)}")
            return {"status": 500, "message": "Internal Server Error"}