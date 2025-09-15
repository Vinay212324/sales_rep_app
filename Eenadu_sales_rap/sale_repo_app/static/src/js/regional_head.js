/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class RegionalHeadDashboard extends Component {
    static template = "sale_repo_app.regional_head_dashboard_template";
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
        globalState: { type: Object, optional: true },
    };

    setup() {
        this.actionService = useService("action");
        this.rpc = useService("rpc");

        this.state = useState({
            user_info: {},
            circulation_incharge:{},
            unit_names: [],
            unit_details: null, // New property for unit-specific details
            loading: true,
            error: null,
            currentView: "dashboard",
            selected_unit: null,
        });

        onWillStart(async () => {
            console.log("Fetching unit details...");
            try {
                const res = await this.rpc("/get_units_details", {});
                console.log("RPC Response:", res);
                if (res && res.status === 200 && res.user) {
                    this.state.user_info = res.user;
                    this.state.unit_names = res.user.unit_name_ids; // Array of strings, e.g., ["HYD", "warangal"]
                } else if (res.status === 404) {
                    this.state.error = res.message || "User not found";
                }
                console.log("Unit Names:", this.state.unit_names);
            } catch (error) {
                this.state.error = error.message || "RPC Error";
            } finally {
                this.state.loading = false;
            }
        });
    }

    async navigateToUnit(unit) {
        console.log("Navigating to unit:", unit);
        this.state.loading = true; // Show loading state during RPC
        try {
            const res = await this.rpc("/get_unit_information_users", { unit });
            console.log("Unit Details RPC Response:", res);
            if (res && res.status === 200 && res.unit) {
                this.state.unit_details = res.unit; // Store unit-specific details
            } else if (res.status === 404) {
                this.state.error = res.message || "Unit not found";
            }
        } catch (error) {
            this.state.error = error.message || "Failed to fetch unit details";
        } finally {
            this.state.loading = false;
            this.state.currentView = "unit_detail";
            this.state.selected_unit = unit; // Unit is a string, e.g., "HYD"
            this.render(); // Trigger re-render
        }
    }

    goBack() {
        console.log("Returning to dashboard");
        this.state.currentView = "dashboard";
        this.state.selected_unit = null;
        this.state.unit_details = null; // Clear unit details
        this.state.error = null; // Clear any errors
        this.render(); // Trigger re-render
    }
}

registry.category("actions").add("sale_repo_app.regional_head_dashboard", RegionalHeadDashboard);