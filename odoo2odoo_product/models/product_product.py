# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product"]
    _no_export_field = "no_export_product"

    odoo_bind_ids = fields.One2many(
        "odoo.product.product",
        inverse_name="odoo_id",
        string=u"Odoo Bindings",
        readonly=True)

    no_export_product = fields.Boolean(
        string="Exclude Product From Export",
        default=True,
    )


class OdooProductProduct(models.Model):
    _name = "odoo.product.product"
    _inherit = "odoo.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "Product Binding"

    odoo_id = fields.Many2one(
        "product.product",
        string=u"Product",
        required=True,
        ondelete="cascade")
