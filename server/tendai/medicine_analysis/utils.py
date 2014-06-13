import json
from django import http
from django.views.generic import View

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload."
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object."
        return json.dumps(context)


class JSONView(JSONResponseMixin, View):
    def get_context_data(self, *args, **kwargs):
        "Return a Python object that will be serialized into a JSON response."
        return {
            'params': kwargs
        }

    def get(self, request, *args, **kwargs):
        "Serialize the JSON data into an HTTP response."
        context = self.get_json_data(*args, **kwargs)
        return self.render_to_response(context)
