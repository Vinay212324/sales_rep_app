{ 
    "name": "Custom Login Page User", 
    "version": "16.0.1.0.0", 
    "summary": "Fully custom login page with separate template", 
    "depends": ["web","sale_repo_app"],
    "data": ["views/login_template.xml"], 
    "assets": {
        "web.assets_frontend": ["custom_login_page_user/static/src/css/login.css"]
    }, 
    "installable": True, 
    "auto_install": False 
}