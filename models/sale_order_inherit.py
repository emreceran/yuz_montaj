# yuz_montaj/models/sale_order_inherit.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re  # <-- BU SATIRI EKLEYİN
import logging  # <-- HATA AYIKLAMA İÇİN İSTEĞE BAĞLI

_logger = logging.getLogger(__name__)  # <-- HATA AYIKLAMA İÇİN İSTEĞE BAĞLI


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_project_tasks(self):
        """
        Satış siparişinden görev oluşturur. Görev adını satış satırı açıklamasındaki
        varyant bilgilerine (regex ile) göre biçimlendirir.
        """
        # Regex pattern'lerini metot dışında veya burada tanımlayabilirsiniz.
        # Genellikle performan için metot dışında tanımlamak daha iyidir,
        # ancak kolaylık için burada tanımlıyorum.
        # NOT: Regex'lerdeki "ürün adı:", "ürün açıklama:", "uzunluk:" gibi anahtarların
        # satış satırı açıklamanızdaki gerçek metinlerle birebir eşleştiğinden emin olun.
        pattern_adi = re.compile(r"ürün adı:\s*ürün adı:\s*(.*?)\s*(?:ürün açıklama:|uzunluk:|$)", re.IGNORECASE)
        pattern_aciklama = re.compile(r"ürün açıklama:\s*ürün açıklama:\s*(.*?)\s*(?:uzunluk:|$)", re.IGNORECASE)
        pattern_uzunluk = re.compile(r"uzunluk:\s*uzunluk:\s*(\d+(?:[.,]\d+)?)\b", re.IGNORECASE)

        for order in self:
            if not order.project_id:
                raise UserError(
                    _("Bu satış siparişine bağlı bir proje bulunamadı. Lütfen bir proje seçin veya projeye bağlantıyı sağlayın."))

            newly_created_tasks = self.env['project.task']

            for line in order.order_line:
                if line.product_id and line.product_id.type in ['product', 'consu'] and line.product_uom_qty > 0:

                    existing_task_for_line = self.env['project.task'].search([
                        ('sale_order_id', '=', order.id),
                        ('sale_order_line_id', '=', line.id)
                    ], limit=1)

                    if existing_task_for_line:
                        continue

                    # Görev adı oluşturma: Satış satırı açıklamasından (line.name) regex ile çekme
                    source_string_for_task_name = line.name  # Kullanacağımız kaynak string
                    extracted_adi = ""
                    extracted_aciklama = ""

                    if source_string_for_task_name:
                        # Ürün Adı
                        match_adi = pattern_adi.search(source_string_for_task_name)
                        if match_adi: extracted_adi = match_adi.group(1).strip()
                        # Ürün Açıklama
                        match_aciklama = pattern_aciklama.search(source_string_for_task_name)
                        if match_aciklama: extracted_aciklama = match_aciklama.group(1).strip()
                        # Uzunluk (görev adına eklemiyoruz ama çekme mantığı aynı)
                        # match_uzunluk = pattern_uzunluk.search(source_string_for_task_name)
                        # if match_uzunluk:
                        #     extracted_uzunluk_str = match_uzunluk.group(1)
                        #     try: uzunluk_float = float(extracted_uzunluk_str.replace(',', '.'))
                        #     except ValueError: uzunluk_float = 0; _logger.warning(f"Uzunluk ('{extracted_uzunluk_str}') çevrilemedi.")

                    # Görev adını istediğiniz formatta birleştirin: "S2 - Çiftli"
                    task_name = ""
                    if extracted_adi:
                        task_name += extracted_adi
                    if extracted_aciklama:
                        if task_name:  # Eğer ürün adı varsa araya " - " koy
                            task_name += " - "
                        task_name += extracted_aciklama

                    if not task_name:  # Eğer regex ile hiçbir şey çekilemezse, varsayılan ürün adını kullan
                        task_name = line.product_id.name

                    # Görev açıklaması oluşturma (burası daha detaylı kalabilir)
                    task_description = _(
                        f"Satış Siparişi #{order.name} için ürün ({line.product_id.name}) üretilecek/hazırlanacak.\n"
                        f"Talep Edilen Miktar: {line.product_uom_qty} {line.product_uom.name}.\n"
                        f"Satış Satırı Açıklaması: {line.name}\n"
                        f"Müşteri: {order.partner_id.name}"
                    )

                    new_task = self.env['project.task'].create({
                        'name': task_name,  # Yeni biçimlendirilmiş görev adı
                        'project_id': order.project_id.id,
                        'description': task_description,
                        'talep_edilen_montaj_miktari': line.product_uom_qty,
                        'sale_order_id': order.id,
                        'sale_order_line_id': line.id,
                    })
                    newly_created_tasks += new_task

            if not newly_created_tasks:
                raise UserError(
                    _("Bu satış siparişinde henüz görev oluşturulmamış veya yeni eklenecek bir satış siparişi satırı bulunamadı."))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Görevler Oluşturuldu!"),
                'message': _("%s adet görev başarıyla oluşturuldu.") % len(newly_created_tasks),
                'type': 'success',
                'sticky': False,
            }
        }