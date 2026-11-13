# Author: Siddharth1India
import os
from flask import (
    Flask, abort, g, redirect, render_template, request,
    send_from_directory, Response
)
from werkzeug.exceptions import NotFound

app = Flask(__name__)

# Supported languages
supported_languages = ['en', 'hi', 'fr', 'zh', 'es']

# Canonical site configurations for SEO & Sitemap
SITE_DOMAIN = 'https://pixoratools.com'

TOOL_ROUTES = [
    'image-compression',
    'image-rotate',
    'image-crop',
    'image-resize',
    'image-effects',
    'convert-image-format',
    'image-watermarking',
    'blur-face',
    'remove-background'
]

INFO_ROUTES = [
    'about',
    'contact-us',
    'help',
    'faq',
    'media',
    'legal',
    'our-story',
    'features',
    'pricing',
    'languages',
    'tools',
    'privacy_policy'
]

SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp', 'ico']
CONVERTER_ROUTES = [
    f'convert/{f}-to-{t}'
    for f in SUPPORTED_FORMATS
    for t in SUPPORTED_FORMATS
    if f != t
]

ALL_PAGE_KEYS = [''] + TOOL_ROUTES + CONVERTER_ROUTES + INFO_ROUTES

_SITEMAP_CACHE = None

def get_canonical_url(lang, key):
    if key == '':
        return f'{SITE_DOMAIN}/' if lang == 'en' else f'{SITE_DOMAIN}/{lang}/'
    return f'{SITE_DOMAIN}/{key}' if lang == 'en' else f'{SITE_DOMAIN}/{lang}/{key}'

def generate_sitemap_xml():
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    ]
    for lang in supported_languages:
        for key in ALL_PAGE_KEYS:
            loc = get_canonical_url(lang, key)
            lines.append('  <url>')
            lines.append(f'    <loc>{loc}</loc>')
            for alt_lang in supported_languages:
                alt_url = get_canonical_url(alt_lang, key)
                lines.append(f'    <xhtml:link rel="alternate" hreflang="{alt_lang}" href="{alt_url}"/>')
            x_default = get_canonical_url('en', key)
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{x_default}"/>')
            lines.append('  </url>')
    lines.append('</urlset>')
    return '\n'.join(lines) + '\n'

def get_sitemap_xml():
    global _SITEMAP_CACHE
    if _SITEMAP_CACHE is None:
        _SITEMAP_CACHE = generate_sitemap_xml()
    return _SITEMAP_CACHE

@app.before_request
def before_request():
    # Exclude static files from language handling
    if request.path.startswith('/static/'):
        return  # Skip setting language for static file requests

    # Extract language from URL if present
    parts = request.path.split('/')
    if len(parts) > 1 and parts[1] in supported_languages:
        g.lang = parts[1]
    else:
        g.lang = 'en'  # Default to English

from werkzeug.exceptions import NotFound

@app.route('/<lang>/<path:subpath>')
def localized_route(lang, subpath):
    if lang not in supported_languages:
        # If language is not supported, redirect to English version
        return redirect(f'/en/{subpath}')
    
    # Set the language for this request
    g.lang = lang
    
    # Create a MapAdapter bound to the current host
    url_adapter = app.url_map.bind(request.host)
    
    try:
        # Try to match the subpath to a route
        endpoint, arguments = url_adapter.match('/' + subpath)
        return app.view_functions[endpoint](**arguments)
    except NotFound:
        # If no matching route found, try to render a template
        template_path = f'{lang}/{subpath}.html'
        if os.path.exists(os.path.join(app.template_folder, template_path)):
            return render_template(template_path)
        elif os.path.exists(os.path.join(app.template_folder, f'en/{subpath}.html')):
            return render_template(f'en/{subpath}.html')
        else:
            abort(404)

@app.route('/')
@app.route('/<lang>/')
def index(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/')
    return render_template(f'{lang}/index.html')

@app.route('/image-compression')
@app.route('/<lang>/image-compression')
def image_compression(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/image-compression')
    return render_template(f'{lang}/compress_en.html')

@app.route('/image-rotate')
@app.route('/<lang>/image-rotate')
def image_rotate(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/image-rotate')
    return render_template(f'{lang}/rotate_en.html')

@app.route('/image-crop')
@app.route('/<lang>/image-crop')
def image_crop(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/image-crop')
    return render_template(f'{lang}/crop_en.html')

@app.route('/image-resize')
@app.route('/<lang>/image-resize')
def image_resize(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/image-resize')
    return render_template(f'{lang}/resize_en.html')

@app.route('/image-effects')
@app.route('/<lang>/image-effects')
def image_effects(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/image-effects')
    return render_template(f'{lang}/image_effects_en.html')

@app.route('/convert-image-format')
@app.route('/<lang>/convert-image-format')
def convert_image_format(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/convert-image-format')
    return render_template(f'{lang}/convert_en.html')

@app.route('/convert/<from_format>-to-<to_format>')
@app.route('/<lang>/convert/<from_format>-to-<to_format>')
def convert_image_format_route(lang='en', from_format='', to_format=''):
    if lang not in supported_languages:
        return redirect(f'/en/convert/{from_format}-to-{to_format}')
    
    supported_formats = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp', 'ico']
    
    # Normalize formats
    from_format = from_format.lower()
    to_format = to_format.lower()
    
    # Validate formats
    if from_format not in supported_formats or to_format not in supported_formats:
        return render_template(f'{lang}/error.html', error="Unsupported image format"), 400
    
    # Prevent unnecessary conversions
    if from_format == to_format:
        return render_template(f'{lang}/error.html', error="Source and target formats are the same"), 400
    
    template_name = f'{from_format}-to-{to_format}.html'
    
    # Check if a specific template exists, otherwise use a generic template
    if os.path.exists(os.path.join(app.template_folder, f'{lang}/{template_name}')):
        return render_template(f'{lang}/{template_name}')
    else:
        return render_template(f'{lang}/generic_convert.html', from_format=from_format, to_format=to_format)

@app.route('/image-watermarking')
@app.route('/<lang>/image-watermarking')
def image_watermarking(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/image-watermarking')
    return render_template(f'{lang}/watermark_en.html')

@app.route('/blur-face')
@app.route('/<lang>/blur-face')
def image_blur(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/blur-face')
    return render_template(f'{lang}/blur_en.html')

@app.route('/remove-background')
@app.route('/<lang>/remove-background')
def remove_background_page(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/remove-background')
    return render_template(f'{lang}/remove-background.html')


# Consolidate static page routes
@app.route('/about')
@app.route('/<lang>/about')
def about(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/about')
    return render_template(f'{lang}/about.html')

@app.route('/contact-us')
@app.route('/<lang>/contact-us')
def contact_us(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/contact-us')
    return render_template(f'{lang}/contact_us.html')

@app.route('/help')
@app.route('/<lang>/help')
def help(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/help')
    return render_template(f'{lang}/help.html')

@app.route('/faq')
@app.route('/<lang>/faq')
def faq(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/faq')
    return render_template(f'{lang}/faq.html')

@app.route('/media')
@app.route('/<lang>/media')
def media(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/media')
    return render_template(f'{lang}/media.html')

@app.route('/legal')
@app.route('/<lang>/legal')
def legal(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/legal')
    return render_template(f'{lang}/legal.html')

@app.route('/our-story')
@app.route('/<lang>/our-story')
def our_story(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/our-story')
    return render_template(f'{lang}/our_story.html')

@app.route('/features')
@app.route('/<lang>/features')
def features(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/features')
    return render_template(f'{lang}/features.html')

@app.route('/pricing')
@app.route('/<lang>/pricing')
def pricing(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/pricing')
    return render_template(f'{lang}/pricing.html')

@app.route('/languages')
@app.route('/<lang>/languages')
def languages(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/languages')
    return render_template(f'{lang}/languages.html')

@app.route('/tools')
@app.route('/<lang>/tools')
def tools(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/tools')
    return render_template(f'{lang}/tools.html')

@app.route('/privacy_policy')
@app.route('/<lang>/privacy_policy')
def privacy_policy(lang='en'):
    if lang not in supported_languages:
        return redirect('/en/privacy_policy')
    return render_template(f'{lang}/privacy_policy.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'pixora_tools.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/sitemap.xml')
def sitemap():
    return Response(get_sitemap_xml(), mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('en/error.html', error="404 - Page Not Found"), 404

if __name__ == '__main__':
    app.run(debug=True)