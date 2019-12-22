# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields
from openerp.addons.connector.queue.job import job
from openerp.addons.odoo2odoo_backend.connector import get_environment
from ..consumer import SaleOrderSyncDelayedBatchImporter


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order"]
    _no_export_field = "no_export"

    odoo_bind_ids = fields.One2many(
        comodel_name="odoo.sale.order",
        inverse_name="odoo_id",
        string="Odoo Bindings",
        readonly=True
    )
    no_export = fields.Boolean(
        string="Exclude From Export",
        default=True,
    )


class OdooSaleOrder(models.Model):
    _name = "odoo.sale.order"
    _inherit = "odoo.binding"
    _inherits = {"sale.order": "odoo_id"}
    _description = "Sale Orders Binding"

    odoo_id = fields.Many2one(
        comodel_name="sale.order",
        string="Order ID",
        required=True,
        ondelete="cascade"
    )
    odoo_order_line_ids = fields.One2many(
        comodel_name='odoo.sale.order.line',
        inverse_name='odoo_order_id',
        string='Sale Order Lines'
    )


@job(default_channel='root.o2o')
def import_so_batch(session, model_name, backend_id, domain=None):
    if domain is None:
        domain = {}
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(SaleOrderSyncDelayedBatchImporter)
    importer.run(domain=domain)
