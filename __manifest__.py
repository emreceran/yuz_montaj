{
    'name': 'YUZ Montaj Yönetimi',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Montaj emirlerinin yönetimi ve proje görevleriyle entegrasyon.',
    'sequence': 10,
    'author': 'Your Name/Company Name', # Kendi adınızı/şirket adınızı yazın
    'depends': [
        'base',
        'project',
        'hr',
        'hr_timesheet',
        'sale',  # <-- BU SATIR EKLENDİ
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/montaj_emri_views.xml',
        'views/montaj_emri_menus.xml',
        'views/project_task_inherit_views.xml', # Proje görevi entegrasyonu
        'views/sale_order_inherit_views.xml', # Proje görevi entegrasyonu

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}