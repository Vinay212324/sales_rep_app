{
    "name": "Sales REPO",
    "version": "1.0",
    "depends": ["base", "web"],  # Base module + OWL support
    "author": "Your Name",
    "category": "Custom",
    "summary": "Manage user hierarchy with OWL authentication",
    "data": [
        "security/access_group.xml",
        "security/ir.model.access.csv",
        "views/templates.xml",
        "views/users_view.xml",
        "views/user_dashboard.xml",
        "views/customers_form.xml",
        "views/list_customer_form.xml",
        'views/unit_name_views.xml',
        'views/customer_form_views.xml'
    ],
    "assets": {
        "web.assets_frontend": [
            "sale_repo_app/static/src/css/style.css",
            "sale_repo_app/static/src/css/user_dashboard.css",
            "sale_repo_app/static/src/css/customer_form_list.css",
            "sale_repo_app/static/src/css/customers_form.css",
            "sale_repo_app/static/src/js/main.js",
            "sale_repo_app/static/src/js/dashboard.js",
            'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap',
            "sale_repo_app/static/src/js/customer_form_list.js"

        ],
    },
    "installable": True,
    "application": True,
}
