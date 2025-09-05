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