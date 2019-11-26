# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class BaseSyncPolicy(models.Model):
    _name = "base.sync.policy"
    _description = "Base Syncronize Policy"

    name = fields.Char(
        string="Name",
        required=True,
    )
    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        required=True,
    )
    """Write By OpenSynergy Indonesia November 2019"""
    """============================================"""
    backend_id = fields.Many2one(
        string="#Backend",
        comodel_name="odoo.backend",
    )
    """============================================"""
    python_condition = fields.Text(
        string="Condition",
        help="The result of executing the expresion must be "
             "a boolean.",
        default="""# Available locals:\n#  - record: current record""",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    description = fields.Text(
        string="Note",
    )
