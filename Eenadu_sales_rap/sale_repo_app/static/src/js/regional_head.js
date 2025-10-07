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
        this.orm = useService("orm");
        this.rpc = useService("rpc");

        const STORAGE_KEY = 'regional_head_dashboard_state';

        this.state = useState({
            user_info: {},
            circulation_incharge: {},
            unit_names: [],
            unit_details: null,
            loading: true,
            error: null,
            currentView: "dashboard",
            selected_unit: null,
            selectedUserId: null,
        });

        // Load persisted state from localStorage
        const savedState = localStorage.getItem(STORAGE_KEY);
        if (savedState) {
            try {
                const parsed = JSON.parse(savedState);
                // Merge persisted state, but keep loading and error as default
                Object.assign(this.state, {
                    ...parsed,
                    loading: true,
                    error: null,
                });
            } catch (e) {
                console.warn("Failed to load saved state:", e);
            }
        }

        onWillStart(async () => {
            console.log("Fetching unit details...");
            try {
                const res = await this.rpc("/get_units_details", {});
                console.log("RPC Response:", res);
                if (res && res.status === 200 && res.user) {
                    this.state.user_info = res.user;
                    this.state.unit_names = res.user.unit_name_ids || [];
                    // If unit_names changed, update persisted state
                    if (this.state.unit_names.length !== (savedState ? JSON.parse(savedState).unit_names?.length || 0 : 0)) {
                        this.saveState();
                    }
                } else {
                    this.state.error = res.message || "User not found";
                }
                console.log("Unit Names:", this.state.unit_names);
            } catch (error) {
                this.state.error = error.message || "Failed to fetch units";
            } finally {
                this.state.loading = false;
                this.saveState();
            }
        });
    }

    saveState() {
        const STORAGE_KEY = 'regional_head_dashboard_state';
        const stateToSave = {
            ...this.state,
            loading: false,  // Don't persist loading
            error: null,     // Don't persist errors
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave));
    }

    async navigateToUnit(unit) {
        console.log("Navigating to unit:", unit);
        this.state.loading = true;
        this.state.error = null; // Clear previous errors
        this.state.unit_details = null; // Reset unit details
        try {
            const res = await this.rpc("/get_unit_information_users", { unit });
            console.log("Unit Details RPC Response:", res);
            if (res && !res.status) {
                // Direct response with unit details (as per provided RPC response)
                this.state.unit_details = res;
            } else if (res.status === 200 && res.unit) {
                this.state.unit_details = res.unit;
            } else {
                this.state.error = res.message || "Unit not found";
            }
        } catch (error) {
            this.state.error = error.message || "Failed to fetch unit details";
        } finally {
            this.state.loading = false;
            this.state.currentView = "unit_detail";
            this.state.selected_unit = unit;
            this.state.selectedUserId = null;
            this.saveState();
            this.render();
        }
    }
    async loadStaffDetails(email, user_id, name) {
        try {
            console.log("Loading details for user_id:", email);
        } catch (error) {
            console.error("Error fetching staff details:", error);
        }
    }
    selectUser(userId) {
        this.state.selectedUserId = userId;
        this.saveState();
    }
    async today_attendance(user_id) {
        try {
            const domain = [["user_id", "=", user_id]];
            const context = { default_user_id: user_id };
            await this.actionService.doAction({
                type: "ir.actions.act_window",
                name: "Work Sessions",
                res_model: "work.session",
                view_mode: "tree,form",
                views: [
                    [false, "tree"],
                    [false, "form"],
                ],
                target: "current",
                domain: domain,
                context: context,
            });
        } catch (error) {
            console.error("Error fetching staff details:", error);
        }
    }

    async totalCustomerForms(email,user_id) {
        try {
            console.log(email, "vinn");
            const domain = [["agent_login", "=", email]];
            const context = { default_user_id: user_id };
            await this.actionService.doAction({
                type: "ir.actions.act_window",
                name: "Customer Form",
                res_model: "customer.form",
                view_mode: "kanban,form",
                views: [
                    [false, "kanban"],
                    [false, "form"],
                ],
                target: "current",
                domain: domain,
                context: context,
            });
        } catch (error) {
            console.error("Error fetching staff details:", error);
        }
    }
    async reg_head_cu_form() {
        if (this.state.unit_names.length === 0) {
            console.warn("No units available for filtering customer forms.");
            return;
        }
        try {
            const users = await this.orm.searchRead("res.users", [
                ["role", "=", "agent"],
                ["unit_name", "in", this.state.unit_names],
                ["status", "=", "active"],
            ], ["login"]);
            const agent_logins = users.map((u) => u.login).filter(Boolean);
            if (agent_logins.length === 0) {
                console.warn("No active agents found in the units.");
                return;
            }
            const domain = [["agent_login", "in", agent_logins]];
            await this.actionService.doAction({
                type: "ir.actions.act_window",
                name: "Customer Form",
                res_model: "customer.form",
                view_mode: "kanban,form",
                views: [
                    [false, "kanban"],
                    [false, "tree"],
                    [false, "form"],
                ],
                target: "current",
                domain: domain,
                context: {},
            });
        } catch (error) {
            console.error("Error opening customer forms:", error);
        }
    }
    user_creation() {
        this.actionService.doAction("sale_repo_app.action_users_wizard");
    }
    excel_report() {
        this.actionService.doAction("sale_repo_app.action_users_wizard_excel");
    }
    attendance_excel_report() {
        this.actionService.doAction("sale_repo_app.action_attendance_report_users_wizard_excel");
    }

    goBack() {
        console.log("Returning to dashboard");
        this.state.currentView = "dashboard";
        this.state.selected_unit = null;
        this.state.unit_details = null;
        this.state.error = null;
        this.state.selectedUserId = null;
        this.saveState();
        this.render();
    }
}

registry.category("actions").add("sale_repo_app.regional_head_dashboard", RegionalHeadDashboard);