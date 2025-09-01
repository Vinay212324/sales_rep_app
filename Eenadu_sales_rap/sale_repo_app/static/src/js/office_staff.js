/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class SalesOfficeStaff extends Component {
    static template = "sale_repo_app.office_staff_dashboard_template";

    setup() {
        this.rpc = useService("rpc");

        this.state = useState({
            loading: true,
            error: null,
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

        onWillStart(async () => {
            try {
                console.log("🎯 onWillStart triggered");
                const res = await this.rpc("/get_created_staff", { params: {} });
                console.log("API Response:", res);

                if (res && res.status === 200 && res.users) {
                    this.state.staffList = res.users;
                    console.log("✅ Staff loaded:", this.state.staffList);
                }
            } catch (error) {
                console.error("RPC Error:", error);
                this.state.error = error.message || "RPC Error";
            } finally {
                this.state.loading = false;
            }
        });
    }

    toggleCreate = () => {
        this.state.isCreatingStaff = !this.state.isCreatingStaff;
        this.state.isViewingStaff = false;
        if (!this.state.isCreatingStaff) {
            this.resetForm();
        }
    };

    toggleViewStaff = () => {
        this.state.isViewingStaff = !this.state.isViewingStaff;
        this.state.isCreatingStaff = false;
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

    submitStaff = async (ev) => {
        ev.preventDefault();

        try {
            this.state.loading = true;
            const res = await this.rpc("/create_staff", { params: { ...this.state.staffData } });
            if (res && res.status === 200) {
                // Refresh staff list after creation
                const refresh = await this.rpc("/get_created_staff", { params: {} });
                if (refresh && refresh.status === 200 && refresh.users) {
                    this.state.staffList = refresh.users;
                }
                this.resetForm();
                this.state.isCreatingStaff = false;
                this.state.isViewingStaff = true;
                this.state.error = null;
            } else {
                this.state.error = res.error || "Failed to create staff";
            }
        } catch (error) {
            this.state.error = error.message || "Error creating staff";
        } finally {
            this.state.loading = false;
        }
    };
}

registry.category("actions").add("sale_repo_app.office_staff_dashboard", SalesOfficeStaff);
