"""
High-quality ICO file generator with proper transparency support
"""
from PIL import Image
import sys

def create_ico_with_transparency(png_path):
    """
    Creates a high-quality .ico file from PNG with proper alpha channel handling
    """
    try:
        # Open the PNG image
        img = Image.open(png_path)
        
        # Ensure the image has an alpha channel
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Define sizes for Windows icons (including all standard sizes)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Create resized versions with high-quality resampling
        icon_images = []
        for size in sizes:
            # Use LANCZOS for best quality downsampling
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # Save as ICO with all sizes
        output_path = 'icon.ico'
        icon_images[0].save(
            output_path,
            format='ICO',
            sizes=sizes,
            append_images=icon_images[1:]
        )
        
        print(f"✅ Icon created successfully: {output_path}")
        print(f"📐 Sizes included: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        print(f"✨ Transparency: Preserved")
        return output_path
        
    except FileNotFoundError:
        print(f"❌ Error: File '{png_path}' not found!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_high_quality_icon.py <input_png_file>")
        sys.exit(1)
    
    png_file = sys.argv[1]
    create_ico_with_transparency(png_file)
