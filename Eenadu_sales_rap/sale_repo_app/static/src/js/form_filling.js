/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const NEWSPAPERS = [
    "Deccan Chronicle", "Eenadu", "AndhraJyoti", "The Hindu", "Namasthe Telangana",
    "Metro India", "The Hans India", "Nava Telangana", "The Deccan Times", "Hindi Milap", "Prajasakti"
];

const PROFESSIONS = [
    "Farmer", "Doctor", "Teacher", "Lawyer", "Artist", "Musician", "Chef", "Photographer",
    "Electrician", "Plumber", "Designer", "Writer", "Social Worker", "Marketing Specialist", "Accountant"
];

export class SelfCustomerFormFillingSalesRep extends Component {
    static template = "sale_repo_app.customer_form_filling_file";

    setup() {
        this.PROFESSIONS = PROFESSIONS;
        this.rpc = useService("rpc");

        const today = new Date();
        const date = today.toISOString().split('T')[0];
        const time = today.toTimeString().slice(0, 5);

        // Store initial state for easy reset
        this.initialState = {
            date,
            time,
            family_head_name: "",
            father_name: "",
            mother_name: "",
            spouse_name: "",
            house_number: "",
            street_number: "",
            city: "",
            pin_code: "",
            address: "",
            mobile_number: "",
            eenadu_newspaper: true,
            feedback_to_improve_eenadu_paper: "",
            read_newspaper: false,
            current_newspaper: "",
            reason_for_not_taking_eenadu_newsPaper: "",
            reason_not_reading: "",
            free_offer_15_days: false,
            reason_not_taking_offer: "",
            employed: true,
            job_type: "",
            job_type_one: "",
            job_profession: "",
            job_designation: "",
            company_name: "",
            profession: "",
            job_designation_one: "",
            select_profession: "",
            latitude: "",
            longitude: "",
            showModal: false,
            modalType: "",
            selfieDataUrl: "",       // If you added selfie capture per previous discussions
            cameraActive: false,
        };

        this.state = useState(Object.assign({}, this.initialState));
    }

    toggle(key) {
        this.state[key] = !this.state[key];
    }

    showDropdown(type) {
        this.state.showModal = true;
        this.state.modalType = type;
    }

    selectDropdownItem(type, value) {
        this.state[type] = value;
        this.closeDropdownModal();
    }

    closeDropdownModal() {
        this.state.showModal = false;
        this.state.modalType = "";
    }

    async getAddressFromCoords(latitude, longitude) {
        const url = `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json&addressdetails=1`;
        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to fetch address.");
        const data = await response.json();

        const address = data.display_name || "";
        const city = data.address.city || data.address.town || data.address.village || data.address.hamlet || "";
        const pincode = data.address.postcode || "";

        return { address, city, pincode, full: data.address };
    }

    async getLocation() {
        if (!navigator.geolocation) {
            alert("❌ Geolocation not supported.");
            return;
        }
        navigator.geolocation.getCurrentPosition(
            async pos => {
                this.state.latitude = pos.coords.latitude;
                this.state.longitude = pos.coords.longitude;

                try {
                    const { address, city, pincode } = await this.getAddressFromCoords(
                        this.state.latitude,
                        this.state.longitude
                    );
                    this.state.address = address;
                    this.state.city = city;
                    this.state.pin_code = pincode;

                    alert(`📍 Location found:
City: ${city}
Pin code: ${pincode}
Address: ${address}`);
                } catch (err) {
                    alert("❌ Could not get address: " + err.message);
                }
            },
            err => {
                alert("❌ Error getting location: " + err.message);
            }
        );
    }

    // (Optional: selfie related methods if you have added selfie capture)
    // ...

    // Getters used for showing/hiding form sections (as per your earlier code)
    get showFeedbackToImprove() { return !this.state.eenadu_newspaper; }
    get showReadNewspaperSection() { return this.state.eenadu_newspaper; }
    get showCurrentPaperSection() { return this.state.read_newspaper; }
    get showNoNewsReason() { return !this.state.read_newspaper; }
    get showFreeTrialSection() { return this.state.eenadu_newspaper; }
    get showPrivateJobFields() { return this.state.employed ? false : (this.state.job_type === "private"); }
    get showGovtJobFields() { return this.state.employed ? false : (this.state.job_type === "govt"); }
    get showProfessionField() { return this.state.employed; }
    get showJobType() { return !this.state.employed; }
    get showJobDesignationOne() { return this.state.job_type === "private" && this.state.employed; }
    get showJobTypeOne() { return this.state.job_type === "govt" && !this.state.employed; }

    async submitForm(ev) {
        ev.preventDefault();
        const formData = { ...this.state };
        try {
            const res = await this.rpc("/for/api/customer_form", { ...formData });
            if (res.result || res.status === "success") {
                alert("✅ Data Submitted Successfully!");

                // Reset form to initial state (clears the form)
                Object.assign(this.state, this.initialState);
            } else {
                alert("❌ Submission Failed: " + (res.error?.message || ""));
            }
        } catch (err) {
            alert("❌ Error submitting form: " + err.message);
        }
    }
}

registry.category("actions").add(
    "sale_repo_app.self_customer_form_filling_sales_rep",
    SelfCustomerFormFillingSalesRep
);
