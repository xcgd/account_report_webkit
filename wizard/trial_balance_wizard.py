from openerp.osv import fields, orm


class AccountTrialBalanceWizard(orm.TransientModel):
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

    def _ledger_type_available(self, cr, uid, context=None):
        obj = self.pool.get('account_streamline.ledger_type')
        return obj.search(cr, uid, [], context=context) != []

    _columns = {
        'analytic_codes': fields.selection(
            _analytic_dimensions,
            string='Ouput element'
        ),
        'ledger_type': fields.many2one(
            'account_streamline.ledger_type',
            string='Ledger type',
            help='Ledger selection: only accounts defined for the selected'
                 ' ledger will be printed; or accounts in the actual ledger'
                 ' if this is left unselected.'
        ),
        'ledger_type_available': fields.boolean(
            invisible=True
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
        'ledger_type_available': _ledger_type_available,
        'include_zero': lambda *a: False,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        up_fields = [
            'analytic_codes',
            'ledger_type',
            'ledger_type_available',
            'account_from',
            'account_to',
            'currency_id',
            'include_zero'
        ]
        data['form'].update(
            self.read(cr, uid, ids, up_fields, context=context)[0]
        )
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.account_report_trial_balance_webkit',
            'datas': data
        }
