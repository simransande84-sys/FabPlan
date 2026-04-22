from core.models import Profile, CutPiece

def generate_cut_pieces(design):
    """
    Generates CutPiece records based on the DesignItem dimensions and typology.
    """
    # Get profiles
    try:
        frame_profile = Profile.objects.get(type='frame')
    except Profile.DoesNotExist:
        frame_profile = None

    try:
        sash_profile = Profile.objects.get(type='sash')
    except Profile.DoesNotExist:
        sash_profile = None

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
    # Note: sliding defaults to 2 panels based on requirements
    if sash_profile and design.typology in ['sliding', 'casement']:
        panels = 2 if design.typology == 'sliding' else 1
        
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
