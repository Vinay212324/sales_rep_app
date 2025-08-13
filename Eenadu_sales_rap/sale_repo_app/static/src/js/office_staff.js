/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class SalesOfficeStaff extends Component {
    static template = "sale_repo_app.office_staff_dashboard_template";

    setup() {

    }


}

registry.category("actions").add("sale_repo_app.office_staff_dashboard", SalesOfficeStaff);
