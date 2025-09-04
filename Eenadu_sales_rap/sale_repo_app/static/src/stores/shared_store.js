/** @odoo-module **/
import { reactive } from "@odoo/owl";

// Shared store
export const sharedStore = reactive({
    message: "",
    triggerFunction: false,
});
