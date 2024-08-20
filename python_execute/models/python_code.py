# -*- coding: utf-8 -*-
###################################################################################

# Author       :  A & M
# Copyright(c) :  2024-Present.
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

###################################################################################

import io
import sys
from datetime import datetime
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class PythonCodeExecute(models.Model):
    _name = 'python.code.execute'
    _description = 'Python Code Execute'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "code_name"

    code_name = fields.Char(string='Identifier', help="Identifier", tracking=True)
    execute_code = fields.Text(string='Code', help="Code to Execute", tracking=True, default="\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    code_result = fields.Html(string='Output', help="Output of the Execute Code")
    code_state = fields.Selection([('draft', 'New'), ('done', 'Verified')], string='Code Status', default='draft', tracking=True)
    modified_uid = fields.Many2one('res.users', string='Modified By')
    last_execute = fields.Datetime(string='Last Execute On')

    def action_verify_code(self):
        for record in self:
            record.modified_uid = record.env.user.id
            record.code_state = 'done'
            record.code_result = ''

    def action_back_to_draft(self):
        for record in self:
            record.code_state = 'draft'
            record.code_result = ''

    def action_execute_code(self):
        try:
            output_capture = io.StringIO()
            sys.stdout = output_capture
            for record in self:
                compiled_code = compile(record.execute_code, 'something', 'exec')
                exec(compiled_code)
                sys.stdout = sys.__stdout__
                captured_output = output_capture.getvalue()
                record.code_result = captured_output
                record.last_execute = datetime.now()
            message = f"{self.env.user.partner_id.name} executed the following code: '{self.execute_code}'."
            self.sudo().message_post(
                body=message,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )
        except Exception as error:
            raise ValidationError(_(f"Python Execution Error :\n{error}"))
