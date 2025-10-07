/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class SalesOfficeStaff extends Component {
    static template = "sale_repo_app.office_staff_dashboard_template";

    setup() {
        this.rpc = useService("rpc");

        // Load persisted state from localStorage
        const persistedState = JSON.parse(localStorage.getItem('officeStaffState') || '{}');

        this.state = useState({
            loading: true,
            error: null,
            successMessage: null,
            isCreatingStaff: persistedState.isCreatingStaff || false,
            isViewingStaff: persistedState.isViewingStaff || false,
            searchTerm: persistedState.searchTerm || "",
            staffData: {
                name: "",
                unit: "",
                email: "",
                phone: "",
                user_id: "",
                password: "",
                adhaar: "",
            },
            login_info: [],
            staffList: [],
        });

        onWillStart(async () => {
            try{
                const res = await this.rpc("/user_info", { params: {} });
                if (res && res.status === 200 && res.user_info) {
                    this.state.login_info = res.user_info;
                    this.state.staffData.unit = res.user_info.unit_name;
                }
            }catch (error) {
                this.state.error = error.message || "RPC Error";
            }
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

    // Filtered staff list - only active
    get filteredStaffList() {
        const term = this.state.searchTerm.trim().toLowerCase();
        let filtered = this.state.staffList.filter(staff => staff.status === 'active');
        if (!term) return filtered;
        return filtered.filter((staff) =>
            staff.name?.toLowerCase().includes(term) ||
            staff.email?.toLowerCase().includes(term) ||
            staff.unit_name?.toLowerCase().includes(term) ||
            staff.phone?.toLowerCase().includes(term)
        );
    }

    toggleCreate = () => {
        this.state.isCreatingStaff = !this.state.isCreatingStaff;
        this.state.isViewingStaff = false;
        this.state.successMessage = null;
        if (!this.state.isCreatingStaff) {
            this.resetForm();
        }
        this.saveState();
    };

    toggleViewStaff = () => {
        this.state.isViewingStaff = true;
        this.state.isCreatingStaff = false;
        this.saveState();
    };

    saveState = () => {
        const stateToSave = {
            isCreatingStaff: this.state.isCreatingStaff,
            isViewingStaff: this.state.isViewingStaff,
            searchTerm: this.state.searchTerm,
        };
        localStorage.setItem('officeStaffState', JSON.stringify(stateToSave));
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
        };
    }

    onSearchChange = (ev) => {
        this.state.searchTerm = ev.target.value;
        this.saveState();
    };

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
                this.state.successMessage = "Staff created successfully!";
                this.state.error = null;
                this.saveState();
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