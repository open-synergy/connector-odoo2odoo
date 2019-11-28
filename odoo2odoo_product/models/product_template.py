# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template"]
    _no_export_field = "no_export_tmpl"

    odoo_bind_ids = fields.One2many(
        comodel_name="odoo.product.template",
        inverse_name="odoo_id",
        string="Odoo Bindings",
        readonly=True
    )
    no_export_tmpl = fields.Boolean(
        string="Exclude Template From Export",
        default=True,
    )


class OdooProductTemplate(models.Model):
    _name = "odoo.product.template"
    _inherit = "odoo.binding"
    _inherits = {"product.template": "odoo_id"}
    _description = "Product Template Binding"

    odoo_id = fields.Many2one(
        comodel_name="product.template",
        string="Product",
        required=True,
        ondelete="cascade"
    )
