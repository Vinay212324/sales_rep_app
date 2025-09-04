/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { sharedStore } from "./dashboard";
import { useStore } from "@odoo/owl";

export class SearchDashboard extends Component {
    static template = "sale_repo_app.search_dashboard_template";

    setup() {
        this.store = useStore(() => sharedStore);
    }

    updated() {
        if (this.store.triggerFunction) {
            this.myFunctionInB();
        }
    }

    myFunctionInB() {
        alert("Triggered in Search Dashboard! Message = " + this.store.message);
    }
}

registry.category("actions").add(
    "sale_repo_app.search_dashboard_action",
    SearchDashboard
);
