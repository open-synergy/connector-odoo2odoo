# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from openerp.addons.odoo2odoo_backend.backend import odoo
from openerp.addons.odoo2odoo_backend.unit.binder import OdooModelBinder
from openerp.addons.odoo2odoo_backend.unit.backend_adapter \
    import GenericCRUDAdapter
from openerp.addons.connector.unit.mapper import (
    mapping, ImportMapper, follow_m2o_relations)
from openerp.addons.odoo2odoo_backend.unit.import_synchronizer import (
    OdooImporter, DirectBatchOdooImporter, DelayedBatchOdooImporter)
_logger = logging.getLogger(__name__)


@odoo
class SaleOrderSyncAdapter(GenericCRUDAdapter):
    _model_name = ["odoo.sale.order"]
    _external_model = "purchase.order"

@odoo
class SaleOrderLineSyncAdapter(GenericCRUDAdapter):
    _model_name = ["odoo.sale.order.line"]
    _external_model = "purchase.order.line"


@odoo
class SaleOrderSyncBinder(OdooModelBinder):
    _model_name = ["odoo.sale.order"]


@odoo
class SaleOrderLineSyncBinder(OdooModelBinder):
    _model_name = ["odoo.sale.order.line"]


@odoo
class SaleOrderSyncDirectBatchImporter(DirectBatchOdooImporter):
    _model_name = ["odoo.sale.order"]


@odoo
class SaleOrderSyncImporter(OdooImporter):
    _model_name = ["odoo.sale.order"]
    _cross_model = True

@odoo
class SaleOrderSyncImportMapper(ImportMapper):
    _model_name = "odoo.sale.order"

    def _get_origin(field):
        def modifier(self, record, to_attr):
            server_name =\
                self.backend_record.name
            server_name = "[" + server_name + "]"
            name = server_name + " " + record[field]
            return name
        return modifier

    direct = [
        (_get_origin("name"), "origin"),
    ]

    children = [
        ("order_line", "order_line", "odoo.sale.order.line"),
    ]

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        source = map_record.source
        child_records = source[from_attr]

        detail_records = []
        _logger.debug('Loop over children ...')
        for child_record in child_records:
            adapter = self.unit_for(GenericCRUDAdapter, model_name)

            detail_record = adapter.read(child_record)
            detail_records.append(detail_record)

        mapper = self._get_map_child_unit(model_name)

        items = mapper.get_items(
            detail_records, map_record, to_attr, options=self.options
        )

        _logger.debug('Child "%s": %s', model_name, items)

        return items

    @mapping
    def partner_id(self, record):
        adapter = self.unit_for(GenericCRUDAdapter, "odoo.res.company")
        company_ids = adapter.read(record["company_id"])
        _logger.info('COMPANY IDS:%s', company_ids["partner_id"])
        external_partner_id = company_ids["partner_id"][0]
        binder = self.binder_for("odoo.res.partner")
        partner_id = binder.to_openerp(external_partner_id)
        _logger.info('EXTERNAL ID:%s\n PARTNER ID:%s', external_partner_id, partner_id)
        if partner_id:
            return {"partner_id": partner_id.odoo_id.id}

    @mapping
    def pricelist_id(self, record):
        return {"pricelist_id": 1}

    @mapping
    def partner_invoice_id(self, record):
        return {"partner_invoice_id": 1}

    @mapping
    def partner_shipping_id(self, record):
        return {"partner_shipping_id": 1}

@odoo
class SaleOrderLineSyncImportMapper(ImportMapper):
    _model_name = "odoo.sale.order.line"

    direct = [
        ("name", "name"),
        ("price_unit", "price_unit"),
    ]

    @mapping
    def product_uom_qty(self, record):
        qty =\
            float(record.get("product_qty") or 0.0)
        return {"product_uom_qty": qty}

    @mapping
    def product_id(self, record):
        binder = self.binder_for("odoo.product.product")
        product_id = binder.to_openerp(record["product_id"][0], unwrap=True)
        if product_id:
            return {"product_id": product_id.id}
