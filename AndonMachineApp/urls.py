from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardInjection.as_view(), name='dashboard_mesin_injection'),
    path('dashboard/blow', views.DashboardBlow.as_view(), name='dashboard_mesin_blow'),
    path('mesin/list/', views.ListMesin.as_view(), name='list_mesin'),
    path('mesin/register/', views.RegisterMesin.as_view(), name='register_mesin'),
    path('mesin/<int:pk>/update/', views.UpdateMesin.as_view(), name='update_mesin'),
    path('mesin/<int:pk>/update/status', views.UpdateStatusMesin.as_view(), name='update_status_mesin'),
    path('mesin/<int:pk>/delete/', views.DeleteMesin.as_view(), name='delete_mesin'),
    path('mesin/number/<int:pk>/', views.DashboardMesin.as_view(), name='number_mesin'),

    # htmx response
    path('async-mesin-card/', views.AsyncMesinCard, name='async_mesin_card'),
    path('async-mesin/', views.AsyncMesin, name='async_mesin'),
]
