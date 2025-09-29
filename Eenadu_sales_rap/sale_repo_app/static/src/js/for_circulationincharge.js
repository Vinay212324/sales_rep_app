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

        this.state = useState({
            name: "",
            user_id: "",
            login: "",
            status: "active",
            number_of_resources: false,
            attend_customer: false,
            view_all_customer_forms: false,
            approved_staff: false,
            staff_waiting_for_approval: false,
            searchTerm: "",
            searchAge: "",
            selectedStaff: null,
            staffList: [],
            agenciesList: [],
            loading: true,
            error: null,
            count:"",
            cu_count:"",
        });

        onWillStart(async () => {
            try {
                const res = await this.rpc("/get_created_staff", {});
                if (res && res.status === 200 && res.users) {
                    this.state.staffList = res.users;
                }
                if (res && res.agencies) {
                    this.state.agenciesList = res.agencies;
                }
                this.state.count = res.count || 0;
                this.state.cu_count = res.cu_count || 0;

            } catch (error) {
                this.state.error = error.message || "RPC Error";
            } finally {
                this.state.loading = false;
            }
        });
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
    }
    filteredAgenciesList_open() {
        this.state.number_of_resources = false;
        this.state.attend_customer = false;
        this.state.view_all_customer_forms = true;
        this.state.approved_staff = false;
        this.state.staff_waiting_for_approval = false;
        this.state.status = "active";
    }
    openStaffList_only() {
        this.state.number_of_resources = true;
        this.state.attend_customer = false;
        this.state.view_all_customer_forms = false;
        this.state.approved_staff = true;
        this.state.staff_waiting_for_approval = false;
        this.state.status = "active";
    }
    user_unactive() {
        this.state.number_of_resources = true;
        this.state.attend_customer = false;
        this.state.view_all_customer_forms = false;
        this.state.approved_staff = false;
        this.state.staff_waiting_for_approval = true;
        this.state.status = "un_activ";
    }

    office_staff_creation() {
        this.actionService.doAction("sale_repo_app.action_create_office_staff_custom_form");
    }

    get filteredStaffList() {
        const term = (this.state.searchTerm || "").trim().toLowerCase();
        if (!term) {
            return this.state.staffList;
        }
        return this.state.staffList.filter((staff) => {
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
            this.state.attend_customer = true;
            this.state.number_of_resources = true;
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
            this.state.attend_customer = true;
            this.state.number_of_resources = true;
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
            this.state.login = login;
            this.state.name = name;
            this.state.user_id = user_id;
            console.log("Loading details for user_id:", user_id);
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
            this.state.attend_customer = true;
            this.state.number_of_resources = true;
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
            this.state.number_of_resources = true;
            this.state.attend_customer = false;
            this.state.view_all_customer_forms = false;
            this.state.approved_staff = false;
            this.state.staff_waiting_for_approval = true;
            this.state.login = login;
            this.state.name = name;
            this.state.user_id = user_id;
            try {
                const res = await this.rpc("/local/update/status", { "user_id": user_id, "status": "active" });
                if (res && res.success === "True") {
                    console.log("Staff activated successfully:", res);
                } else {
                    console.warn("Activation failed:", res);
                }
            } catch (error) {
                this.state.error = error.message || "RPC Error";
            }
            try {
                const res = await this.rpc("/get_created_staff", {});
                if (res && res.status === 200 && res.users) {
                    this.state.staffList = res.users;
                }
                if (res && res.agencies) {
                    this.state.agenciesList = res.agencies;
                }
            } catch (error) {
                this.state.error = error.message || "RPC Error";
            } finally {
                this.state.loading = false;
            }
        } catch (error) {
            console.error("Error fetching staff details:", error);
        }
    }
    excel_report() {
        this.actionService.doAction("sale_repo_app.action_users_wizard_excel");
    }
    attendance_excel_report() {
        this.actionService.doAction("sale_repo_app.action_attendance_report_users_wizard_excel");
    }
}
registry.category("actions").add(
    "sale_repo_app.circulation_incharge_dashboard",
    SalesCirculationIncharge
);




            // ✅ Directly open your custom form view
//            await this.actionService.doAction({
//                type: "ir.actions.act_window",
//                name: "Waiting User",
//                res_model: "sale_repo_app.base.res.users",
//                view_mode: "form",
//                views: [[false, "form"]],   // default form view
//                target: "current",
//                res_id: user_id,
//                context: { default_user_id: user_id },
//            });




//            const domain = [["user_id", "=", user_id]]; // Filter by user_id for work.session
//            const context = {
//                default_user_id: user_id, // Set default value for user_id field
//            };
//
//
//            await this.actionService.doAction({
//                type: "ir.actions.act_window",
//                name: "Work Sessions",
//                res_model: "work.session", // Changed to work.session
//                view_mode: "tree,form", // Specify both tree and form views
//                views: [
//                    [false, "tree"], // Use default tree view
//                    [false, "form"], // Use default form view
//                ],
//                target: "current",
//                domain: domain, // Apply the domain filter
//                context: context, // Apply context for constraints
//            });