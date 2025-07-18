from odoo import http
from odoo.http import request

class CustomLoginController(http.Controller):

    @http.route('/web/login', type='http', auth="none", website=True)
    def custom_login(self, **kwargs):
        if request.session.uid:
            return request.redirect('/web')  # user already logged in
        return request.render('custom_login_page_user.custom_login_template')

    @http.route('/custom/do_login', type='http', auth="none", methods=['POST'], csrf=False)
    def custom_do_login(self, **kwargs):
        login = kwargs.get('login')
        password = kwargs.get('password')
        try:
            uid = request.session.authenticate(request.db, login, password)
            if uid:
                return request.redirect('/web')  # login success
        except Exception as e:
            return request.render('custom_login_page_user.custom_login_template', {
                'error': 'Wrong username or password'
            })
