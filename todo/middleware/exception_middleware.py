# -*- coding: utf-8 -*-

from pyatdllib.core import errors
from django.http import JsonResponse


class ExceptionMiddleware(object):
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    return self.get_response(request)

  def process_exception(self, request, exception):
    if not isinstance(exception, errors.DataError):
      return None
    return JsonResponse({"error": f"The given to-do list is ill-formed: {exception}"},
                        status=422)
