from openerp.osv import fields, orm

# The alternate_ledger module is not required; fallback gracefully.
try:
    import openerp.addons.alternate_ledger
    ledger_available = True
except ImportError:
    class FakeLedger(orm.Model):
        _name = 'fake_alternate_ledger'
    ledger_available = False


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

    def _default_ledger_types(self, cr, uid, context):
        if not ledger_available:
            return []
        obj = self.pool.get('alternate_ledger.ledger_type')
        return obj.search(cr, uid, [('name', '=', 'A')], context=context)

    _columns = {
        'analytic_codes': fields.selection(
            _analytic_dimensions,
            string='Ouput element'
        ),
        'ledger_types': fields.many2many(
            'alternate_ledger.ledger_type' if ledger_available
            else 'fake_alternate_ledger',
            'trial_balance_report_ledger_type_rel' if ledger_available
            else None,
            'trial_balance_report_id',
            'ledger_type_id',
            string='Ledger types',
            required=ledger_available,
            invisible=not ledger_available
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
        up_fields = [
            'analytic_codes',
            'account_from',
            'account_to',
            'currency_id',
            'include_zero'
        ]
        if ledger_available:
            up_fields.append('ledger_types')
        data['form'].update(
            self.read(cr, uid, ids, up_fields, context=context)[0]
        )
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.account_report_trial_balance_webkit',
            'datas': data
        }
