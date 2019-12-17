# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from openerp.addons.odoo2odoo_backend.backend import odoo
from openerp.addons.odoo2odoo_backend.unit.binder import OdooModelBinder
from openerp.addons.odoo2odoo_backend.unit.backend_adapter \
    import GenericCRUDAdapter
from openerp.addons.connector.unit.mapper import (
    mapping, ImportMapper, follow_m2o_relations, ImportMapChild)
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
class SaleOrderSyncDelayedBatchImporter(DelayedBatchOdooImporter):
    _model_name = ["odoo.sale.order"]

    def _import_records(self, record_id, **kwargs):
        """ Import the record directly """
        return super(SaleOrderSyncDelayedBatchImporter, self)._import_records(
            record_id, max_retries=0, priority=5)

    def run(self, domain=None):
        if not domain:
            domain = []
        record_ids =\
            self.backend_adapter.search(domain)
        _logger.debug('search data %s returned %s',
                     domain, record_ids)
        for record_id in record_ids:
            self._import_records(record_id)

@odoo
class SaleOrderSyncImporter(OdooImporter):
    _model_name = ["odoo.sale.order"]
    _cross_model = True

    def __init__(self, connector_env):
        super(SaleOrderSyncImporter, self).__init__(connector_env)
        self.map_so_data = None
        self.map_so_line_data = None

    def _import_record(self, external_id):
        binding_so = False
        record_data =\
            self._get_external_data(external_id)
        binding = self._get_binding(external_id, record_data)

        map_record = self._map_data(record_data)

        self.map_so_data =\
            self._prepare_data_so(map_record)
        self.map_so_line_data =\
            self._prepare_data_so_line(map_record)

        check_so =\
            self.check_import(external_id, self.map_so_data, binding)

        if not check_so:
            _logger.debug(
                u"%s - Skipping import Sales Order (%s,%s)",
                self.backend_record.name, self.model._name, external_id)

        lock_name = 'import({}, {}, {}, {})'.format(
            self.backend_record._name,
            self.backend_record.id,
            self.model._name,
            external_id,
        )
        self.advisory_lock_or_retry(lock_name)
        self._before_import(external_id, record_data, binding)
        self._import_dependencies(external_id, record_data, binding)

        if self.map_so_data:
            if binding.external_odoo_id and check_so:
                self.update_record(binding, self.map_so_data)
            else:
                binding_so = self.create_record(
                    external_id, self.map_so_data
                )

        if binding_so:
            so_id = binding_so.id
        else:
            so_id = binding.id

        if self.map_so_line_data and so_id:
            self.import_record_line(
                so_id, self.map_so_line_data
            )

        self._after_import(binding)
        return True

    def _prepare_data_so(self, record):
        result = {}
        map_so = record.values()
        if "odoo_order_line_ids" in map_so:
            del map_so["odoo_order_line_ids"]
            result = map_so
        return result

    def _prepare_data_so_line(self, record):
        result = []
        map_so = record.values()
        if "odoo_order_line_ids" in map_so:
            for m1, m2, line in map_so["odoo_order_line_ids"]:
                result.append(line)
        return result

    def create_record(self, external_id, record_data):
        model = self.model.with_context(connector_no_export=True)
        record_data['backend_id'] = self.backend_record.id
        binding = model.create(record_data)
        self.binder.bind(external_id, binding.id)
        _logger.debug(
            u"%s - Binding record '%s' imported (created)",
            self.backend_record.name, binding)
        return binding

    def import_record_line(self, so_id, record_data):
        for data in record_data:
            external_id =\
                data["external_odoo_id"]
            importer = self.unit_for(
                SaleOrderLineSyncImporter,
                model="odoo.sale.order.line")
            importer._import_record(external_id, so_id)
        return

@odoo
class SaleOrderLineSyncImporter(OdooImporter):
    _model_name = ["odoo.sale.order.line"]
    _cross_model = True

    def _import_record(self, external_id, so_id):
        record_data =\
            self._get_external_data(external_id)
        binding = self._get_binding(external_id, record_data)
        if not self.check_import(external_id, record_data, binding):
            _logger.debug(
                u"%s - Skipping import Sales Order Line(%s,%s)",
                self.backend_record.name, self.model._name, external_id)
            return
        lock_name = 'import({}, {}, {}, {})'.format(
            self.backend_record._name,
            self.backend_record.id,
            self.model._name,
            external_id,
        )
        self.advisory_lock_or_retry(lock_name)
        self._before_import(external_id, record_data, binding)
        self._import_dependencies(external_id, record_data, binding)
        map_record = self._map_data(record_data)
        if binding.external_odoo_id:
            record = self._update_data(map_record)
            self.update_record(binding, record)
        else:
            record = self._create_data(map_record)
            self.create_record(so_id, external_id, record)
        self._after_import(binding)
        return True

    def create_record(self, so_id, external_id, record_data):
        model = self.model.with_context(connector_no_export=True)
        record_data['backend_id'] = self.backend_record.id
        record_data['odoo_order_id'] = so_id
        binding = model.create(record_data)
        self.binder.bind(external_id, binding.id)
        _logger.debug(
            u"%s - Binding record '%s' imported (created)",
            self.backend_record.name, binding)
        return binding


@odoo
class SaleOrderSyncImportMapper(ImportMapper):
    _model_name = "odoo.sale.order"

    children = [
        ("order_line", "odoo_order_line_ids", "odoo.sale.order.line"),
    ]

    @mapping
    def origin(self, record):
        return {
            "origin": record["name"]
        }

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        source = map_record.source
        order_id = source["id"]
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
        return items

    @mapping
    def partner_id(self, record):
        adapter = self.unit_for(GenericCRUDAdapter, "odoo.res.company")
        company_ids = adapter.read(record["company_id"][0])
        external_partner_id = company_ids["partner_id"][0]
        binder = self.binder_for("odoo.res.partner")
        partner_id = binder.to_openerp(external_partner_id)
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
        ("product_qty", "product_uom_qty"),
    ]

    @mapping
    def product_id(self, record):
        binder = self.binder_for("odoo.product.product")
        product_id = binder.to_openerp(record["product_id"][0], unwrap=True)
        if product_id:
            return {"product_id": product_id.id}

    @mapping
    def external_odoo_id(self, record):
        return {"external_odoo_id": record["id"]}
