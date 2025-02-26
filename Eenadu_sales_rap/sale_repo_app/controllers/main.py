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




class ControllerA(http.Controller):
    @http.route('/web/login', type='http', auth='public', website=True)
    def controller_a(self, **kw):
        return redirect('/lin')

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


    @http.route('/web/session/authenticate', type='json', auth="none", csrf=False, cors="*")
    def authenticate(self, login, password):
        db = "sale_rep_db"
        try:
            # Validate database access
            if not http.db_filter([db]):
                raise AccessError("Database not found")

            # Authenticate with session validation
            uid = request.session.authenticate(db, login, password)
            if not uid:
                _logger.error("Authentication failed for %s@%s", login, db)
                return {'error': 'Invalid credentials', 'code': 401}

            # Initialize secure environment
            request.session.db = db
            env = request.env(user=uid)

            # Generate API key
            try:
                api_key = env['res.users.apikeys']._generate(
                    name=f"SessionKey_{uuid.uuid4()}",
                    scope='rpc',
                    user_id=uid
                )
            except Exception as e:
                _logger.warning("Cryptographic failure, using HMAC fallback: %s", str(e))
                api_key = hmac.new(
                    key=b'secret_key',
                    msg=str(uid).encode(),
                    digestmod=hashlib.sha256
                ).hexdigest()  # Corrected hmac usage

            # Fetch expiration date if available
            expiration = None
            apikey_record = env['res.users.apikeys'].search([('user_id', '=', uid)], limit=1)
            if apikey_record and hasattr(apikey_record, 'expiration_date'):
                expiration = apikey_record.expiration_date

            user = request.env.user
            role = ""
            if user.has_group('sale_repo_app.agent_group'):
                role = "agent_level1"
            elif user.has_group('sale_repo_app.unit_manager_group'):
                role = "level2"
            elif user.has_group('sale_repo_app.region_head_group'):
                role = 'level3'
            elif user.has_group('sale_repo_app.circulation_head_group'):
                role = "level4"
            else:
                role = "No acs"

            # Commit transaction
            env.cr.commit()

            return {
                'user_id': uid,
                'api_key': api_key,
                'role_Le_gr': role,
                'role': user.role,
                'unit': user.unit_name,
                'expiration': expiration  # Set expiration if available
            }

        except AccessDenied as e:
            _logger.warning("Access denied for %s: %s", login, str(e))
            return {'error': 'Authentication failed', 'code': 403}

        except Exception as e:
            _logger.exception("Critical authentication failure")
            return {'error': str(e), 'code': 500}








    @http.route('/web/session/user_creation_for_sales_rep', type='json', auth='none', csrf=False, cors="*")
    def user_creation(self, **kw):
        _logger = logging.getLogger(__name__)  # Ensure proper logging
        try:
            # Authentication check
            token = kw.get('token')
            if not token:
                return {'error': 'Authentication token required', 'code': 401}  # Fixed indexing error

            # API key validation
            user_id = request.env['res.users.apikeys'].sudo()._check_credentials(scope='rpc', key=token)
            if not user_id:
                return {'error': 'Invalid authentication token', 'code': 403}  # Removed invalid indexing

            # Permission check
            env = request.env(user=user_id)
            if not env.user.has_group('sale_repo_app.circulation_head_group'):
                return {'error': 'Insufficient permissions', 'code': 403}

            # Field validation
            required_fields = ['name', 'email', 'password']
            missing = [field for field in required_fields if not kw.get(field)]
            if missing:
                return {'error': f'Missing required fields: {", ".join(missing)}', 'code': 400}

            # Existing user check
            existing_user = env['res.users'].search([('login', '=', kw['email'])], limit=1)
            if existing_user:
                return {'error': 'Email already registered', 'code': 409}

            # User creation
            company = env['res.company'].search([], limit=1)
            groups = [
                env.ref('base.group_user').id,
                env.ref('base.group_erp_manager').id,
                env.ref('sale_repo_app.circulation_head_group').id
            ]

            values = {
                'name': kw['name'],
                'login': kw['email'],
                'email': kw['email'],
                'password': kw['password'],
                'role': kw['role'],
                'who_is_created_id': user_id,
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'groups_id': [(6, 0, groups)]  # Fixed group assignment syntax
            }

            new_user = env['res.users'].create(values)
            env.cr.commit()  # Consider if this is truly necessary

            return {
                'success': True,
                'user_id': new_user.id,
                'message': 'User created successfully'
            }

        except exceptions.AccessDenied as e:
            _logger.error("Access denied: %s", str(e))
            return {'error': 'Authentication failed', 'code': 403}
        except exceptions.ValidationError as e:
            _logger.error("Validation error: %s", str(e))
            return {'error': str(e), 'code': 400}
        except Exception as e:
            _logger.exception("Server error during user creation:")  # Better error logging
            return {'error': 'Internal server error', 'code': 500}







    @http.route('/web/session/creating_region_head', type='json', auth='none', csrf=False, cors="*")
    def user_creation(self, **kw):
        _logger = logging.getLogger(__name__)  # Ensure proper logging
        try:
            # Authentication check
            token = kw.get('token')
            if not token:
                return {'error': 'Authentication token required', 'code': 401}  # Fixed indexing error

            # API key validation
            user_id = request.env['res.users.apikeys'].sudo()._check_credentials(scope='rpc', key=token)
            if not user_id:
                return {'error': 'Invalid authentication token', 'code': 403}  # Removed invalid indexing

            # Permission check
            env = request.env(user=user_id)
            if not env.user.has_group('sale_repo_app.circulation_head_group'):
                return {'error': 'Insufficient permissions', 'code': 403}

            # Field validation
            required_fields = ['name', 'email', 'password']
            missing = [field for field in required_fields if not kw.get(field)]
            if missing:
                return {'error': f'Missing required fields: {", ".join(missing)}', 'code': 400}

            # Existing user check
            existing_user = env['res.users'].search([('login', '=', kw['email'])], limit=1)
            if existing_user:
                return {'error': 'Email already registered', 'code': 409}

            # User creation
            company = env['res.company'].search([], limit=1)
            groups = [
                env.ref('base.group_user').id,
                env.ref('base.group_erp_manager').id,
                env.ref('sale_repo_app.region_head_group').id
            ]

            values = {
                'name': kw['name'],
                'login': kw['email'],
                'email': kw['email'],
                'password': kw['password'],
                'role': kw['role'],
                'who_is_created_id': user_id,
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'groups_id': [(6, 0, groups)]  # Fixed group assignment syntax
            }

            new_user = env['res.users'].create(values)
            env.cr.commit()  # Consider if this is truly necessary

            return {
                'success': True,
                'user_id': new_user.id,
                'message': 'User created successfully'
            }

        except exceptions.AccessDenied as e:
            _logger.error("Access denied: %s", str(e))
            return {'error': 'Authentication failed', 'code': 403}
        except exceptions.ValidationError as e:
            _logger.error("Validation error: %s", str(e))
            return {'error': str(e), 'code': 400}
        except Exception as e:
            _logger.exception("Server error during user creation:")  # Better error logging
            return {'error': 'Internal server error', 'code': 500}  

    @http.route('/web/session/creating_unit_manager', type='json', auth='none', csrf=False, cors="*")
    def user_creation(self, **kw):
        _logger = logging.getLogger(__name__)  # Ensure proper logging
        try:
            # Authentication check
            token = kw.get('token')
            if not token:
                return {'error': 'Authentication token required', 'code': 401}  # Fixed indexing error

            # API key validation
            user_id = request.env['res.users.apikeys'].sudo()._check_credentials(scope='rpc', key=token)
            if not user_id:
                return {'error': 'Invalid authentication token', 'code': 403}  # Removed invalid indexing

            # Permission check
            env = request.env(user=user_id)
            if not env.user.has_group('sale_repo_app.region_head_group'):
                return {'error': 'Insufficient permissions', 'code': 403}

            # Field validation
            required_fields = ['name', 'email', 'password']
            missing = [field for field in required_fields if not kw.get(field)]
            if missing:
                return {'error': f'Missing required fields: {", ".join(missing)}', 'code': 400}

            # Existing user check
            existing_user = env['res.users'].search([('login', '=', kw['email'])], limit=1)
            if existing_user:
                return {'error': 'Email already registered', 'code': 409}

            # User creation
            company = env['res.company'].search([], limit=1)
            groups = [
                env.ref('base.group_user').id,
                env.ref('base.group_erp_manager').id,
                env.ref('sale_repo_app.unit_manager_group').id
            ]

            values = {
                'name': kw['name'],
                'login': kw['email'],
                'email': kw['email'],
                'password': kw['password'],
                'role': kw['role'],
                'who_is_created_id': user_id,
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'groups_id': [(6, 0, groups)]  # Fixed group assignment syntax
            }

            new_user = env['res.users'].create(values)
            env.cr.commit()  # Consider if this is truly necessary

            return {
                'success': True,
                'user_id': new_user.id,
                'message': 'User created successfully'
            }

        except exceptions.AccessDenied as e:
            _logger.error("Access denied: %s", str(e))
            return {'error': 'Authentication failed', 'code': 403}
        except exceptions.ValidationError as e:
            _logger.error("Validation error: %s", str(e))
            return {'error': str(e), 'code': 400}
        except Exception as e:
            _logger.exception("Server error during user creation:")  # Better error logging
            return {'error': 'Internal server error', 'code': 500}

    @http.route('/web/session/creating_agent', type='json', auth='none', csrf=False, cors="*")
    def user_creation(self, **kw):
        _logger = logging.getLogger(__name__)  # Ensure proper logging
        try:
            # Authentication check
            token = kw.get('token')
            if not token:
                return {'error': 'Authentication token required', 'code': 401}  # Fixed indexing error

            # API key validation
            user_id = request.env['res.users.apikeys'].sudo()._check_credentials(scope='rpc', key=token)
            if not user_id:
                return {'error': 'Invalid authentication token', 'code': 403}  # Removed invalid indexing

            # Permission check
            env = request.env(user=user_id)
            if not env.user.has_group('sale_repo_app.unit_manager_group'):
                return {'error': 'Insufficient permissions', 'code': 403}

            # Field validation
            required_fields = ['name', 'email', 'password']
            missing = [field for field in required_fields if not kw.get(field)]
            if missing:
                return {'error': f'Missing required fields: {", ".join(missing)}', 'code': 400}

            # Existing user check
            existing_user = env['res.users'].search([('login', '=', kw['email'])], limit=1)
            if existing_user:
                return {'error': 'Email already registered', 'code': 409}

            # User creation
            company = env['res.company'].search([], limit=1)
            groups = [
                env.ref('base.group_user').id,
                env.ref('base.group_erp_manager').id,
                env.ref('sale_repo_app.agent_group').id
            ]

            values = {
                'name': kw['name'],
                'login': kw['email'],
                'email': kw['email'],
                'password': kw['password'],
                'role': kw['role'],
                'who_is_created_id': user_id,
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'groups_id': [(6, 0, groups)]  # Fixed group assignment syntax
            }

            new_user = env['res.users'].create(values)
            env.cr.commit()  # Consider if this is truly necessary

            return {
                'success': True,
                'user_id': new_user.id,
                'message': 'User created successfully'
            }

        except exceptions.AccessDenied as e:
            _logger.error("Access denied: %s", str(e))
            return {'error': 'Authentication failed', 'code': 403}
        except exceptions.ValidationError as e:
            _logger.error("Validation error: %s", str(e))
            return {'error': str(e), 'code': 400}
        except Exception as e:
            _logger.exception("Server error during user creation:")  # Better error logging
            return {'error': 'Internal server error', 'code': 500}













