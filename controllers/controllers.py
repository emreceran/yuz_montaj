# -*- coding: utf-8 -*-
# from odoo import http


# class YuzMontaj(http.Controller):
#     @http.route('/yuz_montaj/yuz_montaj', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/yuz_montaj/yuz_montaj/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('yuz_montaj.listing', {
#             'root': '/yuz_montaj/yuz_montaj',
#             'objects': http.request.env['yuz_montaj.yuz_montaj'].search([]),
#         })

#     @http.route('/yuz_montaj/yuz_montaj/objects/<model("yuz_montaj.yuz_montaj"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('yuz_montaj.object', {
#             'object': obj
#         })

