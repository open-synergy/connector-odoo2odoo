# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class BaseSyncPolicy(models.Model):
    _name = "base.sync.policy"
    _description = "Base Syncronize Policy"

    name = fields.Char(
        string="Name",
        required=True,
    )

    @api.model
    def _default_backend_id(self):
        active_id =\
            self.env.context.get("backend_id", False)
        return active_id

    backend_id = fields.Many2one(
        string="#Backend",
        comodel_name="odoo.backend",
        default=lambda self: self._default_backend_id(),
        required=True,
        readonly=True,
    )
    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        required=True,
    )
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
