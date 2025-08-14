#!/usr/bin/env python3
"""
YAZ Logo Generator
Creates PNG versions of the YAZ logo using PIL/Pillow
Black and white geometric design
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_yaz_logo_png(background_color="white", text_color="black"):
    """Create a modern PNG version of the YAZ logo with geometric letterforms"""
    
    # Create image
    width, height = 400, 120
    img = Image.new('RGBA', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a modern geometric font, fallback to default
    try:
        font_size = 70
        # Try different system fonts for geometric look
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Arial.ttf"
        ]
        font = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Letter positions with proper spacing for geometric letters
    y_pos = height // 2
    letter_spacing = 120
    start_x = 70
    
    # Draw Y - Sharp and angular
    x_y = start_x
    draw.text((x_y, y_pos), "Y", fill=text_color, font=font, anchor="mm")
    
    # Draw A - Traditional triangular structure  
    x_a = x_y + letter_spacing
    draw.text((x_a, y_pos), "A", fill=text_color, font=font, anchor="mm")
    
    # Draw Z - Straight and angular
    x_z = x_a + letter_spacing
    draw.text((x_z, y_pos), "Z", fill=text_color, font=font, anchor="mm")
    
    return img

def create_icon_version(background_color="white", text_color="black"):
    """Create a circular icon version"""
    size = 256
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle
    center = size // 2
    radius = center - 10
    
    # Draw background circle
    draw.ellipse([center - radius, center - radius, 
                  center + radius, center + radius], 
                 fill=background_color, outline=text_color, width=4)
    
    # Draw YAZ text
    try:
        font_size = 60
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        font = None
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    draw.text((center, center), "YAZ", fill=text_color, 
              font=font, anchor="mm")
    
    return img

if __name__ == "__main__":
    # Ensure logos directory exists
    logos_dir = "/workspaces/yaz/static/logos"
    os.makedirs(logos_dir, exist_ok=True)
    
    # Create and save white background logo
    logo_white = create_yaz_logo_png("white", "black")
    logo_white.save(os.path.join(logos_dir, "yaz_logo_white.png"))
    
    # Create and save black background logo
    logo_black = create_yaz_logo_png("black", "white")
    logo_black.save(os.path.join(logos_dir, "yaz_logo_black.png"))
    
    # Create and save white background icon
    icon_white = create_icon_version("white", "black")
    icon_white.save(os.path.join(logos_dir, "yaz_icon_white.png"))
    
    # Create and save black background icon
    icon_black = create_icon_version("black", "white")
    icon_black.save(os.path.join(logos_dir, "yaz_icon_black.png"))
    
    print("✅ YAZ black and white logos created successfully!")
    print(f"   📁 Saved to: {logos_dir}")
    print("   📄 Files created:")
    print("      - yaz_logo.svg (main logo - white bg)")
    print("      - yaz_logo_horizontal.svg (horizontal layout - white bg)")
    print("      - yaz_logo_dark.svg (black background)")
    print("      - yaz_minimal.svg (minimal version)")
    print("      - yaz_icon.svg (circular icon)")
    print("      - yaz_logo_white.png (PNG white background)")
    print("      - yaz_logo_black.png (PNG black background)")
    print("      - yaz_icon_white.png (PNG icon white background)")
    print("      - yaz_icon_black.png (PNG icon black background)")
