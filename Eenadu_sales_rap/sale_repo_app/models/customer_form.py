from odoo import models, api, fields, _
from datetime import datetime, timedelta
# from odoo.exceptions import


class CustomerForm(models.Model):
    _name = 'customer.form'
    _description = 'Customer Form'

    agent_name = fields.Char(string='Agent Name')
    agent_login =fields.Char(string="Agent login")
    unit_name = fields.Char(string="Unit name")
    date = fields.Date(string='Today Date', default=fields.Date.context_today)
    time = fields.Char(string='Current Time')

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
    job_type = fields.Selection([("government_job","Government Job"),("private_job","Private Job")])
    job_type_one = fields.Selection([("central_job","Central Job"),("psu","PSU"),("state_job","State Job")])
    job_profession = fields.Char(string="Profession")
    job_designation = fields.Char(string="Job Designation")

    company_name = fields.Char(string="Company Name")
    profession = fields.Char(string="Profession")
    job_designation_one = fields.Char(string="Job Designation")
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")

