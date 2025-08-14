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
        '/daily-data/<string:day>/<string:city>/<string:name>',
        type='http',
        auth='public',
        website=True,
        csrf=False
    )
    def daily_data_excel(self, day, city, name):
        """Render daily data page"""
        try:
            # Ensure date is in YYYY-MM-DD format string
            try:
                day_date = datetime.strptime(day, "%Y-%m-%d").date()
                day_str = day_date.strftime('%Y-%m-%d')
            except ValueError:
                day_str = day  # fallback if already string

            values = {
                "date": day_str,
                "city": city,
                "name": name
            }
            return http.request.render("sale_repo_app.daily_data_template", values)

        except Exception as e:
            return str(e)

    @http.route('/daily-data/pdf/<string:day>/<string:city>/<string:name>',
                type='http', auth='public', website=True)
    def download_pdf(self, day, city, name, **kwargs):
        """Download PDF file"""
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, "Daily Data Information")
        p.drawString(100, 720, f"Date: {day}")
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

    @http.route('/daily-data/excel/<string:day>/<string:city>/<string:name>',
                type='http', auth='public', website=True)
    def download_excel(self, day, city, name, **kwargs):
        """Download Excel file"""
        buffer = BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Daily Data"

        ws.append(["Date", "City", "Name"])
        ws.append([day, city, name])

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





