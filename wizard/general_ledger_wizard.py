import time

from openerp.osv import fields, orm

# The alternate_ledger module is not required; fallback gracefully.

# TODO Disabled for now; to be discussed...
class FakeLedger(orm.Model):
    _name = 'fake_alternate_ledger'
ledger_available = False

# try:
#     import openerp.addons.alternate_ledger
#     ledger_available = True
# except ImportError:
#     class FakeLedger(orm.Model):
#         _name = 'fake_alternate_ledger'
#     ledger_available = False


class AccountReportGeneralLedgerWizard(orm.TransientModel):
    """Will launch general ledger report and pass required args"""

    _inherit = "account.common.account.report"
    _name = "general.ledger.webkit"
    _description = "General Ledger Report"

    # This enum is to be kept in sync with the one in
    # report/general_ledger.py...
    alloc_enum = [
        ('allocated', 'Allocated'),
        ('not_allocated', 'Not allocated'),
        ('partial', 'Partial'),
        ('all', 'All'),
    ]

    def _analytic_dimensions(self, cr, uid, context):
        obj = self.pool.get('analytic.dimension')
        ids = obj.search(
            cr, uid,
            [('ns_id.model_name', '=', 'account_account')],
            context=context
        )
        res = obj.read(cr, uid, ids, ['id', 'name'], context=context)
        return [(r['id'], r['name']) for r in res]

    def _default_ledger_types(self, cr, uid, context):
        if not ledger_available:
            return []
        obj = self.pool.get('alternate_ledger.ledger_type')
        return obj.search(cr, uid, [('name', '=', 'A')], context=context)

    def _get_account_ids(self, cr, uid, context=None):
        res = False
        if (context.get('active_model', False) == 'account.account' and
            context.get('active_ids', False)
            ):
            res = context['active_ids']
        return res

    _columns = {
        'amount_currency': fields.boolean(
            "With Currency",
            help="It adds the currency column"),

        'display_account': fields.selection(
            [('bal_all', 'All'),
             ('bal_mix', 'With transactions or non zero balance')],
            'Display accounts',
            required=True
        ),
        'account_ids': fields.many2many(
            'account.account', string='Filter on accounts',
            help="Only selected accounts will be printed."
                 " Leave empty to print all accounts."
        ),
        'centralize': fields.boolean(
            'Activate Centralization',
            help='Uncheck to display all the details of centralized accounts.'
        ),
        'analytic_codes': fields.selection(
            _analytic_dimensions,
            string='Ouput element'
        ),
        'allocated': fields.selection(
            alloc_enum,
            string='Allocated',
            required=True,
            translate=True
        ),
        'ledger_types': fields.many2many(
            'alternate_ledger.ledger_type' if ledger_available
            else 'fake_alternate_ledger',
            'general_ledger_report_ledger_type_rel' if ledger_available
            else None,
            'general_ledger_report_id' if ledger_available
            else None,
            'ledger_type_id' if ledger_available
            else None,
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
            'Include accounts that have no transaction'
        ),
    }

    _defaults = {
        'amount_currency': False,
        'display_account': 'bal_mix',
        'account_ids': _get_account_ids,
        'centralize': True,
        'allocated': lambda *a: 'all',
        'ledger_types': _default_ledger_types,
        'include_zero': lambda *a: False,
    }

    def _check_fiscalyear(self, cr, uid, ids, context=None):
        obj = self.read(
            cr, uid, ids[0],
            ['fiscalyear_id', 'filter'],
            context=context
        )
        if not obj['fiscalyear_id'] and obj['filter'] == 'filter_no':
            return False
        return True

    _constraints = [
        (_check_fiscalyear,
         'When no Fiscal year is selected, you must choose'
         ' to filter by periods or by date.',
         ['filter']),
    ]

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountReportGeneralLedgerWizard, self).pre_print_report(
            cr, uid, ids, data, context
        )
        # will be used to attach the report on the main account
        data['ids'] = [data['form']['chart_account_id']]
        vals = self.read(cr, uid, ids, [
            'amount_currency',
            'display_account',
            'account_ids',
            'centralize'
        ], context=context)[0]
        data['form'].update(vals)
        return data

    def onchange_filter(self, cr, uid, ids, filter='filter_no',
                        fiscalyear_id=False, context=None):
        res = {}
        if filter == 'filter_no':
            res['value'] = {
                'period_from': False,
                'period_to': False,
                'date_from': False,
                'date_to': False,
            }
        if filter == 'filter_date':
            if fiscalyear_id:
                fyear = self.pool.get('account.fiscalyear').browse(
                    cr, uid, fiscalyear_id, context=context
                )
                date_from = fyear.date_start
                date_to = (
                    fyear.date_stop > time.strftime('%Y-%m-%d') and
                    time.strftime('%Y-%m-%d') or fyear.date_stop
                )
            else:
                date_from = time.strftime('%Y-01-01')
                date_to = time.strftime('%Y-%m-%d')
            res['value'] = {
                'period_from': False,
                'period_to': False,
                'date_from': date_from,
                'date_to': date_to
            }
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False

            cr.execute('''
                SELECT * FROM (
                    SELECT p.id
                    FROM account_period p
                    LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                    WHERE f.id = %s
                    AND COALESCE(p.special, FALSE) = FALSE
                    ORDER BY p.date_start ASC
                    LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (
                    SELECT p.id
                    FROM account_period p
                    LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                    WHERE f.id = %s
                    AND p.date_start < NOW()
                    AND COALESCE(p.special, FALSE) = FALSE
                    ORDER BY p.date_stop DESC
                    LIMIT 1) AS period_stop''',
                       (fiscalyear_id, fiscalyear_id))

            periods = [i[0] for i in cr.fetchall()]
            if periods:
                start_period = end_period = periods[0]
                if len(periods) > 1:
                    end_period = periods[1]
            res['value'] = {
                'period_from': start_period,
                'period_to': end_period,
                'date_from': False,
                'date_to': False}
        return res

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        up_fields = [
            'analytic_codes',
            'allocated',
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
            'report_name': 'account.account_report_general_ledger_webkit',
            'datas': data
        }
