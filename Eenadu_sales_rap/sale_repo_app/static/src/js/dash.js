/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";  // ✅ CORRECT way to use rpc in OWL
import { rpc } from "@web/core/network/rpc_service";

export class SelfDashboardManagerSalesRep extends Component {
    static template = "sale_repo_app.SelfDashboardTemplate";

    setup() {
        this.rpc = useService("rpc");  // ✅ Get the rpc service
        this.state = useState({ name: "", target: "", today_customer_forms_count: "", target_left:""});


        onWillStart(async () => {
            try {
                const result = await this.rpc("/api/dashboard_data", {});
                if (result.success) {
                    this.state.name = result.name || "";
                    this.state.target = result.target || "";
                    this.state.today_customer_forms_count = result.today_customer_forms_count || 0;
                    this.state.target_left = result.target_left || 0;
                } else {
                    console.error("❌ Failed to fetch data:", result.message);
                }
            } catch (error) {
                console.error("❌ RPC Error:", error);
            }
        });
    }
}


registry.category("actions").add("sale_repo_app.self_dashboard_manager_sales_rep", SelfDashboardManagerSalesRep);
