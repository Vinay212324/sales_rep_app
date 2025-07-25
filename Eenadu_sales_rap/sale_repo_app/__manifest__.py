{
    "name": "Sales REPO",
    "version": "1.0",
    "depends": ["base", "web", "web_tour"],
    "author": "Your Name",
    "category": "Custom",
    "summary": "Manage user hierarchy with OWL authentication",
    "data": [
        "security/access_group.xml",
        "security/ir.model.access.csv",
        "security/for_record_rules.xml",
        #"views/manager_dashboard_action.xml",
        "views/users_view.xml",
        "views/user_dashboard.xml",
        "views/customers_form.xml",
        "views/list_customer_form.xml",
        "views/unit_name_views.xml",
        "views/root_map_views.xml",
        "views/templates.xml",
        "views/customer_form_views.xml",
        "views/dashboard_action.xml",
        "views/fromto_rootmap_views.xml",
        "views/hide_app_menu.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "sale_repo_app/static/src/css/agent_dashboard.css",
            "sale_repo_app/static/src/js/dash.js",
            "sale_repo_app/static/src/xml/dashboard_template.xml",
            "sale_repo_app/static/src/js/hide_menu_items.js",
            "sale_repo_app/static/src/js/main.js",
        ],
        "web.assets_frontend": [
            "sale_repo_app/static/src/css/style.css",
            "sale_repo_app/static/src/css/user_dashboard.css",
            "sale_repo_app/static/src/css/customer_form_list.css",
            "sale_repo_app/static/src/css/customers_form.css",
            "sale_repo_app/static/src/js/dashboard.js",
            "sale_repo_app/static/src/js/customer_form_list.js",
            "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap"
        ]
    },
    "installable": True,
    "application": True
}
