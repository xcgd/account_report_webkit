# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright Camptocamp SA 2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class AccountPartnerBalanceWizard(orm.TransientModel):
    """Will launch partner balance report and pass required args"""

    _inherit = "account.common.balance.report"
    _name = "partner.balance.webkit"
    _description = "Partner Balance Report"

    def _ledger_type_available(self, cr, uid, context=None):
        obj = self.pool.get('account_streamline.ledger_type')
        return obj.search(cr, uid, [], context=context) != []

    _columns = {
        'result_selection': fields.selection([('customer', 'Receivable Accounts'),
                                              ('supplier', 'Payable Accounts'),
                                              ('customer_supplier', 'Receivable and Payable Accounts')],
                                              "Partner's", required=True),
        'partner_ids': fields.many2many('res.partner', string='Filter on partner',
                                         help="Only selected partners will be printed. Leave empty to print all partners."),
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
    }

    _defaults = {
        'result_selection': lambda *a: 'customer_supplier',
        'ledger_type_available': _ledger_type_available,
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountPartnerBalanceWizard, self).pre_print_report(
            cr, uid, ids, data, context
        )
        vals = self.read(cr, uid, ids, [
            'result_selection',
            'partner_ids',
            'ledger_type',
            'ledger_type_available',
            'account_from',
            'account_to',
        ], context=context)[0]
        data['form'].update(vals)
        return data

    def _print_report(self, cursor, uid, ids, data, context=None):
        # we update form with display account value
        data = self.pre_print_report(cursor, uid, ids, data, context=context)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.account_report_partner_balance_webkit',
            'datas': data
        }
