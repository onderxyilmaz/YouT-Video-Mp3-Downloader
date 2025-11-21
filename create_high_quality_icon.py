from PIL import Image
import sys

def create_high_quality_icon(png_path, ico_path='icon.ico'):
    """
    PNG'den yüksek kaliteli ICO dosyası oluşturur.
    Windows için önerilen tüm boyutları içerir.
    """
    try:
        # PNG'yi aç
        img = Image.open(png_path)
        
        # RGBA moduna çevir (transparency için)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Windows için standart ikon boyutları
        # 256x256: Windows 7+ için yüksek çözünürlük
        # 128x128: Büyük ikonlar
        # 48x48: Orta boy ikonlar
        # 32x32: Küçük ikonlar
        # 16x16: Mini ikonlar (görev çubuğu vb.)
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        
        # Her boyut için optimize edilmiş resimler oluştur
        icon_images = []
        for size in sizes:
            # LANCZOS resampling ile yüksek kaliteli ölçekleme
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
            print(f"✓ {size[0]}x{size[1]} boyutu oluşturuldu")
        
        # ICO dosyasını kaydet
        icon_images[0].save(
            ico_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in icon_images],
            append_images=icon_images[1:]
        )
        
        print(f"\n✅ Yüksek kaliteli ikon başarıyla oluşturuldu: {ico_path}")
        print(f"📦 İçerdiği boyutlar: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python create_high_quality_icon.py <png_dosyasi>")
        print("Örnek: python create_high_quality_icon.py YouT_Image.png")
        sys.exit(1)
    
    png_file = sys.argv[1]
    create_high_quality_icon(png_file)


