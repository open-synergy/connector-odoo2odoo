# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import models, fields, api
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.odoo2odoo_backend.unit.import_synchronizer import import_batch
_logger = logging.getLogger(__name__)


class OdooBackend(models.Model):
    _inherit = "odoo.backend"

    @api.model
    def import_po_to_so(self):
        """ Import purchase orders from external system """
        session = ConnectorSession(self.env.cr, self.env.uid,
                                   context=self.env.context)

        backend_ids = self.search([("active", "=", True)])

        for backend in backend_ids:
            filters = []
            # filters = backend.import_product_domain_filter
            if filters and isinstance(filters, str):
                filters = eval(filters)

            import_batch(session, "odoo.sale.order",
                         backend.id, filters)
        return True
