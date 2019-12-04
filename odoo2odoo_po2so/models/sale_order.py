# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openerp import models, fields


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
