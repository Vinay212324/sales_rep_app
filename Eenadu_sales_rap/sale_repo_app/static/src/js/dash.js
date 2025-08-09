/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class SalesDashboardDesktop extends Component {
    static template = "sale_repo_app.SalesDashboardDesktopTemplate";

    setup() {
        this.rpc = useService("rpc");
        this.actionService = useService("action");

        this.state = useState({
            name: "",
            date: "",
            target: 0,
            today_customer_forms_count: 0,
            target_left: 0,
            subscribed_count: 0,
            shift_start_time: "",
            loading: true,
            error: "",
            agencies: [],
            selectedAgencyId: "",
            saving: false,
            saveSuccess: "",
            saveError: "",
            showAgencySelect: false,
        });

        onWillStart(async () => {
            try {
                // Fetch all agencies
                const res = await this.rpc("/get_all_agencies_web", {});
                if (res.success) {
                    this.state.agencies = res.data || [];

                    // Fetch current agency after agencies are loaded
                    const currentAgency = await this.rpc("/get_current_agency_web", {});
                    if (currentAgency.success && currentAgency.data) {
                        this.state.selectedAgencyId = String(currentAgency.data.id);
                    } else {
                        this.state.selectedAgencyId = "";
                    }
                } else {
                    this.state.error = res.message || "Failed to fetch agencies";
                }

                // Fetch dashboard data
                const dashboardResult = await this.rpc("/api/dashboard_data", {});
                if (dashboardResult.success) {
                    this.state.name = dashboardResult.name || "";
                    this.state.date = dashboardResult.date || (new Date()).toLocaleDateString();
                    this.state.target = dashboardResult.target || 0;
                    this.state.today_customer_forms_count = dashboardResult.today_customer_forms_count || 0;
                    this.state.target_left = dashboardResult.target_left || 0;
                    this.state.subscribed_count = dashboardResult.subscribed_count || 0;
                    this.state.shift_start_time = dashboardResult.shift_start_time || "";
                } else {
                    this.state.error = dashboardResult.message || "Failed to fetch dashboard data";
                }
            } catch (error) {
                this.state.error = error.message || "RPC Error";
            } finally {
                this.state.loading = false;
            }
        });
    }

    showAgencyDropdown() {
        this.state.saveSuccess = "";
        this.state.saveError = "";
        this.state.showAgencySelect = true;
    }

    async onAgencyChange() {
        this.state.saveSuccess = "";
        this.state.saveError = "";

        if (!this.state.selectedAgencyId) {
            return;
        }

        this.state.saving = true;
        try {
            const res = await this.rpc("/assign_agency_web", { pin_lo_id: this.state.selectedAgencyId });
            if (res.success) {
                this.state.saveSuccess = res.message || "Agency assigned successfully.";
                this.state.showAgencySelect = false;
            } else {
                this.state.saveError = res.message || "Failed to assign agency.";
            }
        } catch (e) {
            this.state.saveError = e.message || "Network error.";
        } finally {
            this.state.saving = false;
        }
    }

    showRouteMap() {
        alert("Route Map feature under development!");
    }

    startWork() {
        alert("Starting work!");
    }

    goToCustomerForm() {
        if (this.actionService) {
            this.actionService.doAction("sale_repo_app.self_customer_form_filling_sales_rep");
        } else {
            console.error("actionService is not available.");
        }
    }
}

registry.category("actions").add("sale_repo_app.sales_dashboard_desktop", SalesDashboardDesktop);
