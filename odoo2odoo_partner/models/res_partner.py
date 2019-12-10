# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openerp import models, fields


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner"]
    _no_export_field = "no_export"

    odoo_bind_ids = fields.One2many(
        comodel_name="odoo.res.partner",
        inverse_name="odoo_id",
        string="Odoo Bindings",
        readonly=True
    )
    no_export = fields.Boolean(
        string="Exclude From Export",
        default=True,
    )


class OdooResPartner(models.Model):
    _name = "odoo.res.partner"
    _inherit = "odoo.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "Partner Binding"

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="cascade"
    )
