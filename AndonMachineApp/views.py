from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, View
from .models import Mesin, Downtime, DowntimeByRole


kategori_mesin =  [{'value': 'blow', 'label': 'Blow Molding Machine'}, {'value': 'injection', 'label': 'Injection Molding Machine'}]
first_role = [{'value': 'leader', 'label': 'Production Leader'}]
roles =  [{'value': 'setter', 'label': 'Setter'}, {'value': 'maintenance', 'label': 'Maintenance Department'}, {'value': 'mold', 'label': 'Mold Division'}]


class Dashboard(TemplateView):
    template_name = 'base/index.html'


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

def AsyncMesin(request):
    list_mesin = Mesin.objects.all()
    return render(request, 'partial/mesin-partial.html', {'list_mesin': list_mesin})


def AsyncMesinCard(request):
    list_mesin = Mesin.objects.all()
    return render(request, 'partial/mesin-partial-card.html', {'list_mesin': list_mesin})


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


class DisplayAndon(TemplateView):
    template_name = 'crud_downtime/andon-view.html'

    def dispatch(self, request, *args, **kwargs):
        kategori_mesin = request.GET.get('category')
        nmr_mesin = request.GET.get('machine')

        if kategori_mesin and nmr_mesin:
            if Mesin.objects.filter(no_machine=nmr_mesin, category_machine=kategori_mesin).exists():
                pass
            else:
                return redirect(reverse('view_dashboard'))
                
        else:
            return redirect(reverse('view_dashboard'))
            
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kategori_mesin = self.request.GET.get('category')
        nmr_mesin = self.request.GET.get('machine')

        try:
            mesin = Mesin.objects.get(no_machine=nmr_mesin, category_machine=kategori_mesin)
            # Update the status field
            if mesin.status == 'standby' or mesin.status == 'waiting':
                all_roles = first_role + roles
                context['roles'] = all_roles

                # Create a list of role values that are in all_roles
                context['disabled_roles'] = {role['value'] for role in roles}
            else:
                all_roles = first_role + roles
                context['roles'] = all_roles

                 # Create a list of role values that are in all_roles
                context['disabled_roles'] = {role['value'] for role in first_role}

            if mesin.status == "standby":
                context['title'] = 'Stop-Call-Wait'
                context['status'] = 'Was there a problem?'
                context['icon'] = 'fa-hand'
                context['bgcolor'] = 'bg-pink'

            else:
                context['title'] = 'Take Response'
                context['status'] = 'Take on this downtime repair work'
                context['icon'] = 'fa-wrench'
                context['bgcolor'] = 'bg-secondary'

        except Mesin.DoesNotExist:
            # Handle the case where the Mesin does not exist
            print("The specified Mesin does not exist.")

        context['nmr_mesin'] = nmr_mesin
        context['kategori_mesin'] = kategori_mesin

        return context
    
    
class AddDowntime(View):

    def post(self, request):
        kategori_mesin = request.POST.get('kategori_mesin')
        nmr_mesin = request.POST.get('nmr_mesin')
        role = request.GET.get('role')

        try:
            mesin = Mesin.objects.get(no_machine=nmr_mesin, category_machine=kategori_mesin)
            # Update the status field
            mesin.status = 'waiting'
            mesin.save()  # Save the changes to the database
            # If it exists, create a Downtime record
            downtime_instance = Downtime.objects.create(
                machine=mesin,
                start_time=timezone.now()
            )

            DowntimeByRole.objects.create(
                downtime=downtime_instance,
                role=role,
                status="waiting"
            )

        except Mesin.DoesNotExist:
            # Handle the case where the Mesin does not exist
            print("The specified Mesin does not exist.")

        return redirect(self.request.META.get('HTTP_REFERER'))


def leader_trigger(request):
    is_waiting_instances = DowntimeByRole.objects.filter(role="leader", status="waiting").exists()

    if is_waiting_instances:
        return HttpResponse("off")

    else:
        return HttpResponse("off")
