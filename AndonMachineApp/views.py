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


class DashboardBlow(TemplateView):
    template_name = 'base/dashboard-blow.html'

class ListMesin(ListView):
    template_name = 'crud_mesin/list_machines.html'
    model = Mesin
    context_object_name = 'list_mesin'
    ordering = ['category_machine', 'no_machine']


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


class UpdateMesin(UpdateView):
    model = Mesin
    fields = ['category_machine', 'no_machine', 'description']
    template_name = 'crud_mesin/update-machine.html'
    success_url = reverse_lazy('list_mesin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kategori_mesin'] = kategori_mesin
        return context


def AsyncMesin(request):
    list_mesin = Mesin.objects.all()
    return render(request, 'partial/mesin-partial.html', {'list_mesin': list_mesin})

def AsyncMesinBlowCard(request):
    list_mesin = Mesin.objects.filter(category_machine='blow').order_by('no_machine')

    # Prepare list mesin dengan beberapa komponen "color"
    mesin_card_color = []

    # Determine color for each machine's status
    for data in list_mesin:
        if data.is_active and data.status == "standby":
            bg_color = 'bg-teal'

        elif ((data.is_active) and (data.status == "maintain" or data.status == "pending")):
            bg_color = 'bg-warning'
        
        else:
            bg_color = 'bg-gray-200'
        
        # Append machine and its background color to the list
        mesin_card_color.append({
            'data': data,
            'bg_color': bg_color
        })

    return render(request, 'partial/mesin-partial-card-blw.html', {'list_mesin': mesin_card_color})

def AsyncMesinInjectionCard(request):
    list_mesin = Mesin.objects.filter(category_machine='injection').order_by('no_machine')

    # Prepare list mesin dengan beberapa komponen "color"
    mesin_card_color = []

    # Determine color for each machine's status
    for data in list_mesin:
        if data.is_active and data.status == "standby":
            bg_color = 'bg-teal'

        elif ((data.is_active) and (data.status == "maintain" or data.status == "pending")):
            bg_color = 'bg-warning'
        else:
            bg_color = 'bg-gray-200'
        
        # Append machine and its background color to the list
        mesin_card_color.append({
            'data': data,
            'bg_color': bg_color
        })

    return render(request, 'partial/mesin-partial-card-inj.html', {'list_mesin': mesin_card_color})


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
            if Mesin.objects.filter(no_machine=nmr_mesin, category_machine=kategori_mesin, is_active=True).exists():
                pass
            else:
                return redirect(self.request.META.get('HTTP_REFERER'))
                
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
            context['roles'] = all_roles
            if ((mesin.status == 'standby')):
                context['disabled_roles'] = {role['value'] for role in roles}

            # status "repair" atau "off" enable tombol leader, disable lainnya
            elif ((mesin.status == 'maintain') or (mesin.status == 'off')):
                context['disabled_roles'] = {role['value'] for role in first_roles}

            # status "repair" atau "off" enable tombol leader, disable lainnya
            elif (mesin.status == 'pending'):
                context['disabled_roles'] = {role['value'] for role in all_roles}

        except Mesin.DoesNotExist:
            # Handle the case where the Mesin does not exist
            print("The specified Mesin does not exist.")

        try:
            # if mesin.status == "pending" or mesin.status == "repair":
            downtime_mesin = DowntimeMesin.objects.filter(machine__no_machine=nmr_mesin, machine__category_machine=kategori_mesin).order_by('-start_time').first() 
            downtime_role = DowntimeRole.objects.filter(downtime=downtime_mesin)
            context['btncolor3'] = 'bg-red'

            # Prepare list downtime_role dengan beberapa komponen context
            multicontext_roles = []

            # Determine masing-masing status downtime_role
            for data in downtime_role:
                if data.status == "waiting":
                    btn_color = 'bg-indigo'
                    icon = 'fa-hourglass fa-spin'
                    icon2 = 'fa-wrench'
                    btn_color2 = 'bg-orange'
                    disable_btn2 = ''
                    btn_color3 = 'bg-blue'
                    disable_btn = ''
                    message = 'ambil tugas ini'

                elif data.status == "done":
                    btn_color = 'bg-teal'
                    icon = 'fa-check-circle'
                    icon2 = 'fa-thumbs-up'
                    btn_color2 = 'bg-pink'
                    disable_btn2 = 'disabled'
                    btn_color3 = 'bg-pink'
                    disable_btn = 'disabled'
                    message = ''

                else:
                    btn_color = 'bg-orange'
                    icon = 'fa-cog fa-spin'
                    icon2 = 'fa-thumbs-up'
                    btn_color2 = 'bg-teal'
                    disable_btn2 = 'disabled'
                    btn_color3 = 'bg-pink'
                    disable_btn = ''
                    message = 'selesai perbaikan'

                
                # Append role and color to the list
                multicontext_roles.append({
                    'data': data,
                    'btn_color': btn_color,
                    'icon': icon,
                    'icon2': icon2,
                    'btn_color2': btn_color2,
                    'disable_btn2': disable_btn2,
                    'btn_color3': btn_color3,
                    'disable_btn': disable_btn,
                    'message': message
                })

            # tampilkan list role jika status mesin "maintain/pending"
            if ((mesin.status == 'maintain') or (mesin.status == 'pending')):
                context['multicontext_roles'] = multicontext_roles
                

            # tampilkan tombol finish jika semua status role "done" dan status mesin "maintain"
            if all(role.status == "done" for role in downtime_role) and downtime_role.exists() and mesin.status == 'maintain':
                csrf_token = get_token(self.request)
                html = f'<form method="post" action="{reverse("status_downtime_mesin")}">'
                html += f'<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">'
                html += f'<input type="hidden" name="nmr_mesin" value="{downtime_mesin.machine.no_machine}">'
                html += f'<input type="hidden" name="kategori_mesin" value="{downtime_mesin.machine.category_machine}">'
                html += f'<button type="submit" class="btn btn-teal text-lg w-100 mb-3 p-5">FINISH</button>'
                html += '</form>'
                context['btnfinish'] = html

        except DowntimeRole.DoesNotExist:
            # Handle the case where the DowntimeRole does not exist
            print("The specified DowntimeRole does not exist.")

        context['nmr_mesin'] = nmr_mesin
        context['kategori_mesin'] = kategori_mesin

        if kategori_mesin == "blow":
            context['url'] = reverse('dashboard_mesin_blow')
        else:
            context['url'] = reverse('dashboard_mesin_injection')

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

                # cek jika role sudah ada di id downtime tersebut
                if DowntimeRole.objects.filter(downtime=downtime_instance, role=role).exists():
                    return redirect(self.request.META.get('HTTP_REFERER'))
                
                else:
                    DowntimeRole.objects.create(
                        downtime=downtime_instance,
                        role=role,
                        status="waiting"
                    )

            # create downtime role jika bukan "leader"
            elif mesin.status == 'maintain' and any(r['value'] == role for r in roles):

                # cek jika role sudah ada di id downtime tersebut
                if DowntimeRole.objects.filter(downtime=downtime_instance, role=role).exists():
                    return redirect(self.request.META.get('HTTP_REFERER'))
                
                else:
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
    
    
class DeleteDowntimeRole(View):

    def post(self, request, pk):
        role_instance_update = DowntimeRole.objects.get(id=pk)
        kategori_mesin = request.POST.get('kategori_mesin')
        nmr_mesin = request.POST.get('nmr_mesin')
        mesin = Mesin.objects.get(no_machine=nmr_mesin, category_machine=kategori_mesin)
        downtime_instance = DowntimeMesin.objects.filter(machine__no_machine=mesin.no_machine, machine__category_machine=mesin.category_machine).order_by('-start_time').first()

        # kembali ke "standby" jika batal panggil leader 
        if mesin and any(r['value'] == role_instance_update.role for r in first_roles):
            mesin.status = 'standby'
            mesin.save()

            # hapus "downtime" & "role"
            downtime_instance.delete()
            role_instance_update.delete()

        # jika others
        elif mesin and any(r['value'] == role_instance_update.role for r in roles):
            role_instance_update.delete()

        return redirect(self.request.META.get('HTTP_REFERER'))
    

def ControlTrigger(request):

    if DowntimeRole.objects.filter(role="leader", status="waiting").exists():
        data = {
            "status": "success",
            "message": "waiting",
            "role": "leader"
        }

    elif DowntimeRole.objects.filter(role="setter", status="waiting").exists():
        data = {
            "status": "success",
            "message": "waiting",
            "role": "setter"
        }

    elif DowntimeRole.objects.filter(role="maintenance", status="waiting").exists():
        data = {
            "status": "success",
            "message": "waiting",
            "role": "maintenance"
        }

    elif DowntimeRole.objects.filter(role="mold", status="waiting").exists():
        data = {
            "status": "success",
            "message": "waiting",
            "role": "mold"
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
