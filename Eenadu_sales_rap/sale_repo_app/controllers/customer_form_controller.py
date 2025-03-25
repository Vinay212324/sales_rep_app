import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
import json
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


_logger = logging.getLogger(__name__)

class CustomerFormAPI(http.Controller):

    def _verify_api_key(self, token):

        user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)

        if not user:
            raise AccessDenied("Invalid token!")

        return {"success": "True", "user_Id":user.id, "user_login": user.login}  # Return the associated user


    @http.route('/api/customer_form', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def create_customer(self, **kwargs):
        try:
            # Extract headers
            api_key = kwargs.get('token')

            if not api_key:
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': "403"
                }

            # Validate Token
            user = self._verify_api_key(api_key)
            if not user:
                return {
                    'success': False,
                    'message': 'Invalid or expired token',
                    "code": "403"
                }



            # Extract data from request
            data = kwargs
            if data.get('job_type_one') == "Central Job":
                job_one = "central_job"
            elif data.get('job_type_one') == "PSU":
                job_one = "psu"
            elif data.get('job_type_one') == "State Job":
                job_one = "state_job"
            else:
                job_one = ""


            # Create a new customer form record
            customer = request.env['customer.form'].sudo().create({
                'agent_name': data.get('agent_name'),
                'agent_login': data.get('agent_login'),
                'unit_name': data.get('unit_name'),
                'date': data.get('date'),
                'time': data.get('time'),
                'family_head_name': data.get('family_head_name'),
                'father_name': data.get('father_name'),
                'mother_name': data.get('mother_name'),
                'spouse_name': data.get('spouse_name'),
                'house_number': data.get('house_number'),
                'street_number': data.get('street_number'),
                'city': data.get('city'),
                'pin_code': data.get('pin_code'),
                'address': data.get('address'),
                'mobile_number': data.get('mobile_number'),
                'eenadu_newspaper': data.get('eenadu_newspaper', False),
                'feedback_to_improve_eenadu_paper': data.get('feedback_to_improve_eenadu_paper'),
                'read_newspaper': data.get('read_newspaper', False),
                'current_newspaper': data.get('current_newspaper'),
                'reason_for_not_taking_eenadu_newsPaper': data.get('reason_for_not_taking_eenadu_newsPaper'),
                'reason_not_reading': data.get('reason_not_reading'),
                'free_offer_15_days': data.get('free_offer_15_days', False),
                'reason_not_taking_offer': data.get('reason_not_taking_offer'),
                'employed': data.get('employed', False),
                'job_type': data.get('job_type'),
                'job_type_one': job_one,
                'job_profession': data.get('job_profession'),
                'job_designation': data.get('job_designation'),
                'company_name': data.get('company_name'),
                'profession': data.get('profession'),
                'job_designation_one': data.get('job_designation_one'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
            })

            return {
                'success': True,
                'message': 'Customer Form created successfully',
                'customer_id': customer.id,
                "code": "200"
            }

        except Exception as e:
            return {
                'success': False,
                'message': 'Error: {}'.format(str(e)),
                'code': "403"
            }

    @http.route('/api/login', type='json', auth='public', methods=['POST'])
    def api_login(self, email, password):
        """ Authenticate user and generate API token """
        user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)

        if not user:
            raise exceptions.AccessDenied("User not found!")

        # Use `_check_credentials()` instead of `_check_password()`
        try:
            user.sudo()._check_credentials(password, {'interactive': True})
        except exceptions.AccessDenied:
            raise exceptions.AccessDenied("Invalid password!")

        # Generate token
        user.generate_token()

        return {
            'status': 'success',
            'user_id': user.id,
            'name': user.name,
            'role': user.role,
            'token': user.api_token,
            'token_expiry': user.token_expiry
        }

    @http.route('/api/logout', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def api_logout(self, token):
        """ Logout the user and clear their API token """

        try:
            user = request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)
        except exceptions.AccessDenied:
            raise exceptions.AccessDenied("Invalid token!")

        if not user:
            print(user.id)
            raise AccessDenied("Invalid token!")
            return {"code" : "403", "error" : "code is not define"}

        user.clear_token()
        print(user.id)

        return {'status': 'success', 'message': "User logged out successfully", "code": "200"}


    @http.route('/token_validation', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def tokenvalidation(self, **params):
        try:
            # Extract headers
            api_key = params.get('token')
            print(api_key,"vinayyyyughiuhihnin")

            if not api_key:
                return {
                    'success': False,
                    'message': 'Token is missing',
                    'code': "403"
                }

            # Validate Token
            user = self._verify_api_key(api_key)
            if not user:
                return {
                    'success': False,
                    'message': 'Invalid or expired token',
                    "code": "403"
            }
            else:
                return {
                    'success': True,
                    'message': 'valid token',
                    'user_login': user,
                    "code": "200"
                }




        except Exception as e:
            return {
                'success': False,
                'message': 'Error: {}'.format(str(e)),
                'code': "403"
            }

    import logging
    from odoo import http
    from odoo.http import request

    _logger = logging.getLogger(__name__)

    class CustomerFormController(http.Controller):

        @http.route('/api/customer_forms', type='json', auth='user', methods=['GET'])
        def get_customer_forms(self, **params):
            """
            Fetch customer form records based on the user login.
            """
            user_id = params.get("user_id")
            if not user_id:
                return {'error': 'User ID is required'}

            try:
                user_id = int(user_id)
                print(user_id)
            except ValueError:
                return {'error': 'Invalid User ID'}

            # Fetch user details
            user = request.env['res.users'].sudo().browse(user_id)
            if not user.exists():
                return {'error': 'User not found'}

            agent_login = user.login  # Get the login of the user

            _logger.info(f"Fetching records for agent login: {agent_login}")

            # Debugging: Check if any records exist at all
            all_records = request.env['customer.form'].sudo().search([])
            _logger.info(f"Total Customer Forms: {len(all_records)}")

            # Print all records to check agent_login values
            for record in all_records:
                _logger.info(f"Record ID: {record.id}, Agent Login: {record.agent_login}")

            # Check if `agent_login` is a Many2one relation instead of a Char field
            customer_forms = request.env['customer.form'].sudo().search([('agent_login', '=', agent_login)])
            if not customer_forms:
                _logger.warning(f"No records found for agent_login: {agent_login}")

            # Prepare the result
            result = [{
                'id': record.id,
                'agent_name': record.agent_name,
                'agent_login': record.agent_login,
                'unit_name': record.unit_name,
                'date': record.date,
                'time': record.time,
                'family_head_name': record.family_head_name,
                'father_name': record.father_name,
                'mother_name': record.mother_name,
                'spouse_name': record.spouse_name,
                'house_number': record.house_number,
                'street_number': record.street_number,
                'city': record.city,
                'pin_code': record.pin_code,
                'address': record.address,
                'mobile_number': record.mobile_number,
                'eenadu_newspaper': record.eenadu_newspaper,
                'feedback_to_improve_eenadu_paper': record.feedback_to_improve_eenadu_paper,
                'read_newspaper': record.read_newspaper,
                'current_newspaper': record.current_newspaper,
                'reason_for_not_taking_eenadu_newsPaper': record.reason_for_not_taking_eenadu_newsPaper,
                'reason_not_reading': record.reason_not_reading,
                'free_offer_15_days': record.free_offer_15_days,
                'reason_not_taking_offer': record.reason_not_taking_offer,
                'employed': record.employed,
                'job_type': record.job_type,
                'job_type_one': record.job_type_one,
                'job_profession': record.job_profession,
                'job_designation': record.job_designation,
                'company_name': record.company_name,
                'profession': record.profession,
                'job_designation_one': record.job_designation_one,
                'latitude': record.latitude,
                'longitude': record.longitude,
            } for record in customer_forms]

            return {'records': result}






