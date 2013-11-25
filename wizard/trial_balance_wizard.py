from osv import fields, osv
from openerp.tools.translate import _


class AccountTrialBalanceWizard(osv.TransientModel):
    _inherit = "account.common.balance.report"
    _description = "Trial Balance Report"
    _name = "trial.balance.webkit"

    def _analytic_dimensions(self, cr, uid, context):
        #obj = self.pool.get('analytic.dimension')
        #ids = obj.search(cr, uid,
        #    [('ns_id.model_name', '=', 'account_account')],
        #    context=context)
        #res = obj.read(cr, uid, ids, ['id', 'name'], context=context)
        #return [(r['id'], r['name']) for r in res]
        #TODO : Test if analytic is instaled
        return []

    def _ledger_types(self, cr, uid, context):
        #obj = self.pool.get('alternate_ledger.ledger_type')
        #ids = obj.search(cr, uid, [])
        #res = obj.read(cr, uid, ids, ['id', 'name'], context=context)
        #return [(r['id'], r['name']) for r in res]
        # TODO : Test if alternate ledger is installed
        return []

    def _default_ledger_type(self, cr, uid, context):
        #obj = self.pool.get('alternate_ledger.ledger_type')
        #return obj.search(cr, uid, [('name', '=', 'A')])
        #TODO: Test if alternate ledger is installed
        return []


    _columns = {
        'analytic_codes': fields.selection(_analytic_dimensions,
            string=_('Ouput element')),
        'ledger_type': fields.selection(_ledger_types,
            string=_('Ledger Type'), required=True),
        'account_from': fields.char(_('From account'), size=255),
        'account_to': fields.char(_('To account'), size=255),
        'currency_id': fields.many2one('res.currency',
            string=_('Filter on currencies')),
        'include_zero': fields.boolean(_('Include accounts at 0')),
    }

    _defaults = {
        'ledger_type': _default_ledger_type,
        'include_zero': lambda *a: False,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        # we update form with display account value
        data['form'].update(self.read(
            cr, uid, ids,
            ['analytic_codes',
             'ledger_type',
             'account_from',
             'account_to',
             'currency_id',
             'include_zero'],
            context=context)[0]
        )
        return {'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_trial_balance_webkit',
                'datas': data}
