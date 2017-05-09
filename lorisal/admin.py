from flask import Flask, request, Response, send_from_directory
import flask_admin as admin
from flask_admin.contrib.peewee import ModelView
from PIL import Image
import os
#  from flask_admin.model import typefmt

import models as models
#  Book, Page, ExtractedImage


#  def book_full_title(view, value):
#      return value.full_title
#
#  MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
#  MY_DEFAULT_FORMATTERS.update({
#              type(Book): book_full_title,
#          })

app = Flask(__name__)
#  app = Flask(__name__, static_url_path="/data")


class BookView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    column_exclude_list = ['mods_metadata', 'title', ]


class PageView(ModelView):
    can_create = False
    #  can_edit = False
    can_delete = False
    can_view_details = True
    #  column_filters = ('full_size_downloaded', 'images_detected', )
    #  column_list = ('book','uuid', 'ocr_text', 'images_detected')
    column_exclude_list = ('label', 'page_number', )
    column_sortable_list = ('uuid', ('book', models.Book.full_title), 'images_detected')
    # Full text search
    column_searchable_list = ('uuid', models.Book.full_title, 'ocr_text')
    # Column filters
    column_filters = ('uuid',
                      'ocr_text',
                      models.Book.full_title,
                      'images_detected',
                      )
    #  form_ajax_refs = {
    #              'book': {
    #                      'fields': (Book.full_title, "full_title")
    #                      }
    #  }
    #  column_detail_list = ('uuid', Book.full_title)
    details_template = 'page_details.html'
    details_modal = True
    details_modal_template = 'page_details_modal.html'
    #  column_type_formatters = MY_DEFAULT_FORMATTERS

    #  form_ajax_refs = {
    #          'book': {
    #          'fields': (models.Book.full_title, 'uuid')
    #      } }


class ExtractedImageView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    details_template = 'extract_details.html'
    #  details_modal = True
    #  details_modal_template = 'extract_details_modal.html'
    column_hide_backrefs = False

    column_filters = ('tags',
                      'label',
                      'page_coordinate_TL_x',
                      'page_coordinate_TL_y',
                      'page_coordinate_BR_x',
                      'page_coordinate_BR_y',
                      models.Page.ocr_text,
                      models.Page.uuid,
                      )

    column_searchable_list = ('tags', 'label', )



@app.route('/')
def index():
        return '<a href="/admin/">Click me to get to Admin!</a>'

@app.route('/<path:filename>')
def image(filename):

    print(os.getcwd())
    print(filename)

    try:
        w = int(request.args['w'])
        h = int(request.args['h'])
    except (KeyError, ValueError):
        return send_from_directory('.', filename)

    #  try:
    #      im = Image.open(filename)
    #      im.thumbnail((w, h), Image.ANTIALIAS)
    #      print(w)
    #      print(h)
    #      io = StringIO.StringIO()
    #      im.save(io, format='JPEG')
    #      stream = io.BytesIO(im)
    #      return Response(io.getvalue(), mimetype='image/jpeg')
    #
    #  except IOError:
    #      abort(404)

    return send_from_directory('.', filename)


if __name__ == '__main__':
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    admin = admin.Admin(app, name='Lorisal', template_mode='bootstrap3')
    #  admin = Admin(app, name='Lorisal', template_mode='bootstrap3')
    # Add administrative views here

    admin.add_view(BookView(models.Book))
    admin.add_view(PageView(models.Page))
    admin.add_view(ExtractedImageView(models.ExtractedImage))

    app.run("0.0.0.0", port=5000, debug=True)
