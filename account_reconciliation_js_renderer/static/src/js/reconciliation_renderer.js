odoo.define("account_reconcile_partial.ReconciliationModel", function (require) {


    var model = require('account.ReconciliationModel');
    var field_utils = require('web.field_utils');
    var utils = require('web.utils');
    var session = require('web.session');
    var core = require('web.core');
    var _t = core._t;
    console.log(model);

    var StatementModelInherit = model.StatementModel.include({

        _formatLineProposition: function (line, props) {
            var self = this;
            if (props.length) {
                _.each(props, function (prop) {
                    console.log(prop);
                    prop.amount = prop.debit || -prop.credit;
                    prop.label = prop.name;
                    prop.account_id = self._formatNameGet(prop.account_id || line.account_id);
                    prop.is_partially_reconciled = prop.amount_str !== prop.total_amount_str;
                    prop.to_check = !!prop.to_check;
                });
            }
        },





    });

});
