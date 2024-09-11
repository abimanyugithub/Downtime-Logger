from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, View
from .models import Mesin, DowntimeMesin, DowntimeRole
from django.middleware.csrf import get_token


dict_category_machine =  [{'value': 'blow', 'label': 'Blow Molding Machine'}, {'value': 'injection', 'label': 'Injection Molding Machine'}]
dict_first_roles = [{'value': 'leader', 'label': 'Production Leader'}]
dict_roles =  [{'value': 'setter', 'label': 'Setter'}, {'value': 'maintenance', 'label': 'Maintenance Department'}, {'value': 'mold', 'label': 'Mold Division'}]

'''
class Index(TemplateView):
    template_name = 'base/index.html'
'''
    
class Dashboard(TemplateView):
    template_name = 'base/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kategori_mesin = self.request.GET.get('category')

        # kembalikan dari get filter role
        role_filter = self.request.GET.get('role')

        # using dict.get() with a temporary dictionary
        temp_dict = {k['value']: k for k in dict_category_machine}
        selected_category = temp_dict.get(kategori_mesin)
        context['kategori_mesin'] = selected_category

        combined_roles = dict_first_roles + dict_roles
        # Sort the combined list by the 'value' key
        sorted_combined_roles = sorted(combined_roles, key=lambda x: x['value'])
        context['roles'] = sorted_combined_roles
        context['role_filter'] = role_filter

        return context
    
    
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
        kategori_mesin = form.cleaned_data.get('category_machine')
        no_machine = form.cleaned_data.get('no_machine')

        if Mesin.objects.filter(category_machine=kategori_mesin, no_machine=no_machine).exists():
            return redirect(self.request.META.get('HTTP_REFERER'))
        
        # Perform any other operations you need before saving
        response = super().form_valid(form)

        # Additional logic after saving if needed
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kategori_mesin'] = dict_category_machine
        return context


class UpdateMesin(UpdateView):
    model = Mesin
    fields = ['category_machine', 'no_machine', 'description']
    template_name = 'crud_mesin/update-machine.html'
    success_url = reverse_lazy('list_mesin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kategori_mesin'] = dict_category_machine
        return context
    
'''
def AsyncMesin(request):
    list_mesin = Mesin.objects.all()
    return render(request, 'partial/mesin-partial.html', {'list_mesin': list_mesin})
'''

def AsyncMesinCard(request):
    kategori_mesin = request.GET.get('category')
    role_filter = request.GET.get('role')

    # Fetch the list of machines based on category
    if kategori_mesin == 'all':
        list_mesin = Mesin.objects.all().order_by('category_machine', 'no_machine')
    elif kategori_mesin:
        list_mesin = Mesin.objects.filter(category_machine=kategori_mesin).order_by('no_machine')
    else:
        list_mesin = Mesin.objects.none()  # No machines if no category is provided

    # Prepare list with colors based on roles or default
    mesin_card_color = []
    
    if role_filter:
        downtime_roles = DowntimeRole.objects.filter(role=role_filter)

        for data in list_mesin:
            
            
            

            # Default background color
            if data.is_active and (data.status == "maintain" or data.status == "pending"):
                bg_color = 'bg-indigo'
            elif data.is_active:
                bg_color = 'bg-teal'
            else:
                bg_color = 'bg-gray-200'

            start_time = ''  # Initialize start_time
            
            # Check for downtime roles
            for dtr in downtime_roles:
                if data.id == dtr.downtime.machine.id:
                    if dtr.status == 'waiting':
                        bg_color = 'blinking-card'
                        start_time = dtr.downtime.start_time
                    elif dtr.status == 'onhand':
                        bg_color = 'bg-yellow'
                        start_time = dtr.downtime.start_time
            
            badge_roles = []  # Initialize badge_roles list
            # Check for downtime roles to get badge_roles
            downtime_roles = DowntimeRole.objects.filter(downtime__machine=data, status="onhand")
            for dtr in downtime_roles:
                badge_roles.append(dtr.role) # Collect all roles with 'onhand' status
            

            # Append machine and its background color to the list
            mesin_card_color.append({
                'data': data,
                'bg_color': bg_color,
                'start_time': start_time,
                'badge_roles': badge_roles,
            })

    else:
        for data in list_mesin:
            downtime_mesin = DowntimeMesin.objects.filter(machine=data)
            start_time = ''  # Initialize start_time
            badge_roles = []  # Initialize badge_roles list

            if data.is_active and data.status == "ready":
                bg_color = 'bg-teal'
            elif data.is_active and (data.status == "maintain" or data.status == "pending"):
                bg_color = 'bg-warning'
                # Check for downtime roles
                for dtm in downtime_mesin:
                    if data.id == dtm.machine.id:
                        start_time = dtm.start_time
            else:
                bg_color = 'bg-gray-200'

            # Check for downtime roles to get badge_roles
            downtime_roles = DowntimeRole.objects.filter(downtime__machine=data, status="onhand")
            for dtr in downtime_roles:
                badge_roles.append(dtr.role) # Collect all roles with 'onhand' status

            # Append machine and its background color to the list
            mesin_card_color.append({
                'data': data,
                'bg_color': bg_color,
                'start_time': start_time,
                'badge_roles':badge_roles
            })

    return render(request, 'partial/mesin-partial-card.html', {'list_mesin': mesin_card_color})


class UpdateStatusMesin(View):

    def post(self, request, pk):
        status_mesin = get_object_or_404(Mesin, pk=pk)

        if status_mesin.is_active:
            if not status_mesin.status == 'ready':
                return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                status_mesin.is_active = False
                status_mesin.status = "off"
        else:
            status_mesin.is_active = True
            status_mesin.status = "ready"
        status_mesin.save() # Update the boolean field to False

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
            return redirect(reverse('view_index'))
            
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kategori_mesin = self.request.GET.get('category')
        nmr_mesin = self.request.GET.get('machine')
        mesin = Mesin.objects.get(no_machine=nmr_mesin, category_machine=kategori_mesin)

        try:

            # status "ready" atau "pending" enable tombol leader, disable lainnya
            combined_roles = dict_first_roles + dict_roles
            context['roles'] = combined_roles
            if ((mesin.status == 'ready')):
                context['disabled_roles'] = {role['value'] for role in dict_roles}
                context['status'] = mesin.status
                context['bg_status'] = 'bg-teal'

            # status "repair" atau "off" enable tombol leader, disable lainnya
            elif ((mesin.status == 'maintain') or (mesin.status == 'off')):
                context['disabled_roles'] = {role['value'] for role in dict_first_roles}
                context['status'] = mesin.status

            # status "pending" disable all
            elif (mesin.status == 'pending'):
                context['disabled_roles'] = {role['value'] for role in combined_roles}
                context['status'] = mesin.status

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
                    message = f'You are going to do this now.'
                    title = 'Commit'


                elif data.status == "done":
                    btn_color = 'bg-teal'
                    icon = 'fa-check-circle'
                    icon2 = 'fa-thumbs-up'
                    btn_color2 = 'bg-pink'
                    disable_btn2 = 'disabled'
                    btn_color3 = 'bg-pink'
                    disable_btn = 'disabled'
                    message = ''
                    title = ''

                else:
                    btn_color = 'bg-orange'
                    icon = 'fa-cog fa-spin'
                    icon2 = 'fa-thumbs-up'
                    btn_color2 = 'bg-teal'
                    disable_btn2 = 'disabled'
                    btn_color3 = 'bg-pink'
                    disable_btn = ''
                    message = f'Has the repair been completed?'
                    title = 'Completion'


                
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
                    'message': message,
                    'title': title
                })

            # tampilkan list role jika status mesin "maintain/pending"
            if ((mesin.status == 'maintain') or (mesin.status == 'pending')):
                context['multicontext_roles'] = multicontext_roles

                '''
                downtime = timezone.now() - downtime_mesin.start_time
                downtime_seconds = int(downtime.total_seconds())
                hours, remainder = divmod(downtime_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                formatted_downtime = f"{hours:02}:{minutes:02}:{seconds:02}"

                context['downtime_rundown'] = formatted_downtime
                '''

                context['start_time'] = downtime_mesin.start_time
                context['bg_status'] = 'bg-warning'
                

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

        context['nmr_mesin'] = mesin.no_machine
        context['kategori_mesin'] = mesin.category_machine

        return context
    
    
class StatusDowntimeMesin(View):

    def post(self, request):
        kategori_mesin = request.POST.get('kategori_mesin')
        nmr_mesin = request.POST.get('nmr_mesin')
        role = request.GET.get('role')
            
        try:
            mesin = Mesin.objects.get(no_machine=nmr_mesin, category_machine=kategori_mesin)
            downtime_instance = DowntimeMesin.objects.filter(machine__no_machine=mesin.no_machine, machine__category_machine=mesin.category_machine).order_by('-start_time').first()

            if mesin.status == 'ready' and any(r['value'] == role for r in dict_first_roles):
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
            elif mesin.status == 'maintain' and any(r['value'] == role for r in dict_roles):

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

                mesin.status = 'ready'
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

        # kembali ke "ready" jika batal panggil leader 
        if mesin and any(r['value'] == role_instance_update.role for r in dict_first_roles):
            mesin.status = 'ready'
            mesin.save()

            # hapus "downtime" & "role"
            downtime_instance.delete()
            role_instance_update.delete()

        # jika others
        elif mesin and any(r['value'] == role_instance_update.role for r in dict_roles):
            role_instance_update.delete()

        return redirect(self.request.META.get('HTTP_REFERER'))
    
class ListDowntimeMesin(ListView):
    template_name = 'report/list_downtime_mesin.html'
    model = DowntimeMesin
    context_object_name = 'list_downtime_mesin'
    ordering = ['-start_time']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ddr = DowntimeRole.objects.all()

        downtime_roles = []
        for data in ddr:
            if data.role == "mold":
                badges = 'bg-blue-soft text-blue'
            elif data.role == "maintenance":
                badges = 'bg-purple-soft text-purple'
            elif data.role == "leader":
                badges = 'bg-green-soft text-green'
            elif data.role == "setter":
                badges = 'bg-yellow-soft text-yellow'

            # Append role and color to the list
            downtime_roles.append({
                'data': data,
                'badges': badges
            })

        context['downtime_roles'] = downtime_roles
        return context
    

def ControlTrigger(request):

    # Combine the two lists
    combined_roles = dict_first_roles + dict_roles

    # Create a set of all possible role values (for validation if needed)
    role_values = {role['value'] for role in combined_roles}

    # Fetch all roles with status "waiting" from the database
    waiting_roles_values = DowntimeRole.objects.filter(status="waiting").values_list('role', flat=True).distinct()

    # Filter waiting roles to only include those present in the combined roles
    valid_waiting_roles = [role for role in waiting_roles_values if role in role_values]

    # Define the response data
    data = {
        "status": "success",
        "message": "waiting",
        "roles": valid_waiting_roles if valid_waiting_roles else ["no_role"]
    }

    return JsonResponse(data)
