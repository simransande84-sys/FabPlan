import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from .models import Order, DesignItem, CutPiece
from .services.cutting_engine import generate_cut_pieces
from .services.hardware_engine import calculate_hardware
from .services.glass_engine import calculate_glass
from .services.bar_optimizer import optimize_profile_cuts

def landing_page(request):
    return render(request, 'core/landing.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'orders': orders,
        'typology_choices': DesignItem.TYPOLOGY_CHOICES,
        'product_choices': DesignItem.PRODUCT_CHOICES
    }
    return render(request, 'core/dashboard.html', context)

@login_required
@csrf_exempt
def api_create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_code = data.get('code')
            customer_name = data.get('customer_name')
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'success': False, 'error': 'No items in order'})
                
            order = Order.objects.create(code=order_code, customer_name=customer_name)
            
            for item in items:
                design = DesignItem.objects.create(
                    order=order,
                    product_type=item.get('product_type', 'window'),
                    width=float(item.get('width')),
                    height=float(item.get('height')),
                    typology=item.get('typology'),
                    glass_type=item.get('glass_type'),
                    finish=item.get('finish'),
                    mesh=item.get('mesh') == True or item.get('mesh') == 'on',
                    quantity=int(item.get('quantity', 1))
                )
                generate_cut_pieces(design)
                
            return JsonResponse({'success': True, 'order_id': order.id, 'message': f'Order {order.code} created successfully.'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.GET.get('recalculate') == 'true':
        for design in order.designs.all():
            design.cut_pieces.all().delete()
            generate_cut_pieces(design)
            
    total_profile_cost = 0
    total_hw_cost = 0
    total_glass_cost = 0
    total_labor_cost = 0
    
    designs_data = []
    all_cuts_qs = CutPiece.objects.filter(design__order=order)
    
    for design in order.designs.all():
        profile_cost = sum((cut.profile.cost_per_bar / cut.profile.bar_length) * cut.length * cut.quantity for cut in design.cut_pieces.all())
        
        hw_list = calculate_hardware(design)
        hw_cost = sum(hw['quantity'] * 50 for hw in hw_list)
        
        glass_list = calculate_glass(design)
        glass_cost = sum(((g['width'] / 1000) * (g['height'] / 1000)) * g['quantity'] * 100 for g in glass_list)
        
        labor_cost = 200 * design.quantity
        
        total_profile_cost += profile_cost
        total_hw_cost += hw_cost
        total_glass_cost += glass_cost
        total_labor_cost += labor_cost
        
        designs_data.append({
            "id": design.id,
            "product": design.get_product_type_display(),
            "typology": design.get_typology_display(),
            "dimensions": f"{design.width}x{design.height}",
            "quantity": design.quantity,
            "cost": round(profile_cost + hw_cost + glass_cost + labor_cost, 2)
        })

    cuts_data = [
        {"profile": c.profile.name, "length": c.length, "quantity": c.quantity}
        for c in all_cuts_qs
    ]
    
    optimized = optimize_profile_cuts(all_cuts_qs)
    
    total_waste_sum = 0
    total_bars = 0
    for bars in optimized.values():
        for bar in bars:
            total_waste_sum += bar.get('waste_percentage', 0)
            total_bars += 1
            
    avg_waste = round(total_waste_sum / total_bars, 2) if total_bars > 0 else 0
    
    total_cost = total_profile_cost + total_hw_cost + total_glass_cost + total_labor_cost
    
    # Aggregate hardware and glass
    agg_glass = []
    agg_hw = []
    for design in order.designs.all():
        agg_glass.extend(calculate_glass(design))
        agg_hw.extend(calculate_hardware(design))
        
    data = {
        "id": order.id,
        "code": order.code,
        "customer": order.customer_name or 'N/A',
        "designs": designs_data,
        "costs": {
            "profile": round(total_profile_cost, 2),
            "hardware": round(total_hw_cost, 2),
            "glass": round(total_glass_cost, 2),
            "labor": round(total_labor_cost, 2),
            "total": round(total_cost, 2)
        },
        "summary": {
            "avg_waste": avg_waste,
            "total_bars_used": total_bars
        },
        "cutting_plan": {
            "cuts": cuts_data,
            "optimized": optimized
        },
        "glass": agg_glass,
        "hardware": agg_hw
    }
    
    return JsonResponse(data)
