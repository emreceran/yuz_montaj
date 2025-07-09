# yuz_montaj/models/montaj_emri.py
from odoo import models, fields, api


class MontajEmri(models.Model):
    _name = 'montaj.emri'
    _description = 'Montaj Emri'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Montaj Emri Referansı', required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('yuz.montaj.emri.sequence'))

    project_id = fields.Many2one('project.project', string='Proje', required=True, ondelete='restrict', tracking=True)
    task_id = fields.Many2one('project.task', string='Görev', ondelete='restrict',
                              domain="[('project_id', '=', project_id)]", tracking=True)

    employee_id = fields.Many2one('hr.employee', string='Montaj Personeli', required=True, tracking=True,
                                  default=lambda self: self.env.user.employee_id.id)

    unit_amount = fields.Float(string='Montaj Adeti', required=True, default=0.0, tracking=True) # String "Montaj Adeti" olarak kaldı

    date = fields.Date(string='Tarih', required=True, default=fields.Date.context_today, tracking=True)

    description = fields.Text(string='Açıklama')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('yuz.montaj.emri.sequence') or '/'
        return super(MontajEmri, self).create(vals)

    # <-- action_increase_unit_amount ve action_decrease_unit_amount metotları KALDIRILDI -->