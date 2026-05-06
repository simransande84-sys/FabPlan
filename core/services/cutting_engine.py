from core.models import Profile, CutPiece

def get_best_profile(design, profile_type):
    """
    Intelligently fetch the best matching profile based on typology and product type.
    """
    # Try exact match with product type and typology
    profile = Profile.objects.filter(
        type=profile_type
    ).filter(
        name__icontains=design.typology
    ).filter(
        name__icontains=design.product_type
    ).first()
    
    if profile:
        return profile
        
    # Try match with typology only
    profile = Profile.objects.filter(
        type=profile_type,
        name__icontains=design.typology
    ).first()
    
    if profile:
        return profile
        
    # Fallback to any profile of this type
    return Profile.objects.filter(type=profile_type).first()

def generate_cut_pieces(design):
    """
    Generates CutPiece records based on the DesignItem dimensions and typology.
    """
    # Intelligently get profiles based on design typology and product type
    frame_profile = get_best_profile(design, 'frame')
    sash_profile = get_best_profile(design, 'sash')

    pieces_to_create = []

    # 1. Frame Cuts
    if frame_profile:
        frame_w_cut = design.width - 10
        frame_h_cut = design.height - 10
        
        # 2 Horizontal, 2 Vertical per window
        pieces_to_create.append(CutPiece(
            design=design,
            profile=frame_profile,
            length=frame_w_cut,
            quantity=2 * design.quantity
        ))
        pieces_to_create.append(CutPiece(
            design=design,
            profile=frame_profile,
            length=frame_h_cut,
            quantity=2 * design.quantity
        ))

    # 2. Sash Cuts
    if sash_profile and design.typology in ['sliding', 'casement']:
        panels = design.number_of_panels
        
        sash_h_cut = design.height - 54
        sash_w_cut = (design.width / panels) - 26
        
        # 2 Horizontal, 2 Vertical PER PANEL per window
        pieces_to_create.append(CutPiece(
            design=design,
            profile=sash_profile,
            length=sash_w_cut,
            quantity=2 * panels * design.quantity
        ))
        pieces_to_create.append(CutPiece(
            design=design,
            profile=sash_profile,
            length=sash_h_cut,
            quantity=2 * panels * design.quantity
        ))

    # Bulk create for efficiency
    if pieces_to_create:
        CutPiece.objects.bulk_create(pieces_to_create)
