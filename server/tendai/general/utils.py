import re
import dateutil.parser

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    
    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)

def value_or_none(xml, element_name):
    """
    Used to the text value of an xml leaf node. Returns none if it cannot find one
    """
    try:
        return xml.getElementsByTagName(element_name)[0].childNodes[0].nodeValue
    except IndexError:
        return None

def date_or_none(xml, element_name):
    value = value_or_none(xml, element_name)
    if value:
        return dateutil.parser.parse(value)
    return None
