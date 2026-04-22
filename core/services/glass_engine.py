def calculate_glass(design):
    """
    Calculates glass pane sizes based on design dimensions.
    Assumes standard clearance of 20mm per side per pane.
    """
    results = []
    
    if design.typology == 'fixed':
        # 1 Pane
        w = design.width - 40
        h = design.height - 40
        results.append({'width': w, 'height': h, 'quantity': 1 * design.quantity})
        
    elif design.typology == 'casement':
        # 1 Pane
        w = design.width - 40
        h = design.height - 40
        results.append({'width': w, 'height': h, 'quantity': 1 * design.quantity})
        
    elif design.typology == 'sliding':
        # 2 Panels
        w = (design.width / 2) - 40
        h = design.height - 40
        results.append({'width': w, 'height': h, 'quantity': 2 * design.quantity})
        
    return results
