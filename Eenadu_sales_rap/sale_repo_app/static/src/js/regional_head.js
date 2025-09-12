/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class RegionalHeadDashboard extends Component {
    static template = "sale_repo_app.regional_head_dashboard_template";

}

registry.category("actions").add("sale_repo_app.regional_head_dashboard", RegionalHeadDashboard);