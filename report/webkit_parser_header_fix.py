# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
#
# Author: Guewen Baconnier (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import logging


from openerp.addons.report_webkit import webkit_report

_logger = logging.getLogger('financial.reports.webkit')

# Class used only as a workaround to bug:
# http://code.google.com/p/wkhtmltopdf/issues/detail?id=656

# html headers and footers do not work on big files (hundreds of pages) so we replace them by
# text headers and footers passed as arguments to wkhtmltopdf
# this class has to be removed once the bug is fixed

# in your report class, to print headers and footers as text, you have to add them in the localcontext with a key 'additional_args'
# for instance:
#        header_report_name = _('PARTNER LEDGER')
#        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)
#        self.localcontext.update({
#            'additional_args': [
#                ('--header-font-name', 'Helvetica'),
#                ('--footer-font-name', 'Helvetica'),
#                ('--header-font-size', '10'),
#                ('--footer-font-size', '7'),
#                ('--header-left', header_report_name),
#                ('--footer-left', footer_date_time),
#                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
#                ('--footer-line',),
#            ],
#        })


class HeaderFooterTextWebKitParser(webkit_report.WebKitParser):

    # neutralize previous patch
    pass
