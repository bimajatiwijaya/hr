# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.resource.models.resource import Intervals
from odoo import api, fields, models
import datetime
from dateutil import rrule
from pytz import timezone, utc


def string_to_datetime(value):
    """ Convert the given string value to a datetime in UTC. """
    return utc.localize(fields.Datetime.from_string(value))


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _get_holidays_public_leaves(self, start_dt, end_dt, employe_id, resource):
        """Get the public holidays for the current employee and given dates in
        the format expected by resource methods.

        :param: start_dt: Initial datetime.
        :param: end_dt: End datetime.
        :param: employee_id: Employee ID. It can be false.
        :return: List of tuples with (start_date, end_date) as elements.
        """
        leaves = []
        tz = timezone((resource or self).tz)
        for day in rrule.rrule(rrule.YEARLY, dtstart=start_dt, until=end_dt):
            lines = self.env['hr.holidays.public'].get_holidays_list(
                day.year, employee_id=employe_id,
            )
            for line in lines:
                date = fields.Datetime.from_string(line.date)
                dt0 = string_to_datetime(line.date).astimezone(tz)
                dt1 = string_to_datetime(line.date).astimezone(tz)
                leaves.append((max(start_dt, dt0), min(end_dt, dt1), line))
        return leaves

    @api.multi
    def _leave_intervals(self,  start_dt, end_dt, resource=None, domain=None):
        res = super(ResourceCalendar, self)._leave_intervals(
            resource=resource,
            start_dt=start_dt,
            end_dt=end_dt,
            domain=domain
        )
        print(start_dt, end_dt)
        if self.env.context.get('exclude_public_holidays'):
            res |= Intervals(self._get_holidays_public_leaves(
                start_dt, end_dt,
                self.env.context.get('employee_id', False), resource
            ))
        return res
