# -*- coding: utf-8 -*-
from odoo import api, fields, models
# controllers/quiz_controller.py
from odoo import http
from odoo.http import request, Response
import json
from odoo.exceptions import ValidationError
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import operator

import smtplib
import ssl
from email.mime.text import MIMEText
import logging


from werkzeug.urls import url_encode
from datetime import timedelta

import jwt
import datetime
import json
import logging
from odoo import http, _, exceptions
import smtplib
import string
import random
from email.mime.text import MIMEText
from odoo import http
import odoo
import odoo.modules.registry

from odoo.modules import module
from odoo.exceptions import AccessError, UserError, AccessDenied

from odoo import http
from odoo.http import request
import base64
import secrets
from odoo.tools.translate import _


import logging
import uuid
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.exceptions import AccessError, AccessDenied
from odoo.tools import hmac
import base64

import logging
import uuid
import hmac
import hashlib
from odoo import http
from odoo.http import request

from odoo.exceptions import AccessDenied, AccessError
from cryptography.fernet import InvalidToken

from werkzeug.utils import redirect
_logger = logging.getLogger(__name__)
SECRET_KEY = 'your_secret_key'



#
# class ControllerA(http.Controller):
#     @http.route('/web/login', type='http', auth='public', website=True)
#     def controller_a(self, **kw):
#         return redirect('/lin')

class UserPortal(http.Controller):
    @http.route('/lin', type='http', auth='public')
    def user_portal(self, **kwargs):
        return http.request.render("sale_repo_app.user_portal_template")

    @http.route('/dashboard', type='http', auth='public')
    def dashboard(self, **kw):
        if not request.session.uid:
            print("kkdkmjljjjojffffffffff")
     # Redirect if not logged in
        print("llllllllllllllll")
        return http.request.render('sale_repo_app.user_dashboard_template')

    @http.route('/customers_form', type='http', auth='public')
    def customers_form(self, **kwargs):

        return http.request.render("sale_repo_app.customers_form")

    @http.route(['/someurl'], type='http', auth="public", methods=["POST"], csrf=False)
    def shop(self, **post):
        print("Received POST data:", post)
        return Response("Forbidden", status="700")  # Use 403 for forbidden responses

    @http.route('/customer_form_list', type='http', auth='public')
    def customer_form_list(self):
        return http.request.render("sale_repo_app.list_customer_form")



    @http.route('/web/session/authenticate', type='json', auth="none", csrf=False, cors="*")
    def authenticate(self, login, password):
        """ Authenticate user and generate API token with expiration time. """
        db = request.session.db or "sale_rep_db"

        try:
            # ✅ Validate database access
            if db not in http.db_filter([db]):
                raise AccessDenied("Database not found")

            # ✅ Authenticate user session
            uid = request.session.authenticate(db, login, password)
            if not uid:
                _logger.error("Authentication failed for %s@%s", login, db)
                return {'error': 'Invalid credentials', 'code': "403"}

            # ✅ Initialize environment
            request.session.db = db
            env = request.env(user=uid)

            # ✅ Fetch user from `res.users`
            user = env['res.users'].sudo().search([('login', '=', login)], limit=1)
            print(user)
            if not user:
                raise AccessDenied("User not found!")

            # ✅ Validate Password using `_check_credentials`
            try:
                # Validate user's password
                user.sudo()._check_credentials(password, {'interactive': True})
            except exceptions.AccessDenied:
                raise exceptions.AccessDenied("Invalid password!")

            # ✅ Generate API token using `generate_token()`
            user.sudo().generate_token()

            # ✅ Fetch API key expiration date
            expiration = user.token_expiry if hasattr(user, 'token_expiry') else None


            # ✅ Determine user role
            role = "No access"
            if user.has_group('sale_repo_app.agent_group'):
                role = "agent"
            elif user.has_group('sale_repo_app.office_staff_group'):
                role = "Office_staff"
            elif user.has_group('sale_repo_app.unit_manager_group'):
                role = "unit_manager"
            elif user.has_group('sale_repo_app.region_head_group'):
                role = "region_head"
            elif user.has_group('sale_repo_app.circulation_head_group'):
                role = "circulation_head"

            # ✅ Commit transaction
            env.cr.commit()

            return {
                'status': 'success',
                'user_id': uid,
                'name':user.name,
                'api_key': user.api_token,
                'role_Le_gr': role,
                'role': user.role or "Unknown",  # Prevent NoneType error
                'unit': user.unit_name or "Unknown",
                'aadhar_number': user.aadhar_number,
                'pan_number': user.pan_number,
                'state': user.state,
                'phone': user.phone,

                'expiration': expiration,  # Set expiration if available
                'code': "200"
            }

        except AccessDenied as e:
            _logger.warning("Access denied for %s: %s", login, str(e))
            return {'error': 'Authentication failed', 'code': "403"}

        except Exception as e:
            _logger.exception("Critical authentication failure")
            return {'error': str(e), 'code': "403"}

    @http.route('/sales_rep_user_creation', type='json', auth='none', methods=["POST"], csrf=False, cors="*")
    def user_creation(self, **kw):
        _logger = logging.getLogger(__name__)  # Ensure proper logging
        try:
            # Authentication check
            token = kw.get('token')
            if not token:
                return {'error': 'Authentication token required', 'code': "403"}

            # API key validation
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
            if not user:
                return {'error': 'Invalid authentication token', 'code': "403"}

            # Permission check
            env = request.env(user=user)
            if (env.user.has_group('sale_repo_app.circulation_head_group')) or \
                    (env.user.has_group('sale_repo_app.region_head_group')) or \
                    (env.user.has_group('sale_repo_app.unit_manager_group')) or\
                    (env.user.has_group('sale_repo_app.office_staff_group')) or\
                    (env.user.has_group('sale_repo_app.admin_group')) :
                if env.user.has_group('sale_repo_app.admin_group'):
                    valid_roles = ["admin","circulation_head", "region_head", "unit_manager","Office_staff","circulation_incharge", "agent"]
                elif env.user.has_group('sale_repo_app.circulation_head_group'):
                    valid_roles = ["circulation_head", "region_head","segment_incharge", "unit_manager","Office_staff","circulation_incharge", "agent"]
                elif env.user.has_group('sale_repo_app.region_head_group'):
                    valid_roles = ["region_head", "unit_manager","segment_incharge","Office_staff","circulation_incharge", "agent"]
                elif env.user.has_group('sale_repo_app.unit_manager_group'):
                    valid_roles = ["unit_manager","Office_staff","segment_incharge","circulation_incharge", "agent"]
                elif env.user.has_group('sale_repo_app.office_staff_group'):
                    valid_roles = ["Office_staff", "agent"]

                # Role validation
                if kw.get("role") not in valid_roles:
                    return {'error': 'Role is not valid for this user', 'code': "403"}

            else:
                return {'error': 'Insufficient permissions', 'code': "403"}

            # Field validation
            required_fields = ['name', 'status', 'email', 'phone', 'password', 'role', 'unit_name','state']
            missing = [field for field in required_fields if not kw.get(field)]
            if missing:
                return {'error': f'Missing required fields: {", ".join(missing)}', 'code': "400"}

            # Existing user check
            existing_user = env['res.users'].search([('login', '=', kw['email'])], limit=1)
            if existing_user:
                return {'error': 'Email already registered', 'code': "409"}

            # Assign groups based on role
            try:
                if kw.get("role") == "circulation_head":
                    groups = [
                        env.ref('base.group_user').id,
                        env.ref('base.group_erp_manager').id,
                        env.ref('sale_repo_app.circulation_head_group').id
                    ]
                elif kw.get("role") == "region_head":
                    groups = [
                        env.ref('base.group_user').id,
                        env.ref('base.group_erp_manager').id,
                        env.ref('sale_repo_app.region_head_group').id
                    ]
                elif kw.get("role") in ["unit_manager","segment_incharge","circulation_incharge"]:
                    groups = [
                        env.ref('base.group_user').id,
                        env.ref('base.group_erp_manager').id,
                        env.ref('sale_repo_app.unit_manager_group').id
                    ]
                elif kw.get("role") == "agent":
                    groups = [
                        env.ref('base.group_user').id,
                        env.ref('base.group_erp_manager').id,
                        env.ref('sale_repo_app.agent_group').id
                    ]
                elif kw.get("role") == "admin":
                    groups = [
                        env.ref('base.group_user').id,
                        env.ref('base.group_erp_manager').id,
                        env.ref('sale_repo_app.agent_group').id,
                        env.ref('sale_repo_app.admin_group').id
                    ]
                elif kw.get("role") == "Office_staff":
                    groups = [
                        env.ref('base.group_user').id,
                        env.ref('base.group_erp_manager').id,
                        env.ref('sale_repo_app.office_staff_group').id
                    ]
                else:
                    return {'error': 'Role is not valid', 'code': "403"}
            except Exception as e:
                _logger.error(f"Error resolving group references: {e}")
                return {'error': 'Group reference not found', 'code': "500"}

            # Create the user
            company = env['res.company'].search([], limit=1)
            values = {
                'name': kw['name'],
                'login': kw['email'],
                'email': kw['email'],
                'unit_name' : kw['unit_name'],
                'password': kw['password'],
                'create_uid': user.id,  # Use 'create_uid' to store the creator's user ID
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'role': kw['role'],
                'aadhar_number': kw['aadhar_number'] if (kw['aadhar_number']) else "" ,
                'pan_number': kw['pan_number'] if (kw['pan_number']) else "",
                'state': kw['state'],
                'states': kw['states'],
                'phone': kw['phone'],
                'aadhar_base64': kw['aadhar_base64'] if (kw['aadhar_base64']) else "",
                'Pan_base64': kw['Pan_base64'] if (kw['Pan_base64']) else "",


                'groups_id': [(6, 0, groups)]  # Group assignment based on role
            }

            _logger.info(f"Creating new user with values: {values}")

            try:
                new_user = env['res.users'].sudo().create(values)
                _logger.info(f"New user created with ID: {new_user.id}")
            except Exception as e:
                _logger.error(f"Error during user creation: {e}")
                raise  # Re-raise the exception to propagate it

            return {
                'success': True,
                'user_id': new_user.id,
                'message': 'User created successfully'
            }

        except exceptions.AccessDenied as e:
            _logger.error("Access denied: %s", str(e))
            return {'error': 'Authentication failed', 'code': "403"}
        except exceptions.ValidationError as e:
            _logger.error("Validation error: %s", str(e))
            return {'error': str(e), 'code': "400"}
        except Exception as e:
            _logger.exception("Server error during user creation: %s", str(e))  # Better error logging
            return {'success': 'user created successfully', 'code': "200"}


        except exceptions.ValidationError as e:
            _logger.error("Validation error: %s", str(e))
            return {'error': str(e), 'code': "400"}
        except Exception as e:
            _logger.exception("Server error during user creation: %s", str(e))
            return {'error': 'Internal server error', 'code': "500"}

    #
    # @http.route('/sales_rep_user_list', type='json', auth='none', methods=["POST"], csrf=False, cors="*")
    # def user_list(self, **kw):
    #     pass