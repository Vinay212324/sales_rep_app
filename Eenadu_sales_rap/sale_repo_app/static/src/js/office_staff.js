///** @odoo-module **/
//
//import { Component, onWillStart, useState } from "@odoo/owl";
//import { registry } from "@web/core/registry";
//import { useService } from "@web/core/utils/hooks";
//
//export class SalesOfficeStaff extends Component {
//    static template = "sale_repo_app.office_staff_dashboard_template";
//
//    setup() {
//
//    }
//
//
//}
//
//registry.category("actions").add("sale_repo_app.office_staff_dashboard", SalesOfficeStaff);
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class SalesOfficeStaff extends Component {
    static template = "sale_repo_app.office_staff_dashboard_template";

    setup() {
        this.state = useState({
            isCreatingStaff: false,
            isViewingStaff: false,
            staffData: {
                name: "",
                unit: "",
                email: "",
                phone: "",
                user_id: "",
                password: "",
                adhaar: "",
                address: "",
            },
            staffList: [],
        });
    }

    toggleView = (ev) => {
        const buttonText = ev.target.textContent.trim();

        if (buttonText === "Create Staff") {
            this.state.isCreatingStaff = true;
            this.state.isViewingStaff = false;
            this.resetForm();
        } else if (buttonText === "Cancel") {
            this.state.isCreatingStaff = false;
        } else if (buttonText === "View Created Staff") {
            this.state.isViewingStaff = true;
            this.state.isCreatingStaff = false;
        } else if (buttonText === "Hide Staff") {
            this.state.isViewingStaff = false;
        }
    };

    resetForm() {
        this.state.staffData = {
            name: "",
            unit: "",
            email: "",
            phone: "",
            user_id: "",
            password: "",
            adhaar: "",
            address: "",
        };
    }

    submitStaff = (ev) => {
        ev.preventDefault();

        // Create new staff object with unique id
        const newStaff = {
            id: Date.now(),
            ...this.state.staffData,
        };

        // Add to staff list
        this.state.staffList.push(newStaff);

        // Reset form and switch views
        this.resetForm();
        this.state.isCreatingStaff = false;
        this.state.isViewingStaff = true;
    };
}

registry.category("actions").add("sale_repo_app.office_staff_dashboard", SalesOfficeStaff);
