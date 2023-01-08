/** @odoo-module **/
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";


function databaseManager(env) {
    const databaseURL = "/web/database/manager";
    return {
        type: "item",
        id: "database_manager",
        description: env._t("Database Manager"),
        href: databaseURL,
        callback: () => {
            browser.open(databaseURL, "_blank");
        },
        sequence: 65,
    };
}


registry.category("user_menuitems").add('database_manager', databaseManager)
