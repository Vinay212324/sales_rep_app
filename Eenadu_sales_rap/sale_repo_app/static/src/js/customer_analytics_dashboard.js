/** @odoo-module **/

import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

export class CustomerAnalyticsDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.today = new Date().toISOString().slice(0, 10);

        this.state = useState({
            stats: {},
            openSections: {},

            toggleSection: (period, key) => {
                if (!this.state.openSections[period]) {
                    this.state.openSections[period] = {};
                }
                this.state.openSections[period][key] = !this.state.openSections[period][key];
            },
        });

        onWillStart(async () => {
            const fields = [
                "date", "eenadu_newspaper", "free_offer_15_days", "read_newspaper",
                "current_newspaper", "reason_for_not_taking_eenadu_newsPaper",
                "reason_not_reading", "feedback_to_improve_eenadu_paper"
            ];

            const all = await this.orm.searchRead("customer.form", [], fields);

            const now = new Date();
            const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10);
            const sixMonthsBack = new Date(new Date().setMonth(now.getMonth() - 6)).toISOString().slice(0, 10);
            const yearStart = new Date(new Date().getFullYear(), 0, 1).toISOString().slice(0, 10);

            this.state.stats = this._generateStats(all, {
                today: this.today,
                month: monthStart,
                sixMonths: sixMonthsBack,
                year: yearStart
            });
        });
    }

    _generateStats(records, ranges) {
        return {
            day: this._computeStats(records.filter(r => r.date === ranges.today)),
            month: this._computeStats(records.filter(r => r.date >= ranges.month)),
            sixMonths: this._computeStats(records.filter(r => r.date >= ranges.sixMonths)),
            year: this._computeStats(records.filter(r => r.date >= ranges.year))
        };
    }

    _computeStats(records) {
        let eenaduUsers = 0, freeOffer = 0, otherPapers = 0, noPaper = 0;
        let reasonsNoEenadu = [], reasonsNoReading = [], feedbacks = [];

        for (let i = 0; i < records.length; i++) {
            const rec = records[i];

            if (rec.eenadu_newspaper) {
                eenaduUsers++;
                if (rec.feedback_to_improve_eenadu_paper) {
                    feedbacks.push({ id: `fb-${i}`, text: rec.feedback_to_improve_eenadu_paper });
                }
            }

            if (rec.free_offer_15_days) freeOffer++;

            if (rec.read_newspaper && rec.current_newspaper && rec.current_newspaper.toLowerCase() !== "eenadu") {
                otherPapers++;
            }

            if (!rec.read_newspaper) {
                noPaper++;
                if (rec.reason_not_reading) {
                    reasonsNoReading.push({ id: `nr-${i}`, text: rec.reason_not_reading });
                }
            }

            if (!rec.eenadu_newspaper && rec.reason_for_not_taking_eenadu_newsPaper) {
                reasonsNoEenadu.push({ id: `ne-${i}`, text: rec.reason_for_not_taking_eenadu_newsPaper });
            }
        }

        return {
            eenaduUsers,
            freeOffer,
            otherPapers,
            noPaper,
            reasonsNoEenadu,
            reasonsNoReading,
            feedbacks
        };
    }
}

CustomerAnalyticsDashboard.template = "customer_analytics_dashboard_template";
registry.category("actions").add("customer_analytics_dashboard", CustomerAnalyticsDashboard);
