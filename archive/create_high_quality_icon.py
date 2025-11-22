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
        
        # Define sizes for Windows icons (including desktop icon sizes)
        # Desktop: 32x32 (small), 48x48 (medium/default), 96x96 (large)
        # Also include 16, 24, 64, 128, 256 for all scenarios
        sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (96, 96), (128, 128), (256, 256)]
        
        # Create resized versions with high-quality resampling
        icon_images = []
        for size in sizes:
            # Use LANCZOS for best quality downsampling
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # Save as ICO with all sizes
        # PIL's ICO format: first image + append_images list
        output_path = 'icon.ico'
        
        # Save with all images - PIL will automatically include all sizes
        if len(icon_images) > 1:
            icon_images[0].save(
                output_path,
                format='ICO',
                sizes=[(img.width, img.height) for img in icon_images],
                append_images=icon_images[1:]
            )
        else:
            icon_images[0].save(output_path, format='ICO')
        
        # Verify the ICO file contains multiple sizes
        try:
            verify_img = Image.open(output_path)
            # Try to get all sizes from the ICO
            if hasattr(verify_img, 'info'):
                saved_info = verify_img.info
                if 'sizes' in saved_info:
                    print(f"📋 Verified sizes in ICO: {saved_info['sizes']}")
                else:
                    print(f"⚠️  Warning: Could not verify sizes, but ICO created successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not verify ICO: {e}")
        
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
