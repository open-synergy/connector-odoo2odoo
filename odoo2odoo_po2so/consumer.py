# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.addons.odoo2odoo_backend.backend import odoo
from openerp.addons.odoo2odoo_backend.unit.backend_adapter \
    import GenericCRUDAdapter
from openerp.addons.odoo2odoo_backend.unit.mapper \
    import OdooImportMapper
from openerp.addons.odoo2odoo_backend.unit.import_synchronizer import (
    OdooImporter, DirectBatchOdooImporter, DelayedBatchOdooImporter)


@odoo
class SaleOrderSyncAdapter(GenericCRUDAdapter):
    _model_name = ["odoo.sale.order"]
    _external_model = "purchase.order"


@odoo
class SaleOrderSyncImportMapper(OdooImportMapper):
    _model_name = "odoo.sale.order"

@odoo
class SaleOrderSyncImporter(OdooImporter):
    _model_name = ["odoo.sale.order"]
    _raw_mode = True
    _cross_model = True


# @odoo
# class SaleOrderSyncDirectBatchImporter(DirectBatchOdooImporter):
#     _model_name = ["odoo.sale.order"]


@odoo
class SaleOrderSyncDelayedBatchImporter(DelayedBatchOdooImporter):
    _model_name = ["odoo.sale.order"]
