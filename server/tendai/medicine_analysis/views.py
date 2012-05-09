from utils import JSONView


class MedicineStockView(JSONView):
    def get_json_data(self, *args, **kwargs):
        format = self.request.GET.get('format','json')
        return {'test': 'works', 'format': format}

