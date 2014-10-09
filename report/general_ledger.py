# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Guewen Baconnier
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

from operator import itemgetter
from itertools import groupby
from datetime import datetime

from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _
from .common_reports import CommonReportHeaderWebkit
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser

from report_util import (
    compare_ledger_types,
    should_show_account,
    should_show_line
)


class GeneralLedgerWebkit(report_sxw.rml_parse, CommonReportHeaderWebkit):

    alloc_enum = {
        'allocated': _('Allocated'),
        'not_allocated': _('Not allocated'),
        'partial': _('Partial'),
        'all': _('All'),
    }

    def __init__(self, cursor, uid, name, context):
        super(GeneralLedgerWebkit, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('GENERAL LEDGER'), company.name))

        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('General Ledger'),
            'display_account': self._get_display_account,
            'display_account_raw': self._get_display_account_raw,
            'filter_form': self._get_filter,
            'target_move': self._get_target_move,
            'initial_balance': self._get_initial_balance,
            'amount_currency': self._get_amount_currency,
            'display_target_move': self._get_display_target_move,
            'accounts': self._get_accounts_br,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def set_context(self, objects, data, ids, report_type=None):
        """Populate a ledger_lines attribute on each browse record that will be used
        by mako template"""
        new_ids = (
            data['form']['account_ids'] or
            data['form']['chart_account_id']
        )

        # Account initial balance memoizer
        init_balance_memoizer = {}

        # Reading form
        main_filter = self._get_form_param('filter', data, default='filter_no')
        target_move = self._get_form_param('target_move', data, default='all')
        start_date = self._get_form_param('date_from', data)
        stop_date = self._get_form_param('date_to', data)
        do_centralize = self._get_form_param('centralize', data)
        start_period = self.get_start_period_br(data)
        stop_period = self.get_end_period_br(data)
        fiscalyear = self.get_fiscalyear_br(data)
        chart_account = self._get_chart_account_id_br(data)

        if main_filter == 'filter_no':
            start_period = self.get_first_fiscalyear_period(fiscalyear)
            stop_period = self.get_last_fiscalyear_period(fiscalyear)

        # computation of ledger lines
        if main_filter == 'filter_date':
            start = start_date
            stop = stop_date
        else:
            start = start_period
            stop = stop_period

        initial_balance = self.is_initial_balance_enabled(main_filter)
        initial_balance_mode = initial_balance and self._get_initial_balance_mode(start) or False

        # Retrieving accounts
        accounts = self.get_all_accounts(new_ids, exclude_type=['view'])
        if initial_balance_mode == 'initial_balance':
            init_balance_memoizer = self._compute_initial_balances(accounts, start, fiscalyear)
        elif initial_balance_mode == 'opening_balance':
            init_balance_memoizer = self._read_opening_balance(accounts, start)

        ledger_lines_memoizer = self.compute_account_ledger_lines(
            accounts, main_filter, target_move, start, stop
        )

        allocated = data['form']['allocated']

        analytic_codes = data['form']['analytic_codes']
        if analytic_codes:
            analytic_field = 'a' + analytic_codes + '_id'
            analytic_dim = self.pool.get('analytic.dimension').browse(
                self.cursor, self.uid, int(analytic_codes)).name
            analytic_groups = {}

        account_range_filter = (
            data['form']['account_from'] and
            data['form']['account_to']
        )
        if account_range_filter:
            account_range_filter = _('From %s to %s') % (
                data['form']['account_from'],
                data['form']['account_to']
            )

        currency_filter = data['form']['currency_id']
        if currency_filter:
            currency_filter = currency_filter[0]

            curr_obj = self.pool.get('res.currency')
            curr_name = curr_obj.browse(self.cursor, self.uid,
                currency_filter).name

        objects = []

        for account in self.pool.get('account.account').browse(self.cursor, self.uid, accounts):
            if not compare_ledger_types(account, data, self):
                continue

            if (account_range_filter and
                not should_show_account(account, data)):
                continue

            if do_centralize and account.centralized and ledger_lines_memoizer.get(account.id):
                account.ledger_lines = self.centralize_lines(
                    main_filter, ledger_lines_memoizer.get(account.id, [])
                )
            else:
                account.ledger_lines = ledger_lines_memoizer.get(account.id, [])
            account.init_balance = init_balance_memoizer.get(account.id, {})

            if not account.ledger_lines:
                continue

            # New list of lines as we are going to filter some of them out.
            new_lines = []

            # Recompute these counters as we may not be showing every line.
            account.debit = 0.0
            account.credit = 0.0
            account.balance = 0.0

            for line in account.ledger_lines:
                if not self._check_allocated(account, line, allocated):
                    continue

                if not should_show_line(line, currency_filter):
                    continue

                new_lines.append(line)

                account.debit += line.get('debit_curr')
                account.credit += line.get('credit_curr')
                account.balance += (
                    line.get('debit_curr') -
                    line.get('credit_curr')
                )

            if not any((account.debit, account.credit, account.balance)):
                continue

            account.ledger_lines = new_lines

            if analytic_codes:
                a_code = account[analytic_field]
                if a_code:

                    # Change the account code except for individual lines,
                    # where we want to keep the real account code.
                    for line in account.ledger_lines:
                        line['orig_account'] = account.code

                    if a_code.id not in analytic_groups:
                        account.code = a_code.name
                        account.name = a_code.description
                        account.level = 2
                        analytic_groups[a_code.id] = account
                    else:
                        a_row = analytic_groups[a_code.id]
                        a_row.ledger_lines.extend(account.ledger_lines)
                        # sum the 2 init_balance dicts
                        a_row.init_balance = {
                            k: a_row.init_balance.get(k, 0) + account.init_balance.get(k, 0)
                            for k in set(a_row.init_balance) | set(account.init_balance) }

            else:
                objects.append(account)

        if analytic_codes:
            objects.extend([a_item[1] for a_item in
                            sorted(analytic_groups.items())])

        self.localcontext.update({
            'fiscalyear': fiscalyear,
            'start_date': start_date,
            'stop_date': stop_date,
            'start_period': start_period,
            'stop_period': stop_period,
            'chart_account': chart_account,
            'allocated': self.alloc_enum[allocated],
            'initial_balance_mode': initial_balance_mode,
            'account_range_filter': account_range_filter,
            'currency_filter': curr_name if currency_filter else None,
            'analytic_codes': analytic_dim if analytic_codes else None,
        })

        return super(GeneralLedgerWebkit, self).set_context(objects, data, new_ids,
                                                            report_type=report_type)

    def _check_allocated(self, account, line, allocated):
        if allocated == 'all':
            return True  # Show everything.

        if allocated == 'allocated':
            return account.reconcile and (
                line.get('fullrec') or line.get('partialrec'))

        if allocated == 'not_allocated':
            return ((not account.reconcile) or
                    (not line.get('fullrec')) or
                    line.get('partialrec'))

        if allocated == 'partial':
            return (account.reconcile and
                    (not line.get('fullrec')) and
                    line.get('partialrec'))

        return False


HeaderFooterTextWebKitParser('report.account.account_report_general_ledger_webkit',
                             'account.account',
                             'addons/account_report_webkit/report/templates/account_report_general_ledger.mako',
                             parser=GeneralLedgerWebkit)
