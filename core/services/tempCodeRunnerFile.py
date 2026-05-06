def optimize_cuts(cuts, bar_length=6000):
    """
    Implements First-Fit Decreasing (FFD) Bin Packing Algorithm.
    :param cuts: List of dictionaries or objects with 'length' and 'quantity'.
                 For simplicity, let's assume cuts is a flat list of lengths [1200, 1200, 800, ...]
    :param bar_length: Length of a single bar (default 6000mm)
    :return: List of bars, where each bar is a dict with 'cuts', 'leftover', and 'waste_percentage'
    """
    # Sort cuts in descending order
    sorted_cuts = sorted(cuts, reverse=True)
    
    bars = []
    
    for cut in sorted_cuts:
        placed = False
        # Try to place the cut in an existing bar
        for bar in bars:
            if bar['leftover'] >= cut:
                bar['cuts'].append(cut)
                bar['leftover'] -= cut
                placed = True
                break
        
        # If it doesn't fit in any existing bar, create a new one
        if not placed:
            bars.append({
                'cuts': [cut],
                'leftover': bar_length - cut,
                'bar_length': bar_length
            })
            
    # Calculate waste percentage for each bar
    for bar in bars:
        bar['waste_percentage'] = round((bar['leftover'] / bar['bar_length']) * 100, 2)
        
    return bars

def optimize_profile_cuts(cut_pieces):
    """
    Optimizes a queryset of CutPiece objects, grouped by profile.
    :param cut_pieces: Queryset of CutPiece objects
    :return: Dict grouping optimized bars by profile name
    """
    from collections import defaultdict
    
    profile_cuts = defaultdict(list)
    
    for piece in cut_pieces:
        # Flatten the quantities into individual lengths
        for _ in range(piece.quantity):
            profile_cuts[piece.profile].append(piece.length)
            
    optimized_results = {}
    
    for profile, lengths in profile_cuts.items():
        optimized_results[profile.name] = optimize_cuts(lengths, profile.bar_length)
        
    return optimized_results
