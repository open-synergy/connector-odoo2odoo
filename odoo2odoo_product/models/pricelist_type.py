# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from openerp import models, fields
from openerp.addons.odoo2odoo_backend.backend import odoo
from ..consumer import OdooSyncExporter
logger = logging.getLogger(__name__)


class ProductPricelistType(models.Model):
    _name = "product.pricelist.type"
    _inherit = ["product.pricelist.type"]
    _no_export_field = "no_export"

    odoo_bind_ids = fields.One2many(
        string="Odoo Bindings",
        comodel_name="odoo.product.pricelist.type",
        inverse_name="odoo_id",
        readonly=True
    )
    no_export = fields.Boolean(
        string="Exclude From Export",
        default=True,
    )


class OdooProductPricelistType(models.Model):
    _name = "odoo.product.pricelist.type"
    _inherit = "odoo.binding"
    _inherits = {"product.pricelist.type": "odoo_id"}
    _description = "Product Pricelist Type Binding"

    odoo_id = fields.Many2one(
        string="Pricelist Type",
        comodel_name="product.pricelist.type",
        required=True,
        ondelete="cascade"
    )


@odoo(replacing=OdooSyncExporter)
class OdooProductPricelistTypeExporter(OdooSyncExporter):
    _model_name = "odoo.product.pricelist.type"

    def match_external_record(self, binding):
        """Try to match the local record with a remote one."""
        # Get all languages supported and ensure that 'en_US' is the last one
        # (last resort value if we do not find the corresponding translated
        # record, less error prones)
        obj_res_lang = self.env["res.lang"]
        lang_codes =\
            obj_res_lang.search([]).mapped("code")
        lang_codes.pop(lang_codes.index("en_US"))
        lang_codes.append("en_US")
        # Try to find a remote record corresponding to the local one
        for lang_code in lang_codes:
            record_name =\
                binding.with_context(lang=lang_code).name
            logger.debug(
                u"%s - Try to match the Pricelist Type '%s' (lang='%s')...",
                self.backend_record.name, record_name, lang_code)
            self.backend_adapter.odoo_session.env.context["lang"] = lang_code
            external_ids = self.backend_adapter.search([
                ("name", "=", record_name)
            ])
            # Exclude record IDs already bound
            already_bound_external_ids = self.env[self._model_name].search([
                ("external_odoo_id", "in", external_ids)
            ]).mapped("external_odoo_id")
            external_ids = [id_ for id_ in external_ids
                            if id_ not in already_bound_external_ids]
            external_id = external_ids and external_ids[0] or False
            if external_id:
                data = self.backend_adapter.read([external_id], ["name"])[0]
                logger.debug(
                    u"%s - Pricelist Type '%s' (ID=%s) matches with "
                    u"the external Pricelist Type '%s' (ID=%s)",
                    self.backend_record.name,
                    record_name, binding.odoo_id.id,
                    data["name"], external_id)
                binding.with_context(
                    connector_no_export=True).external_odoo_id = external_id
                break
        self.backend_adapter.odoo_session.env.context.clear()
