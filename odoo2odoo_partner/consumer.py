# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.addons.odoo2odoo_backend.backend import odoo
from openerp.addons.odoo2odoo_backend.unit.binder import OdooModelBinder
from openerp.addons.odoo2odoo_backend.unit.backend_adapter \
    import GenericCRUDAdapter


@odoo
class ResPartnerSyncAdapter(GenericCRUDAdapter):
    _model_name = ["odoo.res.partner"]


@odoo
class ResPartnerSyncBinder(OdooModelBinder):
    _model_name = ["odoo.res.partner"]


@odoo
class ResCompanySyncAdapter(GenericCRUDAdapter):
    _model_name = ["odoo.res.company"]
    _external_model = "res.company"


@odoo
class ResCompanySyncBinder(OdooModelBinder):
    _model_name = ["odoo.res.company"]
