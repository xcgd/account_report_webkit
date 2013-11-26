from osv import fields, osv


class AccountTrialBalanceWizard(osv.TransientModel):
    _inherit = "account.common.balance.report"
    _description = "Trial Balance Report"
    _name = "trial.balance.webkit"

    def _analytic_dimensions(self, cr, uid, context):
        obj = self.pool.get('analytic.dimension')
        ids = obj.search(cr, uid,
            [('ns_id.model_name', '=', 'account_account')],
            context=context)
        res = obj.read(cr, uid, ids, ['id', 'name'], context=context)
        return [(r['id'], r['name']) for r in res]

    def _default_ledger_types(self, cr, uid, context):
#         obj = self.pool.get('alternate_ledger.ledger_type')
#         return obj.search(cr, uid, [('name', '=', 'A')])
        return []  # TODO alternate_ledge

    _columns = {
        'analytic_codes': fields.selection(
            _analytic_dimensions,
            string='Ouput element'
        ),
        # TODO alternate_ledger
        'ledger_types': fields.many2many(
            'res.users',
#             'alternate_ledger.ledger_type',
            string='Ledger types',
#             required=True
        ),
        'account_from': fields.char('From account', size=256),
        'account_to': fields.char('To account', size=256),
        'currency_id': fields.many2one(
            'res.currency',
            string='Filter on currencies'
        ),
        'include_zero': fields.boolean(
            'Include accounts at 0'
        ),
    }

    _defaults = {
        'ledger_types': _default_ledger_types,
        'include_zero': lambda *a: False,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        # we update form with display account value
        data['form'].update(
            self.read(cr, uid, ids, [
                'analytic_codes',
                'ledger_types',
                'account_from',
                'account_to',
                'currency_id',
                'include_zero'
            ], context=context)[0]
        )
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.account_report_trial_balance_webkit',
            'datas': data
        }
