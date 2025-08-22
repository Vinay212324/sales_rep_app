from odoo import http
from odoo.http import request
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook

class MyMessage(http.Controller):

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
    def daily_data_excel(self, day,unic_code):
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

            for i in total_agencies:
                print(i, "vinay")
                count = request.env['customer.form'].sudo().search_count(
                    [('unit_name', '=', unit_name), ('date', '=', day_str), ('Agency', '=', i.location_name)])
                if count >= 1:
                    total_agencies_filled_custon_forms_today.append([i.phone])



            values = {
                "date": day_str,
                "unit_name": unit_name,
                "unic_code": unic_code
            }
            return http.request.render("sale_repo_app.daily_data_template", values)

        except Exception as e:
            return str(e)

    @http.route('/daily-data/pdf/<string:unic_code>',
                type='http', auth='public', website=True)
    def download_pdf(self, unic_code, **kwargs):
        """Download PDF file"""

        print("vinnnnnnnnnnnn")
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

        return request.make_response(
            pdf_data,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename="daily_data.pdf"')
            ]
        )

    @http.route('/daily-data/excel/<string:unic_code>',
                type='http', auth='public', website=True)
    def download_excel(self, unic_code, **kwargs):
        """Download Excel file"""
        buffer = BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Daily Data"
        ws.append(["Agency","date","family-head-name","age","house-number","street-number","city","pin-code","address","location-address","location-url","Start-Circulating","mobile-number","agent_name","date","time","customer-type","current-newspaper"])




        print("vinnnnnnnnnnnn")
        record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
        if not record:
            return "No data found"
        unit_name = record.unit_name
        date = record.date

        total_agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])

        total_agencies_filled_custon_forms_today = []

        for i in total_agencies:
            print(i.location_name, "vinay ", date, unit_name, date)
            count = request.env['customer.form'].sudo().search_count(
                [('unit_name', '=', unit_name), ('date', '=', date), ('Agency', '=', i.location_name)])
            print(count)
            if count >= 1:
                customer_form = request.env['customer.form'].sudo().search(
                    [('unit_name', '=', unit_name), ('date', '=', date), ('Agency', '=', i.location_name)])
                total_agencies_filled_custon_forms_today.append([customer_form])

        print(total_agencies_filled_custon_forms_today, "happy")
        for i in total_agencies_filled_custon_forms_today:
            for j in i:

                ws.append([j.Agency,j.date,j.family_head_name,j.age,j.house_number,j.street_number,j.city,j.pin_code,j.address,j.location_address,j.location_url,j.Start_Circulating,j.mobile_number,j.agent_name,date,j.time,j.customer_type,j.current_newspaper])



        # ws.append([day, city, name])

        wb.save(buffer)
        buffer.seek(0)

        return request.make_response(
            buffer.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename="daily_data.xlsx"')
            ]
        )







    @http.route(
        '/daily-data/<string:unic_code>',
        type='http',
        auth='public',
        website=True,
        csrf=False
    )
    def daily_data_agency(self,unic_code):
        print("hhhhhhhh")
        """Render daily data page"""
        try:
            print("jjjjjjjj")
            record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
            unit_name = record.unit_name
            # Ensure date is in YYYY-MM-DD format string
            try:
                print("aaaaaaaa")


            except ValueError as e:
                return str(e)

            day_str = record.date  # fallback if already string
            print("pkpkpkpk")
            record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
            if not record:
                return "No data found"
            print("jjjjjjj")
            unit_name = record.unit_name
            print(unit_name)

            total_agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])

            total_agencies_filled_custon_forms_today = []

            for i in total_agencies:
                print(i, "vinay")
                count = request.env['customer.form'].sudo().search_count(
                    [('unit_name', '=', unit_name), ('date', '=', day_str), ('Agency', '=', i.location_name)])
                if count >= 1:
                    total_agencies_filled_custon_forms_today.append([i.phone])

            values = {
                "date": day_str,
                "unit_name": unit_name,
                "unic_code": unic_code
            }
            return http.request.render("sale_repo_app.daily_data_agency_template", values)

        except Exception as e:
            return str(e)

    @http.route('/daily_data_agency/pdf/<string:unic_code>',
                type='http', auth='public', website=True)
    def download_pdf_agency(self, unic_code, **kwargs):
        """Download PDF file"""

        print("vinnnnnnnnnnnn")
        record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
        if not record:
            return "No data found"
        unit_name = record.unit_name
        date = record.date

        total_agencies = request.env['pin.location'].sudo().search([('unit_name', '=', unit_name)])

        total_agencies_filled_custon_forms_today = []

        for i in total_agencies:
            print(i.location_name, "vinay ", date, unit_name, date)
            count = request.env['customer.form'].sudo().search_count(
                [('unit_name', '=', unit_name), ('date', '=', date), ('Agency', '=', i.location_name)])
            print(count)
            if count >= 1:
                customer_form = request.env['customer.form'].sudo().search(
                    [('unit_name', '=', unit_name), ('date', '=', date), ('Agency', '=', i.location_name)])
                total_agencies_filled_custon_forms_today.append([i.location_name, customer_form])

        print(total_agencies_filled_custon_forms_today, "happy")
        for i in total_agencies_filled_custon_forms_today[0][1]:
            pass

        buffer = BytesIO()
        day = "happy"
        city = "okok"
        name = "pppp"
        p = canvas.Canvas(buffer, pagesize=letter)

        p.drawString(100, 750, "Daily Data Information")
        p.drawString(50, 720, f"Date: {day} City: {city} Name: {name}")
        p.drawString(100, 700, f"City: {city}")
        p.drawString(100, 680, f"Name: {name}")
        p.showPage()
        p.save()

        pdf_data = buffer.getvalue()
        buffer.close()

        return request.make_response(
            pdf_data,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename="daily_data.pdf"')
            ]
        )

    @http.route('/daily_data_agency/excel/<string:unic_code>',
                type='http', auth='public', website=True)
    def download_excel_agency(self, unic_code, **kwargs):
        """Download Excel file"""
        buffer = BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Daily Data"
        ws.append(["Agency", "date", "family-head-name", "age", "house-number", "street-number", "city", "pin-code",
                   "address", "location-address", "location-url", "Start-Circulating", "mobile-number"])


        print("vinnnnnnnnnnnn")
        record = request.env['message.history'].sudo().search([('unic_code', '=', unic_code)], limit=1)
        if not record:
            return "No data found"
        unit_name = record.unit_name
        date = record.date

        total_agencies = [record.agency]

        total_agencies_filled_custon_forms_today = []


        count = request.env['customer.form'].sudo().search_count(
            [('unit_name', '=', unit_name), ('date', '=', date), ('Agency', '=', record.agency)])
        print(count)
        if count >= 1:
            customer_form = request.env['customer.form'].sudo().search(
                [('unit_name', '=', unit_name), ('date', '=', date), ('Agency', '=',record.agency)])
            total_agencies_filled_custon_forms_today.append([customer_form])

        print(total_agencies_filled_custon_forms_today, "happy")
        for i in total_agencies_filled_custon_forms_today:
            for j in i:
                ws.append(
                    [j.Agency, j.date, j.family_head_name, j.age, j.house_number, j.street_number, j.city, j.pin_code,
                     j.address, j.location_address, j.location_url, j.Start_Circulating, j.mobile_number])

        # ws.append([day, city, name])

        wb.save(buffer)
        buffer.seek(0)

        return request.make_response(
            buffer.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename="daily_data.xlsx"')
            ]
        )

    # @http.route('/api/circulation_send_mes', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    # def getting_users(self, **kw):
    #     token = kw.get('token')
    #     user = self._verify_api_key(token)
    #     if not user:
    #         return {'success': False, 'message': 'Invalid or expired token', 'code': 403}
    #     unit = user.unit_name





