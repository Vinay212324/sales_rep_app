from odoo import http
from odoo.http import request
from odoo.tools.translate import _

class StaffController(http.Controller):
    @http.route('/sale_repo_app/load_work_sessions', type='json', auth='user')
    def load_work_sessions(self, user_id):
        try:
            if not user_id or not isinstance(user_id, int):
                return {'error': 'Invalid user_id parameter.'}

            domain = [('user_id', '=', user_id)]

            return {
                'type': 'ir.actions.act_window',
                'name': _(f"Work Sessions for User ID {user_id}"),
                'res_model': 'work.session',
                'view_mode': 'tree,form',
                'domain': domain,
                'context': {'edit': 0, 'create': 0},
                'views': [
                    [False, 'tree'],
                    [False, 'form']
                ],
            }
        except Exception as e:
            return {'error': str(e)}



from odoo import http
from odoo.http import request
import pytz

class WorkSessionController(http.Controller):

    @http.route('/convert_sessions_to_ist', type='http', auth='user')
    def convert_sessions_to_ist(self, **kwargs):
        ist = pytz.timezone("Asia/Kolkata")
        sessions = request.env['work.session'].sudo().search([])
        count = 0

        for rec in sessions:
            updated_vals = {}
            if rec.start_time:
                dt = rec.start_time.replace(tzinfo=pytz.UTC).astimezone(ist).replace(tzinfo=None)
                updated_vals['start_time'] = dt
            if rec.end_time:
                dt = rec.end_time.replace(tzinfo=pytz.UTC).astimezone(ist).replace(tzinfo=None)
                updated_vals['end_time'] = dt
            if updated_vals:
                rec.write(updated_vals)
                count += 1

        return f"✅ {count} Work Session records converted to IST."

    @http.route('/revert_sessions_to_utc', type='http', auth='user')
    def revert_sessions_to_utc(self, **kwargs):
        ist = pytz.timezone("Asia/Kolkata")
        sessions = request.env['work.session'].sudo().search([])
        count = 0

        for rec in sessions:
            updated_vals = {}
            if rec.start_time:
                # Treat stored value as naive UTC but actually it's IST → convert back to UTC
                dt = rec.start_time.replace(tzinfo=ist).astimezone(pytz.UTC).replace(tzinfo=None)
                updated_vals['start_time'] = dt
            if rec.end_time:
                dt = rec.end_time.replace(tzinfo=ist).astimezone(pytz.UTC).replace(tzinfo=None)
                updated_vals['end_time'] = dt
            if updated_vals:
                rec.write(updated_vals)
                count += 1

        return f"♻️ {count} Work Session records reverted back to UTC."