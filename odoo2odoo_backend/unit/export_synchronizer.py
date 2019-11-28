# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openerp.addons.connector.unit.synchronizer import Exporter
from openerp.addons.connector.queue.job import job

from ..connector import get_environment, create_binding

from openerp.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)


class OdooExporter(Exporter):
    _model_name = []
    _raw_mode = False

    def run(self, binding_id):
        """Run the synchronization (create or update the external Odoo record).
        Returns `True` if the record has been exported.
        """
        binding = self.model.browse(binding_id)
        if not self.check_no_export_record(binding):
            _logger.info(
                u"[No Export]%s - Skipping export for binding record '%s'",
                binding.backend_id.name, binding)
            return
        if not self.check_export(binding):
            _logger.info(
                u"%s - Skipping export for binding record '%s'",
                binding.backend_id.name, binding)
            return
        if not self.check_sync_policy(binding):
            _logger.info(
                u"[Policy]%s - Skipping export for binding record '%s'",
                binding.backend_id.name, binding)
            return
        return self.export_record(binding)

    """Write By OpenSynergy Indonesia November 2019"""
    """============================================"""
    def _prepare_criteria_policy(self, model_name):
        return [
            ('backend_id', '=', self.backend_record.id),
            ("model_id", "=", str(model_name)),
            ("active", "=", True),
        ]

    def _get_record_binding_model(self, binding):
        model_name =\
            getattr(binding, "_model")
        return model_name

    def _get_record_model(self, binding):
        model_name =\
            getattr(binding.odoo_id, "_model")
        return model_name

    def _get_no_export_field(self, binding):
        field_name =\
            getattr(binding.odoo_id, "_no_export_field")
        return field_name

    def _get_localdict(self, model_name, odoo_id):
        object = self.env[str(model_name)].browse(
            [odoo_id]
        )[0]

        return {
            "record": object
        }

    def check_sync_policy(self, binding):
        """Check if the binding record should be exported."""

        """Write By OpenSynergy Indonesia November 2019"""
        """============================================"""
        result = True
        obj_sync_policy =\
            self.env["base.sync.policy"]
        binding_model_name =\
            self._get_record_binding_model(binding)
        model_name =\
            self._get_record_model(binding)
        localdict =\
            self._get_localdict(
                model_name,
                binding.odoo_id.id)
        criteria =\
            self._prepare_criteria_policy(binding_model_name)
        sync_policy =\
            obj_sync_policy.search(criteria)

        if sync_policy:
            try:
                _logger.info(
                    u"%s - Executing python condition",
                    sync_policy.name)
                eval(sync_policy.python_condition,
                     localdict, mode="exec", nocopy=True)
                result = localdict["result"]

            except Exception, e:
                _logger.info(
                    u"Error %s",
                    str(e))
                result = False
        return result

    def check_no_export_record(self, binding):
        result = True
        try:
            f_no_export =\
                self._get_no_export_field(binding)
        except:
            f_no_export = False

        if f_no_export:
            no_export =\
                binding.odoo_id.mapped(str(f_no_export))

        if no_export[0]:
            return False

        return result
        """============================================"""

    def check_export(self, binding):
        """Check if the binding record should be exported."""

        return True

    def export_record(self, binding):
        """Export the binding record and its dependencies."""
        self.export_m2o_dependencies(binding)
        if not binding.external_odoo_id:
            self.match_external_record(binding)
        if binding.external_odoo_id:
            self.update_record(binding)
        else:
            self.create_record(binding)
        return True

    def match_external_record(self, binding):
        """Try to match an external record with the one to export, and update
        the external Odoo ID for the current binding.

        By default this method do nothing, but it should be overriden to avoid
        the duplication of some records (e.g. Units of Mesure,
        Product Categories...).
        """
        pass

    def update_record(self, binding):
        mapped_record = self.mapper.map_record(binding)
        data = mapped_record.values()
        if self._raw_mode:
            self.backend_adapter.raw_write([binding.external_odoo_id], data)
        else:
            self.backend_adapter.write([binding.external_odoo_id], data)
        return True

    def create_record(self, binding):
        mapped_record = self.mapper.map_record(binding)
        data = mapped_record.values(for_create=True)
        if self._raw_mode:
            external_id = self.backend_adapter.raw_create(data)
        else:
            external_id = self.backend_adapter.create(data)
        self.binder.bind(external_id, binding.id)
        return external_id

    def export_m2o_dependencies(self, binding):
        """Export all Many2one dependencies related to the record to export."""
        record = binding.odoo_id
        external_fields_data = self._external_fields_get()
        model2binding = self.backend_record.get_model_bindings()
        for field_name, field_data in external_fields_data.iteritems():
            is_m2o = self._check_many2one(field_name, field_data)
            if is_m2o:
                relation = field_data['relation']
                if relation not in model2binding:
                    continue
                dependencies = getattr(record, field_name)
                for dependency in dependencies:
                    # Create the binding for the dependency record
                    # if it does not exist.
                    # In any case this will trigger an export of the dependency
                    binding_model = model2binding[dependency._name]
                    dependency_binding = self.env[binding_model].search(
                        [('backend_id', '=', self.backend_record.id),
                         ('odoo_id', '=', dependency.id)])
                    if not dependency_binding:
                        dependency_binding = create_binding(
                            self.session,
                            dependency._name, dependency.id,
                            self.backend_record.id)
                    self._export_dependency(dependency_binding)

    def _export_dependency(self, binding, exporter_class=None):
        if not binding:
            return
        if exporter_class is None:
            exporter_class = OdooExporter
        exporter = self.unit_for(exporter_class, model=binding._name)
        return exporter.run(binding.id)

    def _external_fields_get(self):
        return self.backend_adapter.execute('fields_get', [])

    def _check_many2one(self, field_name, field_data):
        return field_data['type'] in ('many2one', 'reference')


@job(default_channel='root.o2o')
def export_binding(session, model_name, binding_id):
    """Export a binding record on Odoo."""
    binding = session.env[model_name].browse(binding_id)
    backend_id = binding.backend_id.id
    env = get_environment(session, model_name, backend_id)
    exporter = env.get_connector_unit(OdooExporter)
    _logger.info(
        u"%s - Exporting binding record '%s'...",
        binding.backend_id.name, binding)
    exporter.run(binding_id)


# Deprecated, kept for backward compatibility.
export_record = export_binding
