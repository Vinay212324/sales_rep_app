/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { sharedStore } from "./dashboard";

export class SalesCirculationIncharge extends Component {
    static template = "sale_repo_app.circulation_incharge_dashboard_template";

    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
        globalState: { type: Object, optional: true },
    };

    setup() {
        this.actionService = useService("action");
        this.rpc = useService("rpc");

        // Load persisted state from localStorage
        const savedState = localStorage.getItem('circulation_dashboard_state');
        const persisted = savedState ? JSON.parse(savedState) : {};

        this.state = useState({
            name: persisted.name || "",
            user_id: persisted.user_id || "",
            login: persisted.login || "",
            status: persisted.status || "active",
            number_of_resources: persisted.number_of_resources || false,
            attend_customer: persisted.attend_customer || false,
            view_all_customer_forms: persisted.view_all_customer_forms || false,
            approved_staff: persisted.approved_staff || false,
            staff_waiting_for_approval: persisted.staff_waiting_for_approval || false,
            searchTerm: persisted.searchTerm || "",
            searchAge: persisted.searchAge || "",
            selectedStaff: null,
            staffList: [],
            agenciesList: [],
            loading: true,
            error: null,
            count:"",
            cu_count:"",
            unit_name: "",
        });

        onWillStart(async () => {
            try {
                this.state.loading = true;
                const res = await this.rpc("/get_created_staff", {});
                if (res && res.status === 200) {
                    this.state.staffList = res.users || [];
                    this.state.agenciesList = res.agencies || [];
                    this.state.count = res.count || 0;
                    this.state.cu_count = res.cu_count || 0;
                    this.state.unit_name = res.unit_name || "";
                } else {
                    this.state.error = res.error || "Failed to load staff data.";
                    this.env.services.notification.add(this.state.error, {
                        type: "danger",
                        title: "Error",
                    });
                }
            } catch (error) {
                this.state.error = error.message || "Failed to load staff data.";
                this.env.services.notification.add(this.state.error, {
                    type: "danger",
                    title: "Error",
                });
            } finally {
                this.state.loading = false;
            }
        });
    }

    saveState() {
        const stateToSave = {
            name: this.state.name,
            user_id: this.state.user_id,
            login: this.state.login,
            status: this.state.status,
            number_of_resources: this.state.number_of_resources,
            attend_customer: this.state.attend_customer,
            view_all_customer_forms: this.state.view_all_customer_forms,
            approved_staff: this.state.approved_staff,
            staff_waiting_for_approval: this.state.staff_waiting_for_approval,
            searchTerm: this.state.searchTerm,
            searchAge: this.state.searchAge,
        };
        localStorage.setItem('circulation_dashboard_state', JSON.stringify(stateToSave));
    }

    sendMessage() {
        sharedStore.message = "Hello from Circulation Incharge!";
        sharedStore.triggerFunction = !sharedStore.triggerFunction;
    }

    openStaffList() {
        this.state.number_of_resources = true;
        this.state.attend_customer = false;
        this.state.view_all_customer_forms = false;
        this.state.approved_staff = false;
        this.state.staff_waiting_for_approval = false;
        this.state.status = "active";
        this.state.name = "";
        this.state.user_id = "";
        this.state.login = "";
        this.saveState();
    }
    filteredAgenciesList_open() {
        this.state.number_of_resources = false;
        this.state.attend_customer = false;
        this.state.view_all_customer_forms = true;
        this.state.approved_staff = false;
        this.state.staff_waiting_for_approval = false;
        this.state.status = "active";
        this.state.name = "";
        this.state.user_id = "";
        this.state.login = "";
        this.saveState();
    }
    openStaffList_only() {
        this.state.number_of_resources = true;
        this.state.attend_customer = false;
        this.state.view_all_customer_forms = false;
        this.state.approved_staff = true;
        this.state.staff_waiting_for_approval = false;
        this.state.status = "active";
        this.state.name = "";
        this.state.user_id = "";
        this.state.login = "";
        this.saveState();
    }
    user_unactive() {
        this.state.number_of_resources = true;
        this.state.attend_customer = false;
        this.state.view_all_customer_forms = false;
        this.state.approved_staff = false;
        this.state.staff_waiting_for_approval = true;
        this.state.status = "un_activ";
        this.state.searchTerm = ""; // Clear search term to show all unapproved staff
        this.state.error = null; // Reset error state
        this.state.name = "";
        this.state.user_id = "";
        this.state.login = "";
        this.saveState();
    }

    office_staff_creation() {
        this.actionService.doAction("sale_repo_app.action_create_office_staff_custom_form");
    }

    get filteredStaffList() {
        const term = (this.state.searchTerm || "").trim().toLowerCase();
        let filtered = this.state.staffList.filter(staff => staff.status === this.state.status);
        if (!term) {
            return filtered;
        }
        return filtered.filter((staff) => {
            const name = (staff.name ?? "").toString().toLowerCase();
            const email = (staff.email ?? "").toString().toLowerCase();
            const unit = (staff.unit_name ?? "").toString().toLowerCase();
            const phone = (staff.phone ?? "").toString().toLowerCase();
            const aadhar = (staff.aadhar_number ?? "").toString().toLowerCase();
            const id = (staff.id ?? "").toString().toLowerCase();
            const status = (staff.status ?? "").toString().toLowerCase();
            return (
                name.includes(term) ||
                email.includes(term) ||
                unit.includes(term) ||
                phone.includes(term) ||
                aadhar.includes(term) ||
                id.includes(term) ||
                status.includes(term)
            );
        });
    }

    get filteredAgenciesList() {
        const term = (this.state.searchAge || "").trim().toLowerCase();
        if (!term) {
            return this.state.agenciesList;
        }
        return this.state.agenciesList.filter((agency) => {
            const code = (agency.code ?? "").toString().toLowerCase();
            const location_name = (agency.location_name ?? "").toString().toLowerCase();
            const name = (agency.name ?? "").toString().toLowerCase();
            const phone = (agency.phone ?? "").toString().toLowerCase();
            const unit_name = (agency.unit_name ?? "").toString().toLowerCase();
            return (
                code.includes(term) ||
                location_name.includes(term) ||
                name.includes(term) ||
                phone.includes(term) ||
                unit_name.includes(term)
            );
        });
    }

    async today_attendance() {
        try {
            const domain = [["user_id", "=", this.state.user_id]];
            const context = { default_user_id: this.state.user_id };
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

    async totalCustomerForms() {
        try {
            const domain = [["agent_login", "=", this.state.login]];
            const context = { default_user_id: this.state.user_id };
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

    async loadStaffDetails(login, user_id, name) {
        try {
            this.state.number_of_resources = false;
            this.state.attend_customer = true;
            this.state.view_all_customer_forms = false;
            this.state.approved_staff = false;
            this.state.staff_waiting_for_approval = false;
            this.state.status = "active";
            this.state.login = login;
            this.state.name = name;
            this.state.user_id = user_id;
            console.log("Loading details for user_id:", user_id);
            this.saveState();
        } catch (error) {
            console.error("Error fetching staff details:", error);
        }
    }

    async Open_agencies_List(phone, id, name) {
        try {
            this.state.number_of_resources = false;
            this.state.attend_customer = false;
            this.state.view_all_customer_forms = true;
            this.state.approved_staff = false;
            this.state.staff_waiting_for_approval = false;
            this.state.status = "active";
            this.state.login = phone;
            this.state.name = name;
            this.state.user_id = id;
            console.log("Loading details for agency id:", id, "name:", name);

            const domain = [["Agency", "ilike", this.state.name]];
            const context = { default_Agency: this.state.name };
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
            // Removed conflicting state changes; rely on persistence
            this.saveState();
        } catch (error) {
            console.error("Error in Open_agencies_List:", error);
            this.env.services.notification.add("Failed to load customer forms: " + (error.message || "Unknown error"), {
                type: "danger",
                title: "Error",
            });
        }
    }

    async loadStaffUnactive(login, user_id, name) {
        try {
            this.state.loading = true;
            this.state.error = null;

            // Call the status update endpoint
            const res = await this.rpc("/local/update/status", { user_id: user_id, status: "active" });
            if (res && res.success === true) {
                // Show success notification
                this.env.services.notification.add("Staff approved successfully!", {
                    type: "success",
                    title: "Success",
                });

                // Refresh the staff list
                const staffRes = await this.rpc("/get_created_staff", {});
                if (staffRes && staffRes.status === 200 && staffRes.users) {
                    this.state.staffList = staffRes.users;
                    this.state.count = staffRes.count || 0;
                    this.state.cu_count = staffRes.cu_count || 0;
                    this.state.unit_name = staffRes.unit_name || "";
                } else {
                    this.state.error = "Failed to refresh staff list.";
                }
            } else {
                this.state.error = res.error || "Failed to approve staff.";
                this.env.services.notification.add(this.state.error, {
                    type: "danger",
                    title: "Error",
                });
            }
        } catch (error) {
            this.state.error = error.message || "Failed to approve staff.";
            this.env.services.notification.add(this.state.error, {
                type: "danger",
                title: "Error",
            });
        } finally {
            this.state.loading = false;
            this.saveState();
        }
    }
    excel_report() {
        this.actionService.doAction("sale_repo_app.action_users_wizard_excel");
    }
    attendance_excel_report() {
        this.actionService.doAction("sale_repo_app.action_attendance_report_users_wizard_excel");
    }
    async reg_head_cu_form() {
        try {
            const domain = [["unit_name", "=", this.state.unit_name]];
            const context = { default_unit_name: this.state.unit_name };
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
                context: context,
            });
        } catch (error) {
            console.error("Error opening customer forms:", error);
            this.env.services.notification.add("Failed to load customer forms: " + (error.message || "Unknown error"), {
                type: "danger",
                title: "Error",
            });
        }
    }
}
registry.category("actions").add(
    "sale_repo_app.circulation_incharge_dashboard",
    SalesCirculationIncharge
);