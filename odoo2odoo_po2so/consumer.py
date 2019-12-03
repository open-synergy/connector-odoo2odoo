# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.addons.odoo2odoo_backend.backend import odoo
from openerp.addons.odoo2odoo_backend.unit.binder import OdooModelBinder
from openerp.addons.odoo2odoo_backend.unit.backend_adapter \
    import GenericCRUDAdapter
from openerp.addons.odoo2odoo_backend.unit.mapper \
    import (OdooImportMapper, mapping)
from openerp.addons.odoo2odoo_backend.unit.import_synchronizer import (
    OdooImporter, DirectBatchOdooImporter, DelayedBatchOdooImporter)


@odoo
class SaleOrderSyncAdapter(GenericCRUDAdapter):
    _model_name = ["odoo.sale.order"]
    _external_model = "purchase.order"


@odoo
class OdooSyncBinder(OdooModelBinder):
    _model_name = ["odoo.sale.order"]


@odoo
class SaleOrderSyncDirectBatchImporter(DirectBatchOdooImporter):
    _model_name = ["odoo.sale.order"]


@odoo
class SaleOrderSyncImporter(OdooImporter):
    _model_name = ["odoo.sale.order"]
    _raw_mode = True
    _cross_model = True

@odoo
class SaleOrderSyncImportMapper(OdooImportMapper):
    _model_name = "odoo.sale.order"

    @mapping
    def partner_id(self, record):
        return {'partner_id': 1}

    @mapping
    def pricelist_id(self, record):
        return {'pricelist_id': 1}

    @mapping
    def partner_invoice_id(self, record):
        return {'partner_invoice_id': 1}

    @mapping
    def partner_shipping_id(self, record):
        return {'partner_shipping_id': 1}
