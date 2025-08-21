/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

class UnitManagerDashboardUM extends Component {
    static template = "sale_repo_app.UnitManagerDashboardUM";
}

// Register the dashboard as a client action
registry.category("actions").add(
    "sale_repo_app.unit_manager_dashboard_um",
    UnitManagerDashboardUM
);
