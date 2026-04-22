# core/views_reports.py
from django.http import HttpResponse
from .services import reports

def download_quotation_pdf(request):
    buffer = reports.generate_quotation_pdf()
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="quotation.pdf"'
    return response

def download_quotation_excel(request):
    buffer = reports.generate_quotation_excel()
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="quotation.xlsx"'
    return response

def download_material_boq_pdf(request):
    buffer = reports.generate_material_boq_pdf()
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="material_boq.pdf"'
    return response

def download_cutting_chart_pdf(request):
    buffer = reports.generate_cutting_chart_pdf()
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cutting_chart.pdf"'
    return response

def download_single_quotation_pdf(request, order_id):
    buffer = reports.generate_single_quotation_pdf(order_id)
    if not buffer:
        from django.http import Http404
        raise Http404("Order not found")
        
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quotation_{order_id}.pdf"'
    return response
