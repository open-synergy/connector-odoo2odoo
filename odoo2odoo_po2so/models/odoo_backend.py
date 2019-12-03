# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
import logging
from openerp import models, fields, api
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.odoo2odoo_backend.unit.import_synchronizer import import_batch
_logger = logging.getLogger(__name__)


class OdooBackend(models.Model):
    _inherit = "odoo.backend"

    external_partner_id = fields.Integer(
        string="External Partner ID"
    )
    import_po_date_start = fields.Datetime(
        string="Purchase Date Start",
        required=True,
        default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    import_po_date_end = fields.Datetime(
        string="Purchase Date End",
        required=True,
        default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    import_additional_domain = fields.Char(
        string='Additional Domain',
    )
    import_po2so_info = fields.Text(
        string="Import Information",
        readonly=True,
    )

    @api.multi
    def _get_domain_import(self):
        self.ensure_one()
        result = True
        domain = []
        if self.external_partner_id:
            domain.append(
                ("partner_id", "=", self.external_partner_id)
            )
        else:
            self.write({
                "import_po2so_info": u"External Partner ID is not define"
            })
            result = False

        return result, str(domain)

    @api.model
    def import_po_to_so(self):
        """ Import purchase orders from external system """
        session = ConnectorSession(self.env.cr, self.env.uid,
                                   context=self.env.context)

        backend_ids = self.search([("active", "=", True)])

        for backend in backend_ids:
            result, domain = backend._get_domain_import()
            if result:
                if domain and isinstance(domain, str):
                    domain = eval(domain)
                    import_batch(session, "odoo.sale.order",
                                 backend.id, domain)
        return True
