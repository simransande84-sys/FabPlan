from django.urls import path
from . import views
from . import views_reports

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('api/orders/create/', views.api_create_order, name='api_create_order'),
    path('order/<int:order_id>/', views.order_details, name='order_details'),
    path('order/<int:order_id>/pdf/', views_reports.download_single_quotation_pdf, name='single_quotation_pdf'),
    path('reports/quotation-pdf/', views_reports.download_quotation_pdf, name='report_quotation_pdf'),
    path('reports/quotation-excel/', views_reports.download_quotation_excel, name='report_quotation_excel'),
    path('reports/material-boq/', views_reports.download_material_boq_pdf, name='report_material_boq_pdf'),
    path('reports/cutting-chart/', views_reports.download_cutting_chart_pdf, name='report_cutting_chart_pdf'),
]
