from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, View
from .models import Mesin
        
kategori_mesin =  [{'value': 'blow', 'label': 'Blow Molding Machine'}, {'value': 'injection', 'label': 'Injection Molding Machine'}]

class ListMesin(ListView):
    template_name = 'crud_mesin/list_machines.html'
    model = Mesin
    context_object_name = 'list_mesin'

class RegisterMesin(CreateView):
    template_name = 'crud_mesin/register-machine.html'
    model = Mesin
    fields = ['category_machine', 'no_machine', 'description']
    success_url = reverse_lazy('list_mesin')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kategori_mesin'] = kategori_mesin
        return context
    
    
class DashboardInjection(TemplateView):
    template_name = 'base/dashboard-injection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_mesin'] = Mesin.objects.filter(category_machine="injection")
        return context
    
class DashboardBlow(TemplateView):
    template_name = 'base/dashboard-blow.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_mesin'] = Mesin.objects.filter(category_machine="blow")
        return context
    
class DashboardMesin(UpdateView):
    template_name = 'index-mesin.html'
    fields = ['category_machine', 'no_machine', 'description']
    template_name = 'CrudMesin/update-mesin.html'
    success_url = '/'


def AsyncMesin(request):
    list_mesin = Mesin.objects.all()
    return render(request, 'Partial/mesin-partial.html', {'list_mesin': list_mesin})

def AsyncMesinCard(request):
    list_mesin = Mesin.objects.all()
    return render(request, 'Partial/mesin-partial-card.html', {'list_mesin': list_mesin})

class UpdateMesin(UpdateView):
    model = Mesin
    fields = ['category_machine', 'no_machine', 'description']
    template_name = 'CrudMesin/update-mesin.html'
    success_url = '/'

class UpdateStatusMesin(View):

    def post(self, request, pk):
        statusmesin = get_object_or_404(Mesin, pk=pk)

        if statusmesin.is_active:
            statusmesin.is_active = False
        else:
            statusmesin.is_active = True
        statusmesin.save() # Update the boolean field to False

        # return redirect(reverse('list_mesin'))
        return redirect(self.request.META.get('HTTP_REFERER'))

class DeleteMesin(DeleteView):
    model = Mesin
    success_url = reverse_lazy('list_mesin')


