import bpy

def scale_images_direct(scale_factor=4.0):
    """
    Directly scales image strips and adjusts positions using absolute frame calculations.
    """
    scene = bpy.context.scene
    seq_editor = scene.sequence_editor
    
    if not seq_editor:
        return "No sequence editor found."
    
    # First, gather all strips and sort by start frame
    all_strips = []
    for strip in seq_editor.sequences_all:
        all_strips.append({
            'strip': strip,
            'original_start': strip.frame_start,
            'original_duration': strip.frame_final_duration,
            'channel': strip.channel
        })
    
    # Sort by start frame to process in order
    all_strips.sort(key=lambda x: x['original_start'])
    
    # Track how much space we've added before each position
    total_offset = 0
    
    # Process each strip
    for strip_data in all_strips:
        strip = strip_data['strip']
        
        # Move strip by current total offset
        strip.frame_start = strip_data['original_start'] + total_offset
        
        # If it's an image, scale it and update total offset
        if strip.type == 'IMAGE':
            new_duration = int(strip_data['original_duration'] * scale_factor)
            strip.frame_final_duration = new_duration
            total_offset += (new_duration - strip_data['original_duration'])
            
            # Handle transform strips for this image
            for seq in seq_editor.sequences_all:
                if (seq.type == 'TRANSFORM' and 
                    hasattr(seq, 'input_1') and 
                    seq.input_1 == strip):
                    seq.frame_start = strip.frame_start
                    seq.frame_final_duration = new_duration
                    if seq.animation_data and seq.animation_data.action:
                        action = seq.animation_data.action
                        for fcurve in action.fcurves:
                            for keyframe in fcurve.keyframe_points:
                                # Calculate relative position and scale it
                                relative_pos = (keyframe.co[0] - strip_data['original_start']) / strip_data['original_duration']
                                keyframe.co[0] = strip.frame_start + (relative_pos * new_duration)
    
    # Update scene end frame
    scene.frame_end = max(s.frame_final_end for s in seq_editor.sequences_all)
    
    return (f"Processing complete.\n"
            f"Total timeline expansion: {total_offset} frames.")

# Run the function
result = scale_images_direct(scale_factor=4.0)
print(result)
