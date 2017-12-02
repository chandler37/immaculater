# -*- coding: utf-8 -*-

import functools
import sys

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateResponseMixin

if sys.version_info[0] > 2:
    basestring = str


class PJAXResponseRedirect(HttpResponse):

    def __init__(self, redirect_to, *args, **kwargs):
        super(PJAXResponseRedirect, self).__init__(*args, **kwargs)
        self['X-PJAX-URL'] = self['Location'] = redirect_to


def pjax(pjax_template=None, additional_templates=None, follow_redirects=False):
    def pjax_decorator(view):
        @functools.wraps(view)
        def _view(request, *args, **kwargs):
            resp = view(request, *args, **kwargs)
            # this is lame. what else though?
            # if not hasattr(resp, "is_rendered"):
            #     warnings.warn("@pjax used with non-template-response view")
            #     return resp
            if request.META.get('HTTP_X_PJAX', False):
                if follow_redirects and isinstance(resp, HttpResponseRedirect):
                    return PJAXResponseRedirect(redirect_to=resp['Location'])

                container = request.META.get('HTTP_X_PJAX_CONTAINER', None)
                template = additional_templates.get(container, pjax_template) if additional_templates else pjax_template

                if template:
                    resp.template_name = template
                else:
                    try:
                        resp.template_name = _pjaxify_template_var(resp.template_name)
                    except AttributeError:
                        pass
            return resp
        return _view
    return pjax_decorator


def pjaxtend(parent='base.html', pjax_parent='pjax.html', context_var='parent'):
    def pjaxtend_decorator(view):
        @functools.wraps(view)
        def _view(request, *args, **kwargs):
            resp = view(request, *args, **kwargs)
            # this is lame. what else though?
            # if not hasattr(resp, "is_rendered"):
            #     warnings.warn("@pjax used with non-template-response view")
            #     return resp
            if request.META.get('HTTP_X_PJAX', False):
                resp.context_data[context_var] = pjax_parent
            elif parent:
                resp.context_data[context_var] = parent
            return resp
        return _view
    return pjaxtend_decorator


class PJAXResponseMixin(TemplateResponseMixin):

    pjax_template_name = None

    def get_template_names(self):
        names = super(PJAXResponseMixin, self).get_template_names()
        if self.request.META.get('HTTP_X_PJAX', False):
            if self.pjax_template_name:
                names = [self.pjax_template_name]
            else:
                names = _pjaxify_template_var(names)
        return names


def _pjaxify_template_var(template_var):
    if isinstance(template_var, (list, tuple)):
        template_var = type(template_var)(_pjaxify_template_name(name) for name in template_var)
    elif isinstance(template_var, basestring):
        template_var = _pjaxify_template_name(template_var)
    return template_var


def _pjaxify_template_name(name):
    if "." in name:
        name = "%s-pjax.%s" % tuple(name.rsplit('.', 1))
    else:
        name += "-pjax"
    return name
