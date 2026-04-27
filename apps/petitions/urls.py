from django.urls import path
from . import views

urlpatterns = [
    # Crear petición
    path('new/', views.create_petition, name='create_petition'),

    # Votaciones
    path('vote/<int:petition_id>/', views.toggle_vote, name='toggle_vote'),

    # Comentarios
    path('comment/<int:petition_id>/', views.add_comment, name='add_comment'),

    # Reportes del usuario
    path('my-reports/', views.my_reports, name='my_reports'),
    path('notifications/', views.notifications, name='notifications'),

    # Moderación
    path('moderation/reports/', views.admin_reports, name='admin_reports'),
    path('moderation/report/<int:report_id>/resolve/', views.resolve_report, name='resolve_report'),
    path('moderation/report/<int:report_id>/delete/', views.delete_reported_content, name='delete_reported_content'),
    path('moderation/admin/followup/<int:petition_id>/', views.add_followup, name='add_followup'),
    # Reportar contenido
    path('report/', views.report_content, name='report_content'),

    # Detalle de petición
    path('<int:petition_id>/', views.petition_detail, name='petition_detail'),

    # Lista de peticiones (HOME)
    path('', views.petition_list, name='petition_list'),
]
