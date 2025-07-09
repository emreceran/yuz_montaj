from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    montaj_emri_ids = fields.One2many(
        'montaj.emri',
        'task_id',
        string='Montaj Emirleri'
    )

    talep_edilen_montaj_miktari = fields.Float(
        string='Talep Edilen Montaj Miktarı',
        default=0.0,
        tracking=True,
        digits='Product Unit of Measure'
    )

    kalan_montaj_miktari = fields.Float(
        string='Kalan Montaj Miktarı',
        compute='_compute_kalan_montaj_miktari',
        store=True,
        digits='Product Unit of Measure'
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string='İlgili Satış Siparişi',
        tracking=True,
        help="Bu görevin ilişkili olduğu satış siparişi."
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='İlgili Satış Satırı',
        domain="[('order_id', '=', sale_order_id)]",
        tracking=True,
        help="Bu görevin ilişkili olduğu satış sipariş satırı."
    )

    teslim_edilen_miktar = fields.Float(
        string='Teslim Edilen Miktar',
        compute='_compute_teslim_edilen_miktar',
        store=True,
        readonly=True,
        digits='Product Unit of Measure',
        help="İlgili satış sipariş satırında teslim edilmiş miktar."
    )

    # Toplam yapılan montaj miktarı alanı kaldırıldı, ancak hesaplaması kalan miktarda devam ediyor.

    # Yeni: Teslim Edilen Miktar Oranı (Char alan olarak)
    teslim_edilen_oran_str = fields.Char(
        string='Teslim Edilen Oran',
        compute='_compute_oran_str',
        store=False,  # Sadece gösterim için, veritabanında saklanmaz
        help="Teslim Edilen Miktar / Talep Edilen Montaj Miktarı."
    )

    # Yeni: Montaj Yapılan Miktar Oranı (Char alan olarak)
    yapilan_montaj_oran_str = fields.Char(
        string='Montaj Yapılan Oran',
        compute='_compute_oran_str',
        store=False,  # Sadece gösterim için, veritabanında saklanmaz
        help="Montaj Yapılan Miktar / Talep Edilen Montaj Miktarı."
    )

    @api.depends('sale_order_line_id.qty_delivered')
    def _compute_teslim_edilen_miktar(self):
        for task in self:
            task.teslim_edilen_miktar = task.sale_order_line_id.qty_delivered if task.sale_order_line_id else 0.0

    @api.depends('talep_edilen_montaj_miktari', 'montaj_emri_ids.unit_amount')
    def _compute_kalan_montaj_miktari(self):
        for task in self:
            toplam_yapilan_montaj = sum(emri.unit_amount for emri in task.montaj_emri_ids)
            task.kalan_montaj_miktari = task.talep_edilen_montaj_miktari - toplam_yapilan_montaj

    # Oran string'lerini hesaplayan metot
    @api.depends('talep_edilen_montaj_miktari', 'teslim_edilen_miktar',
                 'montaj_emri_ids.unit_amount')  # yapilan_montaj_oran_str için montaj_emri_ids.unit_amount eklendi
    def _compute_oran_str(self):
        for task in self:
            talep = task.talep_edilen_montaj_miktari
            teslim = task.teslim_edilen_miktar
            yapilan = sum(
                emri.unit_amount for emri in task.montaj_emri_ids)  # Montaj Yapılan Miktar burada anlık hesaplanıyor

            # Teslim Edilen Oran
            task.teslim_edilen_oran_str = f"{teslim:.2f} / {talep:.2f}" if talep != 0 else f"{teslim:.2f} / 0.00"

            # Montaj Yapılan Oran
            task.yapilan_montaj_oran_str = f"{yapilan:.2f} / {talep:.2f}" if talep != 0 else f"{yapilan:.2f} / 0.00"

    def action_open_montaj_emri_entry(self):
        self.ensure_one()

        montaj_emri_form_view_id = self.env.ref('yuz_montaj.view_montaj_emri_quick_create_form').id

        return {
            'name': 'Hızlı Montaj Emri Girişi',
            'type': 'ir.actions.act_window',
            'res_model': 'montaj.emri',
            'view_mode': 'form',
            'view_id': montaj_emri_form_view_id,
            'target': 'new',
            'context': {
                'default_project_id': self.project_id.id,
                'default_task_id': self.id,
                'default_employee_id': self.env.user.employee_id.id,
                'default_date': fields.Date.context_today(self),
            },
        }