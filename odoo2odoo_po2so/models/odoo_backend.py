# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
import logging
from openerp import models, fields, api, _
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.odoo2odoo_backend.unit.import_synchronizer import import_batch
from openerp.exceptions import Warning as UserError
from .sale_order import import_so_batch
_logger = logging.getLogger(__name__)


class OdooBackend(models.Model):
    _inherit = "odoo.backend"

    po_partner_id = fields.Many2one(
        string="External Supplier",
        comodel_name="res.partner",
    )

    @api.multi
    @api.depends(
        "po_partner_id",
        "po_partner_id.odoo_bind_ids",
        "po_partner_id.odoo_bind_ids.external_odoo_id",
    )
    def _compute_external_partner_id(self):
        obj_odoo_res_partner =\
            self.env["odoo.res.partner"]

        for document in self:
            if document.po_partner_id:
                odoo_partner_ids =\
                    obj_odoo_res_partner.search([
                        ("odoo_id", "=", document.po_partner_id.id)
                    ])
                document.external_partner_id =\
                    odoo_partner_ids.external_odoo_id

    external_partner_id = fields.Integer(
        string="External Partner ID",
        compute="_compute_external_partner_id",
        store=True,
        default=0,
    )
    import_po_date_start = fields.Datetime(
        string="Purchase Date Start",
        required=False,
        default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    import_po_date_end = fields.Datetime(
        string="Purchase Date End",
        required=False,
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
            if self.import_additional_domain:
                add_domain =\
                    eval(self.import_additional_domain)
                if isinstance(add_domain, list):
                    if isinstance(add_domain[0], tuple):
                        domain += add_domain
                        message =\
                            "Domain %s" % (
                                domain)
                        self.write({
                            "import_po2so_info": message
                        })
                    else:
                        message =\
                            "Format domain must be tuple inside a list"
                        self.write({
                            "import_po2so_info": message
                        })
                        result = False
                else:
                    message =\
                        "Format domain must be tuple inside a list"
                    self.write({
                        "import_po2so_info": message
                    })
                    result = False
        else:
            domain.append(
                ("partner_id", "=", 0)
            )
            self.write({
                "import_po2so_info": u"External Partner ID is not define"
            })
            result = False
        return result, domain

    @api.model
    def import_po_to_so(self):
        """ Import purchase orders from external system """
        session = ConnectorSession(self.env.cr, self.env.uid,
                                   context=self.env.context)

        backend_ids = self.search([("active", "=", True)])

        for backend in backend_ids:
            result, domain = backend._get_domain_import()
            if result:
                import_so_batch.delay(
                    session,
                    "odoo.sale.order",
                    backend.id,
                    priority=1)
                import_batch(session, "odoo.sale.order",
                             backend.id, domain)
        return True
