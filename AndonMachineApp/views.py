from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, View
from .models import Mesin, DowntimeMesin, DowntimeRole
from django.middleware.csrf import get_token


kategori_mesin =  [{'value': 'blow', 'label': 'Blow Molding Machine'}, {'value': 'injection', 'label': 'Injection Molding Machine'}]
first_roles = [{'value': 'leader', 'label': 'Production Leader'}]
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

    def form_valid(self, form):
        # Retrieve the form data
        category_machine = form.cleaned_data.get('category_machine')
        no_machine = form.cleaned_data.get('no_machine')

        if Mesin.objects.filter(category_machine=category_machine, no_machine=no_machine).exists():
            return redirect(self.request.META.get('HTTP_REFERER'))
        
        # Perform any other operations you need before saving
        response = super().form_valid(form)

        # Additional logic after saving if needed
        return response

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
            statusmesin.status = "off"
        else:
            statusmesin.is_active = True
            statusmesin.status = "standby"
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
        mesin = Mesin.objects.get(no_machine=nmr_mesin, category_machine=kategori_mesin)

        try:

            # status "standby" atau "pending" enable tombol leader, disable lainnya
            all_roles = first_roles + roles
            if ((mesin.status == 'standby')):
                context['roles'] = all_roles
                context['disabled_roles'] = {role['value'] for role in roles}

            # status "repair" atau "off" enable tombol leader, disable lainnya
            elif ((mesin.status == 'maintain') or (mesin.status == 'off')):
                context['roles'] = all_roles
                context['disabled_roles'] = {role['value'] for role in first_roles}

            # status "repair" atau "off" enable tombol leader, disable lainnya
            elif (mesin.status == 'pending'):
                context['roles'] = all_roles
                context['disabled_roles'] = {role['value'] for role in all_roles}

            '''
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
            '''

        except Mesin.DoesNotExist:
            # Handle the case where the Mesin does not exist
            print("The specified Mesin does not exist.")

        try:
            # if mesin.status == "pending" or mesin.status == "repair":
            downtime_mesin = DowntimeMesin.objects.filter(machine__no_machine=nmr_mesin, machine__category_machine=kategori_mesin).order_by('-start_time').first() 
            downtime_role = DowntimeRole.objects.filter(downtime=downtime_mesin)
            context['btncolor3'] = 'bg-red'

            if any(role.status == "waiting" for role in downtime_role):
                context['btntext'] = 'Take'
                context['btncolor'] = 'bg-indigo'
                context['icon'] = 'fa-hourglass'
                context['icon2'] = 'fa-wrench'
                context['btncolor2'] = 'bg-orange'
                # context['btn'] = f'<button type="button" class="btn bg-warning" type="button" data-bs-toggle="modal" data-bs-target="#dtr-{downtime_role.id}"><i class="me-1 text-white-50 fa fa-wrench"></i></button>'

            # elif any(role.status == "done" for role in downtime_role):
                #context['disablebtn'] = 'disabled'

            else:
                context['btntext'] = 'Finish'
                context['btncolor'] = 'bg-orange'
                context['icon'] = 'fa-cog'
                context['icon2'] = 'fa-thumbs-up'
                context['btncolor2'] = 'bg-success'

            # tampilkan list role jika status mesin "maintain/pending"
            if ((mesin.status == 'maintain') or (mesin.status == 'pending')):     
                context['downtime_role'] = downtime_role
                

            # tampilkan tombol finish jika semua status role "done" dan status mesin "maintain"
            if all(role.status == "done" for role in downtime_role) and downtime_role.exists() and mesin.status == 'maintain':
                csrf_token = get_token(self.request)
                html = f'<form method="post" action="{reverse("status_downtime_mesin")}">'
                html += f'<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">'
                html += f'<input type="hidden" name="nmr_mesin" value="{downtime_mesin.machine.no_machine}">'
                html += f'<input type="hidden" name="kategori_mesin" value="{downtime_mesin.machine.category_machine}">'
                html += f'<button type="submit" class="btn btn-teal w-100 mb-3 p-5">FINISH</button>'
                html += '</form>'
                context['btnfinish'] = html

        except DowntimeRole.DoesNotExist:
            # Handle the case where the DowntimeRole does not exist
            print("The specified DowntimeRole does not exist.")

        context['nmr_mesin'] = nmr_mesin
        context['kategori_mesin'] = kategori_mesin

        return context
    
    
class StatusDowntimeMesin(View):

    def post(self, request):
        kategori_mesin = request.POST.get('kategori_mesin')
        nmr_mesin = request.POST.get('nmr_mesin')
        role = request.GET.get('role')
            
        try:
            mesin = Mesin.objects.get(no_machine=nmr_mesin, category_machine=kategori_mesin)
            downtime_instance = DowntimeMesin.objects.filter(machine__no_machine=mesin.no_machine, machine__category_machine=mesin.category_machine).order_by('-start_time').first()

            if mesin.status == 'standby' and any(r['value'] == role for r in first_roles):
                mesin.status = 'pending'
                mesin.save()

                downtime_instance = DowntimeMesin.objects.create(
                machine=mesin,
                start_time=timezone.now()
                )

                DowntimeRole.objects.create(
                    downtime=downtime_instance,
                    role=role,
                    status="waiting"
                )

            # create downtime role jika bukan "leader"
            elif mesin.status == 'maintain' and any(r['value'] == role for r in roles):
                DowntimeRole.objects.create(
                    downtime=downtime_instance,
                    role=role,
                    status="waiting"
                )

            # finish process
            elif mesin.status == 'maintain':
                downtime_instance.end_time = timezone.now()
                downtime_instance.save()

                mesin.status = 'standby'
                mesin.save()

        except Mesin.DoesNotExist:
            # Handle the case where the Mesin does not exist
            print("The specified Mesin does not exist.")

        return redirect(self.request.META.get('HTTP_REFERER'))


class StatusDowntimeRole(View):

    def post(self, request, pk):
        role_instance_update = DowntimeRole.objects.get(id=pk)
        kategori_mesin = request.POST.get('kategori_mesin')
        nmr_mesin = request.POST.get('nmr_mesin')
        mesin = Mesin.objects.get(no_machine=nmr_mesin, category_machine=kategori_mesin)

        # update ke "onhand" jika pemeran melakukan "take"
        if role_instance_update and role_instance_update.status == "waiting":
            role_instance_update.status = 'onhand'
            role_instance_update.save()

            mesin.status = 'maintain'
            mesin.save()

        # update ke "done" jika pemeran selesai melakukan perbaikan
        else:
            role_instance_update.status = 'done'
            role_instance_update.save()

        return redirect(self.request.META.get('HTTP_REFERER'))


def ControlTrigger(request):

    if DowntimeRole.objects.filter(role="leader", status="waiting").exists():
        data = {
            "status": "success",
            "message": "waiting",
            "role": "leader"
        }
    else:
        data = {
            "status": "success",
            "message": "waiting",
            "role": "no_role"
        }
    return JsonResponse(data)
    
    '''data = {
        "status": "success",
        "message": "hello"
    }

    return JsonResponse(data)'''
