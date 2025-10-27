from odoo import models, api

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def load_menus(self, debug):
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

        return res
