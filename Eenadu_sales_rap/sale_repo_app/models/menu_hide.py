from odoo import models, api
import logging
import time

_logger = logging.getLogger(__name__)

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def load_menus(self, debug):
        start_time = time.time()
        res = super().load_menus(debug)
        user = self.env.user

        # Replace with your actual Agent group ID (check XML ID)
        if user.has_group('sale_repo_app.group_agent'):
            apps_menu = self.env.ref('base.menu_apps', raise_if_not_found=False)

            if apps_menu:
                def hide_menu(menu):
                    if menu.get('id') == apps_menu.id:
                        return False
                    if 'children' in menu:
                        menu['children'] = list(filter(hide_menu, menu['children']))
                    return True

                res['children'] = list(filter(hide_menu, res['children']))

        end_time = time.time()
        duration = end_time - start_time
        _logger.info(f"Function load_menus took {duration:.2f} seconds")
        return res