# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Odoo2Odoo - Partner",
    "version": "8.0.1.0.0",
    "category": "Connector Managements",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base",
        "odoo2odoo_backend",
    ],
    "data": [
        "views/odoo_res_partner.xml",
        "views/res_partner_views.xml",
    ],
}
