from odoo import models, api, fields, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)
import requests

class CustomerForm(models.Model):
    _name = 'customer.form'
    _description = 'Customer Form'

    agent_name = fields.Char(string='Agent Name')
    root_name = fields.Char(string="Root Map")
    agent_login = fields.Char(string="Agent login")
    unit_name = fields.Char(string="Unit name")
    date = fields.Date(string='Form Filled Date', default=fields.Date.context_today)
    time = fields.Char( string='Current Time', default=lambda self: datetime.now().strftime('%H:%M') )

    # Family Details
    family_head_name = fields.Char(string="Family Head Name")
    father_name = fields.Char(string="Father's Name")
    mother_name = fields.Char(string="Mother's Name")
    spouse_name = fields.Char(string="Spouse's Name")

    # Address Details
    house_number = fields.Char(string='House Number')
    street_number = fields.Char(string='Street Number')
    city = fields.Char(string='City')
    pin_code = fields.Char(string='Pin Code')
    address = fields.Text(string='Address')
    mobile_number = fields.Char(string='Mobile Number')

    # Newspaper Details
    eenadu_newspaper = fields.Boolean(string='Eenadu Newspaper')
    feedback_to_improve_eenadu_paper = fields.Text(string="Feedback to Improve Eenadu Paper")
    read_newspaper = fields.Boolean(string='Read Newspaper')
    current_newspaper = fields.Char(string="Current Newspaper")
    reason_for_not_taking_eenadu_newsPaper = fields.Text(string="Reason for not taking Eenadu Newspaper")
    reason_not_reading = fields.Text(string='Reason for Not Reading Newspaper')
    free_offer_15_days = fields.Boolean(string='15 Days Free Eenadu Offer')
    reason_not_taking_offer = fields.Text(string='Reason for Not Taking Free Offer')

    # Employment Details
    employed = fields.Boolean(string='Employed')
    job_type = fields.Selection([
        ("government_job", "Government Job"),
        ("private_job", "Private Job")
    ])

    job_type_one = fields.Selection([
        ("central_job", "Central Job"),
        ("psu", "PSU"),
        ("state_job", "State Job")
    ])

    job_profession = fields.Char(string="Profession")
    job_designation = fields.Char(string="Job Designation")

    job_working_state = fields.Char(string="working state")
    job_working_location = fields.Char(string="working location")
    job_location_landmark = fields.Char(string="job_location_landMark")

    company_name = fields.Char(string="Company Name")
    profession = fields.Char(string="Profession")
    job_designation_one = fields.Char(string="Job Designation")
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    location_address = fields.Char(string="Address")
    location_url = fields.Char(string='Location Link')
    face_base64 = fields.Binary(string="Landmaek Photo")
    for_consider = fields.Char(string="May Consider")
    shift_to_EENADU = fields.Boolean()
    Willing_to_Shift_to_EENADU = fields.Boolean()
    Start_Circulating = fields.Char(string="Start_Circulating")
    Agency = fields.Char(string="Agency")
    age = fields.Char()
    customer_type = fields.Char()
    occupation =  fields.Char()
    def _get_lat_lon_from_ip(self):
        try:
            response = requests.get('http://ip-api.com/json/')
            data = response.json()
            if data.get('status') == 'success':
                return str(data.get('lat')), str(data.get('lon'))
        except Exception as e:
            _logger.warning("Geo IP fetch failed: %s", e)
        return "0.0", "0.0"  # fallback values as string (since you use Char)

    @api.model
    def create(self, vals):
        if not vals.get('latitude') or not vals.get('longitude'):
            lat, lon = self._get_lat_lon_from_ip()
            vals['latitude'] = lat
            vals['longitude'] = lon
        # Generate Google Maps link
        if vals.get('latitude') and vals.get('longitude'):
            lat = vals.get('latitude')
            lon = vals.get('longitude')
            vals['location_url'] = f"https://www.google.com/maps?q={lat},{lon}"
        return super(CustomerForm, self).create(vals)

    def write(self, vals):
        if not vals.get('latitude') or not vals.get('longitude'):
            lat, lon = self._get_lat_lon_from_ip()
            vals['latitude'] = lat
            vals['longitude'] = lon
        # Generate Google Maps link
        lat = vals.get('latitude') or self.latitude
        lon = vals.get('longitude') or self.longitude
        if lat and lon:
            vals['location_url'] = f"https://www.google.com/maps?q={lat},{lon}"
        return super(CustomerForm, self).write(vals)

    @api.model
    def create(self, vals):
        # Auto-fill agent-related fields if not provided
        user = self.env.user
        if not vals.get('agent_name'):
            vals['agent_name'] = user.name
        if not vals.get('agent_login'):
            vals['agent_login'] = user.login
        if not vals.get('unit_name'):
            vals['unit_name'] = user.unit_name # or custom field if you have unit info elsewhere

        # Auto-fill current time if not provided
        if not vals.get('time'):
            vals['time'] = datetime.now().strftime('%H:%M:%S')

        # Auto-fill latitude/longitude if not given
        if not vals.get('latitude') or not vals.get('longitude'):
            lat, lon = self._get_lat_lon_from_ip()
            vals['latitude'] = lat
            vals['longitude'] = lon

        # Generate Google Maps link
        if vals.get('latitude') and vals.get('longitude'):
            lat = vals.get('latitude')
            lon = vals.get('longitude')
            vals['location_url'] = f"https://www.google.com/maps?q={lat},{lon}"

        return super(CustomerForm, self).create(vals)

# @api.model
# def create(self, vals):
#     user = self.env.user
#
#     # Auto-fill agent info
#     vals.setdefault('agent_name', user.name)
#     vals.setdefault('agent_login', user.login)
#     vals.setdefault('unit_name', user.company_id.name)
#
#     # Auto-fill current time if not already set
#     vals.setdefault('time', datetime.now().strftime('%H:%M:%S'))
#
#     # Auto-fill latitude and longitude if not provided
#     if not vals.get('latitude') or not vals.get('longitude'):
#         lat, lon = self._get_lat_lon_from_ip()
#         vals['latitude'] = lat
#         vals['longitude'] = lon
#
#     # Auto-fill Google Maps URL
#     if vals.get('latitude') and vals.get('longitude'):
#         vals['location_url'] = f"https://www.google.com/maps?q={vals['latitude']},{vals['longitude']}"
#
#     return super(CustomerForm, self).create(vals)
    @api.model
    def default_get(self, fields_list):
        """Auto-fill fields when opening the form"""
        res = super().default_get(fields_list)
        user = self.env.user
        if 'agent_name' in fields_list:
            res['agent_name'] = user.name
        if 'agent_login' in fields_list:
            res['agent_login'] = user.login
        if 'unit_name' in fields_list:
            res['unit_name'] = user.unit_name
        if 'time' in fields_list:
            res['time'] = datetime.now().strftime('%H:%M')
        if 'latitude' in fields_list or 'longitude' in fields_list or 'location_url' in fields_list:
            lat, lon = self._get_lat_lon_from_ip()
            res['latitude'] = lat
            res['longitude'] = lon
            res['location_url'] = f"https://www.google.com/maps?q={lat},{lon}"
        return res


    @api.model
    def get_customer_stats(self, start_date=False, end_date=False, unit_name=False):
        """
        Returns a dictionary containing:
            - total_forms: total number of customer.form records
            - unique_users: number of unique agent_login values
            - forms: the actual recordset (to use in another model/report)
        Filtered by date range and/or unit.
        """

        domain = []

        # Date filter logic
        if start_date and end_date:
            domain += [('date', '>=', start_date), ('date', '<=', end_date)]
        elif start_date:  # only start_date → single day
            domain.append(('date', '=', start_date))
        elif end_date:  # only end_date → single day
            domain.append(('date', '=', end_date))

        # Unit filter
        if unit_name:
            domain.append(('unit_name', '=', unit_name))

        # Search records
        forms = self.search(domain)

        # Count total forms
        total_forms = len(forms)

        # Count unique agent_logins
        unique_users = len(set(forms.mapped('agent_login')))

        # Return as dictionary including recordset for use in other models
        return {
            "total_forms": total_forms,
            "unique_users": unique_users,
            "forms": forms,  # the recordset
        }
