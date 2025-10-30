from odoo import http
from odoo.http import request
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import logging
import time

_logger = logging.getLogger(__name__)

class MyMessage(http.Controller):

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

    def _verify_api_key(self, token):
        """Check if the token belongs to a valid user"""
        return request.env['res.users'].sudo().search([('api_token', '=', token)], limit=1)

    @http.route(
        '/daily-data/<string:day>/<string:unic_code>',
        type='http',
        auth='public',
        website=True,
        csrf=False
    )
    def daily_data_excel(self, day, unic_code):
        start_time = time.time()
        print("hhhhhhhh")
        """Render daily data page"""
        try:
            print("jjjjjjjj")
            record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
            unit_name = record.unit_name
            # Ensure date is in YYYY-MM-DD format string
            try:
                print("aaaaaaaa")
                day_date = datetime.strptime(day, "%Y-%m-%d").date()
                day_str = day_date.strftime('%Y-%m-%d')
                print("bbbbbbb")

            except ValueError as e:
                return str(e)

            day_str = day  # fallback if already string
            print("pkpkpkpk")
            record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
            if not record:
                return "No data found"
            print("jjjjjjj")
            unit_name = record.unit_name
            print(unit_name)

            total_agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])

            total_agencies_filled_custon_forms_today = []
            print(day_str,"hhhh")
            for i in total_agencies:
                print(i, "vinay",i.location_name)
                count = request.env['customer.form'].sudo().search_count(
                    [('unit_name', '=', unit_name), ('date', '=', day_str), ('Agency', '=', str(i.location_name)+" ")])
                if count >= 1:
                    print(count,"koooo")
                    total_agencies_filled_custon_forms_today.append([i.phone])



            values = {
                "date": day_str,
                "unit_name": unit_name,
                "unic_code": unic_code
            }
            result = http.request.render("sale_repo_app.daily_data_template", values)
            return result

        except Exception as e:
            result = str(e)
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('daily_data_excel', execution_time)

    @http.route('/daily-data/pdf/<string:unic_code>',
                type='http', auth='public', website=True)
    def download_pdf(self, unic_code, **kwargs):
        start_time = time.time()
        """Download PDF file"""

        print("vinnnnnnnnnnnn")
        try:
            record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
            if not record:
                return "No data found"
            unit_name = record.unit_name
            date = record.date

            total_agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])

            total_agencies_filled_custon_forms_today = []

            for i in total_agencies:
                print(i.location_name, "vinay ",date,unit_name,date)
                count = request.env['customer.form'].sudo().search_count(
                    [('unit_name', '=', unit_name), ('date', '=', date), ('Agency', '=', i.location_name)])
                print(count)
                if count >= 1:
                    customer_form = request.env['customer.form'].sudo().search(
                    [('unit_name', '=', unit_name), ('date', '=', date), ('Agency', '=', i.location_name)])
                    total_agencies_filled_custon_forms_today.append([i.location_name,customer_form])

            print(total_agencies_filled_custon_forms_today,"happy")
            for i in total_agencies_filled_custon_forms_today[0][1]:
                pass

            buffer = BytesIO()
            day="happy"
            city="okok"
            name="pppp"
            p = canvas.Canvas(buffer, pagesize=letter)

            p.drawString(100, 750, "Daily Data Information")
            p.drawString(50, 720, f"Date: {day} City: {city} Name: {name}")
            p.drawString(100, 700, f"City: {city}")
            p.drawString(100, 680, f"Name: {name}")
            p.showPage()
            p.save()

            pdf_data = buffer.getvalue()
            buffer.close()

            result = request.make_response(
                pdf_data,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', 'attachment; filename="daily_data.pdf"')
                ]
            )
            return result

        except Exception as e:
            _logger.error("Error in download_pdf: %s", e)
            return "Error generating PDF"
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('download_pdf', execution_time)

    @http.route('/daily-data/excel/<string:unic_code>',
                type='http', auth='public', website=True)
    def download_excel(self, unic_code, **kwargs):
        start_time = time.time()
        """Download Excel file"""
        try:
            buffer = BytesIO()
            wb = Workbook()
            ws = wb.active
            ws.title = "Daily Data"
            ws.append([
                "Agency", "date", "Customer Name", "age", "house-number", "street-number", "city", "pin-code",
                "address", "location-address", "location-url", "Start-Circulating", "mobile-number",
                "Staff Name", "date", "time", "customer-type", "current-newspaper"
            ])

            # Get record
            record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
            if not record:
                return "No data found"

            unit_name = record.unit_name
            date = record.date

            # Get agencies
            total_agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])

            # Collect customer forms: Unassigned/Empty first, then by agency
            total_agencies_filled_custon_forms_today = []

            # 1. First: Collect unassigned/empty agency forms
            # unassigned_forms = request.env['customer.form'].sudo().search([
            #     ('unit_name', '=', unit_name),
            #     ('date', '=', date),
            #     ('Agency', '=', "Other Agency ")  # Empty or null Agency
            # ])
            # for rec in unassigned_forms:
            #     total_agencies_filled_custon_forms_today.append(rec)

            # 2. Then: Collect forms by agency
            for i in total_agencies:
                customer_forms = request.env['customer.form'].sudo().search([
                    ('unit_name', '=', unit_name),
                    ('date', '=', date),
                    ('Agency', '=', str(i.location_name)+" ")
                ])
                if customer_forms:
                    # Append individual records
                    for rec in customer_forms:
                        total_agencies_filled_custon_forms_today.append(rec)

            # Write into Excel (unassigned first due to collection order)
            for j in total_agencies_filled_custon_forms_today:
                agency_value = j.Agency or 'Unassigned'  # Mark empty as 'Unassigned' in Excel
                ws.append([
                    agency_value,
                    j.date,
                    j.family_head_name,
                    j.age,
                    j.house_number,
                    j.street_number,
                    j.city,
                    j.pin_code,
                    j.address,
                    j.location_address,
                    j.location_url,
                    j.Start_Circulating,
                    j.mobile_number,
                    j.agent_name,
                    j.date,  # or `date` from message.history?
                    j.time,
                    j.customer_type,
                    j.current_newspaper
                ])

            # Save Excel
            wb.save(buffer)
            buffer.seek(0)

            result = request.make_response(
                buffer.read(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', 'attachment; filename="daily_data.xlsx"')
                ]
            )
            buffer.close()  # Close after reading
            return result

        except Exception as e:
            _logger.error("Error in download_excel: %s", e)
            return "Error generating Excel"
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('download_excel', execution_time)


    @http.route(
        '/daily-data/<string:unic_code>',
        type='http',
        auth='public',
        website=True,
        csrf=False
    )
    def daily_data_agency(self, unic_code):
        start_time = time.time()
        print("hhhhhhhh")
        """Render daily data page for specific agency"""
        try:
            print("jjjjjjjj")
            record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
            if not record:
                return "No data found"
            unit_name = record.unit_name
            day_str = str(record.date)  # Ensure date is string in YYYY-MM-DD format
            print("pkpkpkpk")
            print(unit_name)

            # Filter customer forms specifically for this agency
            customer_forms = request.env['customer.form'].sudo().search([
                ('unit_name', '=', unit_name),
                ('date', '=', day_str),
                ('Agency', '=', record.agency)
            ])
            print(f"Found {len(customer_forms)} forms for agency {record.agency}")

            values = {
                "date": day_str,
                "unit_name": unit_name,
                "unic_code": unic_code,
                "agency": record.agency,
                "customer_forms": customer_forms  # Optional: pass for template display
            }
            result = http.request.render("sale_repo_app.daily_data_agency_template", values)
            return result

        except Exception as e:
            _logger.error("Error in daily_data_agency: %s", e)
            result = str(e)
            return result
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('daily_data_agency', execution_time)

    @http.route('/daily_data_agency/pdf/<string:unic_code>',
                type='http', auth='public', website=True)
    def download_pdf_agency(self, unic_code, **kwargs):
        start_time = time.time()
        """Download PDF file for specific agency"""

        print("vinnnnnnnnnnnn")
        try:
            record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
            if not record:
                return "No data found"
            unit_name = record.unit_name
            date = record.date
            agency = record.agency

            # Filter customer forms for this agency
            customer_forms = request.env['customer.form'].sudo().search([
                ('unit_name', '=', unit_name),
                ('date', '=', date),
                ('Agency', '=', agency)
            ])

            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)

            # Header
            p.drawString(100, 750, "Daily Data Information - Agency")
            p.drawString(50, 720, f"Date: {date} | Unit: {unit_name} | Agency: {agency}")
            y_position = 700

            # List forms
            p.drawString(100, y_position, "Customer Forms:")
            y_position -= 20
            for form in customer_forms:
                p.drawString(100, y_position,
                             f"- {form.family_head_name} ({form.age}), Mobile: {form.mobile_number}, Address: {form.address[:50]}...")
                y_position -= 20
                if y_position < 50:  # New page if needed
                    p.showPage()
                    y_position = 750

            p.showPage()
            p.save()

            pdf_data = buffer.getvalue()
            buffer.close()

            result = request.make_response(
                pdf_data,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename="daily_data_{agency}.pdf"')
                ]
            )
            return result

        except Exception as e:
            _logger.error("Error in download_pdf_agency: %s", e)
            return "Error generating PDF"
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('download_pdf_agency', execution_time)

    @http.route('/daily_data_agency/excel/<string:unic_code>',
                type='http', auth='public', website=True)
    def download_excel_agency(self, unic_code, **kwargs):
        start_time = time.time()
        """Download Excel file for specific agency"""
        try:
            buffer = BytesIO()
            wb = Workbook()
            ws = wb.active
            ws.title = "Daily Data Agency"
            ws.append([
                "Agency", "date", "Customer Name", "age", "house-number", "street-number",
                "city", "pin-code", "address", "location-address", "location-url",
                "Start-Circulating", "mobile-number", "Staff Name", "time", "customer-type", "current-newspaper"
            ])

            record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
            if not record:
                return "No data found"

            unit_name = record.unit_name
            date = record.date
            agency = record.agency

            # Filter customer forms for this agency
            customer_forms = request.env['customer.form'].sudo().search([
                ('unit_name', '=', unit_name),
                ('date', '=', date),
                ('Agency', '=', str(agency)+" ")
            ])

            for j in customer_forms:
                ws.append([
                    j.Agency,
                    j.date,
                    j.family_head_name,
                    j.age,
                    j.house_number,
                    j.street_number,
                    j.city,
                    j.pin_code,
                    j.address,
                    j.location_address,
                    j.location_url,
                    j.Start_Circulating,
                    j.mobile_number,
                    j.agent_name,
                    j.time,
                    j.customer_type,
                    j.current_newspaper
                ])

            # Save workbook
            wb.save(buffer)
            buffer.seek(0)

            result = request.make_response(
                buffer.read(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename="daily_data_{agency}.xlsx"')
                ]
            )
            buffer.close()  # Close after reading
            return result

        except Exception as e:
            _logger.error("Error in download_excel_agency: %s", e)
            return "Error generating Excel"
        finally:
            execution_time = time.time() - start_time
            self._update_function_timing('download_excel_agency', execution_time)


    # @http.route('/api/circulation_send_mes', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    # def getting_users(self, **kw):
    #     token = kw.get('token')
    #     user = self._verify_api_key(token)
    #     if not user:
    #         return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
    #     unit = user.unit_name