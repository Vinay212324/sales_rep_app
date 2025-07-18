/** @odoo-module **/

import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

const userMenuRegistry = registry.category("user_menuitems");

// Patch the UserMenu to remove unwanted items
patch(UserMenu.prototype, "Eenadu_sales_rap.UserMenu", {
    setup() {
        this._super(...arguments);
        userMenuRegistry.remove("support");
        userMenuRegistry.remove("odoo_account");
        userMenuRegistry.remove("documentation");
    },
});

// Add "My Profile" as a custom menu item
userMenuRegistry.add(
    "profile",
    (env) => {
        return {
            type: "item",
            id: "profile",
            description: "My Profile",
            callback: async () => {
                const action = await env.services.orm.call("res.users", "action_get", []);
                env.services.action.doAction(action);
            },
            sequence: -1,
        };
    },
    { force: true }
);
