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
        globalState: { type: Object, optional: true },   // ✅ add this
    };

    setup() {
        this.actionService = useService("action");
        this.rpc = useService("rpc");  // ✅ inject rpc service

        this.state = useState({
            status:"active",
            hide_main:false,
            number_of_resources: true,
            searchTerm: "",
            selectedStaff: null,
            staffList: [],
            loading: true,
            error: null,
        });

        onWillStart(async () => {
            try {
                const res = await this.rpc("/get_created_staff", { params: {} });
                if (res && res.status === 200 && res.users) {
                    this.state.staffList = res.users;
                }
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
        this.state.number_of_resources = false;
        this.state.status = "active";
    }
    user_unactive(){
        this.state.number_of_resources = false;
        this.state.status = "un_activ";
    }

    office_staff_creation() {
        this.actionService.doAction("sale_repo_app.action_create_office_staff_custom_form");

//        this.actionService.doAction({
//            type: "ir.actions.act_window",
//            name: "Customer Forms",
//            res_model: "customer.form",
//            view_mode: "tree,form",
//            domain: [["user_id", "=", staffId]],
//            target: "current",
//        });


    }

    get filteredStaffList() {
        const term = (this.state.searchTerm || "").trim().toLowerCase();
        if (!term) {
            return this.state.staffList;
        }

        return this.state.staffList.filter((staff) => {
            // Safely normalize every field
            const name = (staff.name ?? "").toString().toLowerCase();
            const email = (staff.email ?? "").toString().toLowerCase();
            const unit = (staff.unit_name ?? "").toString().toLowerCase();
            const phone = (staff.phone ?? "").toString().toLowerCase();
            const aadhar = (staff.aadhar_number ?? "").toString().toLowerCase();
            const id = (staff.id ?? "").toString().toLowerCase();
            const status = (staff.status ?? "").toString().toLowerCase();

            // Check across ALL fields
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



    async loadStaffDetails(login) {
        try {
            this.state.number_of_resources = true;
            console.log(login);
            this.actionService.doAction({
                type: 'ir.actions.act_window',
                name: "User Customers",
                res_model: 'res.partner',
                view_mode: 'tree,form',
                domain: [['user_id', '=', 155]],
                context: {
                    default_user_id: 155,
                },
                target: 'current',
            });
            // call your backend route with staffId
            const res = await this.rpc("/get_staff_details", { login: login });

            if (res && res.status === 200 && res.user) {
                console.log("Full staff details:", res.user);

                // Example: you can put it in state to render in template
                this.state.selectedStaff = res.user;
            }
        } catch (error) {
            console.error("Error fetching staff details:", error);
        }
    }

}

registry.category("actions").add(
    "sale_repo_app.circulation_incharge_dashboard",
    SalesCirculationIncharge
);
