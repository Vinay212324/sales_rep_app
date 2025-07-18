/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

console.log("✅ Dashboard JS loaded");

export class SelfDashboardManagerSalesRep extends Component {
    static template = "sale_repo_app.SelfDashboardTemplate";
}

registry.category("actions").add("sale_repo_app.self_dashboard_manager_sales_rep", SelfDashboardManagerSalesRep);
