# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openerp import models, fields


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line"]
    _no_export_field = "no_export"

    odoo_bind_ids = fields.One2many(
        comodel_name="odoo.sale.order.line",
        inverse_name="odoo_id",
        string="Odoo Bindings",
        readonly=True
    )
    no_export = fields.Boolean(
        string="Exclude From Export",
        default=True,
    )


class OdooSaleOrderLine(models.Model):
    _name = "odoo.sale.order.line"
    _inherit = "odoo.binding"
    _inherits = {"sale.order.line": "odoo_id"}
    _description = "Sale Order Lines Binding"

    odoo_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Order Line ID",
        required=True,
        ondelete="cascade"
    )
