from .models import Mesin

def navbar_context(request):
      dict_category_machine =  [{'value': 'blow', 'label': 'Blow Molding Machine'}, {'value': 'injection', 'label': 'Injection Molding Machine'}]

      return {
        'cp_kategori_mesin': dict_category_machine,
      }