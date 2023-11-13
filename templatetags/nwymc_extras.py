from django import template

register = template.Library()

@register.filter
def custom_redir_lang(url_fullpath):
    ls_urls = url_fullpath.split('/')
    del ls_urls[1]
    return '/'.join(ls_urls)

@register.filter
def missing_trans_PL(contextData):
    missing = 0
    for x in contextData:
        if len(x.pl_title) < 1:
            missing += 1
    return missing

@register.filter
def missing_trans_EN(contextData):
    missing = 0
    for x in contextData:
        if len(x.en_title) < 1:
            missing += 1
    return missing
