from lxml import etree
from lxml.cssselect import CSSSelector


_css_cache = {}
_xpath_cache = {}


def cssselect(expr, root):
    if not expr in _css_cache:
        compiled_xpath = CSSSelector(expr)
        _css_cache[expr] = compiled_xpath
    else:
        compiled_xpath = _css_cache[expr]
    return compiled_xpath(root)


def xpath(expr, root, **kwargs):
    if not expr in _xpath_cache:
        compiled_xpath = etree.XPath(expr, **kwargs)
        _xpath_cache[expr] = compiled_xpath
    else:
        compiled_xpath = _xpath_cache[expr]
    return compiled_xpath(root)
