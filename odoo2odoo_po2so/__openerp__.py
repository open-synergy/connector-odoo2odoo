# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Odoo2Odoo - Import PO to SO",
    "version": "8.0.2.1.0",
    "category": "Connector Managements",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "odoo2odoo_product",
        "odoo2odoo_partner",
        "sale",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "views/sale_order_views.xml",
        "views/backend.xml",
    ],
}
