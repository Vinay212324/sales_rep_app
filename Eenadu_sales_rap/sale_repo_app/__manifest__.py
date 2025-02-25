{
    "name": "Sales Repo",
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
        "views/customers_form.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "sale_repo_app/static/src/css/style.css",
            "sale_repo_app/static/src/css/user_dashboard.css",
            "sale_repo_app/static/src/js/main.js",
            "sale_repo_app/static/src/js/dashboard.js",
            'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap'

        ],
    },
    "installable": True,
    "application": True,
}
