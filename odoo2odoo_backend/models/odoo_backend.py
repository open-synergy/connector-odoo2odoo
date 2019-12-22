# -*- coding: utf-8 -*-
# Copyright 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import urlparse

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.connector import ConnectorEnvironment

from ..unit.backend_adapter import CheckAuth, GenericAPIAdapter
from ..backend import odoo
from ..exceptions import O2OConnectionError

_logger = logging.getLogger(__name__)


def extract_url_data(url):
    url_data = urlparse.urlparse(url)
    return {
        "scheme": url_data.scheme,
        "hostname": url_data.hostname,
        "port": url_data.port or (url_data.scheme == "https" and 443) or 80,
    }


class OdooBackend(models.Model):
    _name = 'odoo.backend'
    _description = u"Odoo Backend"
    _inherit = 'connector.backend'
    _backend_type = 'odoo'

    active = fields.Boolean(
        string="Active",
        readonly=True,
        default=False
    )
    version = fields.Selection(
        string="Version",
        selection="select_versions",
        required=True
    )
    location = fields.Char(
        string="Location",
        required=True
    )
    hostname = fields.Char(
        string="Hostname",
        compute="_compute_url_data",
        store=True
    )
    protocol = fields.Char(
        string="Protocol",
        compute="_compute_url_data",
        store=True
    )
    port = fields.Integer(
        string="Port",
        compute="_compute_url_data",
        store=True
    )
    database = fields.Char(
        string="Database",
        required=True
    )
    username = fields.Char(
        string="Username",
        required=True
    )
    password = fields.Char(
        string="Password",
        required=True
    )

    @api.multi
    def _compute_allowed_model_ids(self):
        obj_ir_model =\
            self.env["ir.model"]

        for document in self:
            try:
                model_binding_ids =\
                    document.get_model_bindings().values()
            except:  # noqa: E722
                model_binding_ids = []

            criteria = [
                ("model", "in", model_binding_ids)
            ]
            model_ids =\
                obj_ir_model.search(criteria)
            document.allowed_model_ids = model_ids.ids

    allowed_model_ids = fields.Many2many(
        string="Allowed Models",
        comodel_name="ir.model",
        compute="_compute_allowed_model_ids",
        store=False,
    )
    sync_policy_ids = fields.One2many(
        string="Syncronization Policy",
        comodel_name="base.sync.policy",
        inverse_name="backend_id",
    )
    connection_ok = fields.Boolean(
        string="Connection Ok",
        readonly=True,
    )
    connection_info = fields.Text(
        string="Connection Information",
        readonly=True,
    )

    @api.model
    def create(self, values):
        _super = super(OdooBackend, self)
        result = _super.create(values)
        if not self.connection_ok:
            message = "You need to check the connection "\
                      "to activate this server"
            result.write({
                "active": False,
                "connection_info": message,
            })
        return result

    @api.multi
    def deactivated(self):
        for document in self:
            message = "Deactivated By %s" % (
                self.env.user.name)
            return document.write({
                "connection_ok": False,
                "active": False,
                "connection_info": message,
            })

    @api.constrains(
        "location",
        "database"
    )
    def _check_location_database(self):
        if self.location and self.database:
            strWarning = _("No duplicate location and database")
            criteria = [
                ("location", "=", self.location),
                ("database", "=", self.database)
            ]
            check_data =\
                self.search(criteria)
            if len(check_data) > 0:
                raise UserError(strWarning)

    @api.multi
    @api.depends(
        "location"
    )
    def _compute_url_data(self):
        for backend in self:
            url_data = extract_url_data(backend.location)
            self.hostname = url_data["hostname"]
            self.port = url_data["port"]
            self.protocol = \
                url_data["scheme"] == "https" and "jsonrpc+ssl" or "jsonrpc"

    @api.model
    def select_versions(self):
        """ Available versions in the backend.
        Can be inherited to add custom versions. Using this method
        to add a version from an ``_inherit`` does not constrain
        to redefine the ``version`` field in the ``_inherit`` model.
        """
        return [
            ("8.0", "8.0"),
            ("9.0", "9.0"),
        ]

    @api.multi
    def _get_api_adapter(self):
        """Get an adapter to test the backend connection."""
        self.ensure_one()
        session = ConnectorSession(self._cr, self._uid, context=self._context)
        environment = ConnectorEnvironment(self, session, self._name)
        return environment.get_connector_unit(CheckAuth)

    @api.multi
    def check_auth(self):
        for document in self:
            message = u"Check authentication on Server %s (%s)" % (
                document.name, document.location)
            user_info = "Checked By %s" % (
                self.env.user.name)
            try:
                self._get_api_adapter()
            except O2OConnectionError as exc:
                return document.write({
                    "connection_ok": False,
                    "active": False,
                    "connection_info": u"%s\n%s: %s" % (
                        user_info, message, exc),
                })
            return document.write({
                "connection_ok": True,
                "active": True,
                "connection_info": u"%s\n%s: OK" % (user_info, message),
            })

    @api.multi
    def get_model_bindings(self):
        """Return the mapping between the data models and their corresponding
        bindings involved in the synchronization. E.g.:

            {
                'product.uom.categ': 'odoo.product.uom.categ',
                'product.uom': 'odoo.product.uom',
                'product.template': 'odoo.product.template',
                'product.product': 'odoo.product.product',
            }

        This is used by the synchronizers to allow the import/export
        of a record.

        This method must be implemented.
        """
        raise NotImplementedError


@odoo
class GenericCheckAuth(CheckAuth, GenericAPIAdapter):
    _model_name = "odoo.backend"
