from core.models import Hardware

def calculate_hardware(design):
    """
    Calculates hardware needed for a given DesignItem based on its typology and quantity.
    Returns a list of dicts: [{'name': '...', 'quantity': ...}]
    """
    hardware_list = Hardware.objects.filter(typology__iexact=design.typology)
    
    results = []
    
    # We parse the formula. E.g. "2 * panels"
    # We know sliding has 2 panels, casement 1
    panels = 2 if design.typology == 'sliding' else 1
    
    # Safe eval context
    context = {'panels': panels}
    
    for hw in hardware_list:
        try:
            # Note: eval should be used very carefully. 
            # For this simple requirement, we trust the DB data or use a simple string replace.
            # Let's use a safer approach:
            formula = hw.quantity_formula.replace('panels', str(panels))
            # simple eval for math
            hw_qty_per_window = eval(formula, {"__builtins__": None}, {})
            total_qty = hw_qty_per_window * design.quantity
            
            results.append({
                'name': hw.name,
                'quantity': total_qty
            })
        except Exception:
            # If formula parsing fails, default to 1 per window
            results.append({
                'name': hw.name,
                'quantity': design.quantity
            })
            
    return results
