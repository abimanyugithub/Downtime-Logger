from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='view_index'),
    path('dashboard/', views.Dashboard.as_view(), name='view_dashboard'),
    path('dashboard_new/', views.DashboardNew.as_view(), name='view_dashboard_new'),
    path('mesin/list/', views.ListMesin.as_view(), name='list_mesin'),
    path('mesin/register/', views.RegisterMesin.as_view(), name='register_mesin'),
    path('mesin/<int:pk>/update/', views.UpdateMesin.as_view(), name='update_mesin'),
    path('mesin/<int:pk>/update/status/', views.UpdateStatusMesin.as_view(), name='update_status_mesin'),
    path('mesin/<int:pk>/delete/', views.DeleteMesin.as_view(), name='delete_mesin'),
    
    # path('mesin/number/<int:pk>/', views.DashboardMesin.as_view(), name='number_mesin'),
    path('andon/mesin/', views.DisplayAndon.as_view(), name='view_andon'),
    path('downtime/mesin/', views.StatusDowntimeMesin.as_view(), name='status_downtime_mesin'),
    path('downtime/role/<str:pk>/', views.StatusDowntimeRole.as_view(), name='status_downtime_role'),
    path('downtime/role/delete/<str:pk>/', views.DeleteDowntimeRole.as_view(), name='delete_downtime_role'),

    path('downtime/mesin/list/', views.ListDowntimeMesin.as_view(), name='list_downtime_mesin'),

    # trigger andon esp32
    path('andon/esp32-response/', views.ControlTrigger, name='control_trigger'),

    # htmx response
    path('async-mesin-card/', views.AsyncMesinCard, name='async_card'),
    # path('async-mesin/', views.AsyncMesin, name='async_mesin'),
]
