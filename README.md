### README ###


### Accounting Reports Odoo/OpenERP Webkit ###

* Based on Camp To Camp : http://bazaar.launchpad.net/~camptocamp/c2c-financial-addons/trunk/files/head:/account_financial_report_webkit/
This module adds or replaces the following standard OpenERP financial reports:

*	 - General ledger
*	 - Trial Balance (simple or comparative view)
*	 - Partner ledger
*	 - Partner balance
*	 - Open invoices report

### Requirements ###

* In order to run properly this module makes sure you have installed the
  library `wkhtmltopdf` for the pdf rendering (the library path must be
  set in a System Parameter `webkit_path`).

### Main improvements per report ###

The General ledger: details of all entries posted in your books sorted by account.

* Filter by account is available in the wizard (no need to go to the
  Chart of Accounts to do this anymore) or by View account (the report
  will display all regular children accounts) i.e. you can select all
  P&L accounts.
* The report only prints accounts with moves OR with a non
  null balance. No more endless report with empty accounts (field:
  display account is hidden)
* initial balance computation on the fly if no open entry posted
* Thanks to a new checkbox in the account form, you will have the
  possibility to centralize any account you like.  This means you do
  not want to see all entries posted under the account ‘VAT on sales’;
  you will only see aggregated amounts by periods.
* Counterpart account is displayed for each transaction (3 accounts max.)
  to ease searching.
* Better ergonomy on the wizard: important information is displayed in
  the top part, filters are in the middle, and options are in the
  bottom or on a separate tab. There is more specific filtering on
  separate tabs. No more unique wizard layout for all financial
  reports (we have removed the journal tab for the GL report)
* improved report style

The partner ledger: details of entries relative to payable &
receivable accounts posted in your books sorted by account and
partner.

* Filter by partner now available
* Now you can see Accounts then Partner with subtotals for each
  account allowing you to check you data with trial balance and
  partner balance for instance. Accounts are ordered in the same way as
  in the Chart of account
* Period have been added (date only is not filled in since date can be
  outside period)
* Reconciliation code added
* Subtotal by account
* Alphabetical sorting (same as in partner balance)

Open invoice report : other version of the partner ledger showing
unreconciled / partially reconciled entries.

* Possibility to print unreconciled transactions only at any date in
  the past (thanks to the new field: `last_rec_date` which computes
  the last move line reconciliation date). No more pain to get open
  invoices at the last closing date.
* no initial balance computed because the report shows open invoices
  from previous years.

The Trial balance: list of accounts with balances

* You can either see the columns: initial balance, debit, credit,
  end balance or compare balances over 4 periods of your choice
* You can select the "opening" filter to get the opening trial balance
  only
* If you create an extra virtual chart (using consolidated account) of
  accounts for your P&L and your balance sheet, you can print your
  statutory accounts (with comparison over years for instance)
* If you compare 2 periods, you will get the differences in values and
  in percent

The Partner balance: list of account with balances

* Subtotal by account and partner
* Alphabetical sorting (same as in partner balance)

### Limitations ###

Initial balances in these reports are based either on opening entry
posted in the opening period or computed on the fly. So make sure
that your past accounting opening entries are in an opening period.
Initials balances are not computed when using the Date filter (since a
date can be outside its logical period and the initial balance could
be different when computed by data or by initial balance for the
period). The opening period is assumed to be the Jan. 1st of the year
with an opening flag and the first period of the year must start also
on Jan 1st.
