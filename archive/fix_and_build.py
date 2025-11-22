"""
.spec dosyasini otomatik duzelt ve build yap
"""
import subprocess
import sys
import os
import re

def fix_spec_file():
    """spec dosyasindaki bilinen hatalari duzelt"""
    spec_file = 'YouT-Video-Mp3-Downloader.spec'

    if not os.path.exists(spec_file):
        print(f"[HATA] {spec_file} bulunamadi!")
        return False

    print(f"[1/3] {spec_file} dosyasi duzeltiliyor...")

    with open(spec_file, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. icon=['icon.ico'] -> icon='icon.ico' duzeltmesi
    content = re.sub(r"icon=\['icon\.ico'\]", "icon='icon.ico'", content)
    content = re.sub(r'icon=\["icon\.ico"\]', "icon='icon.ico'", content)

    # 2. hookspath ekle (yoksa)
    if "hookspath=[]" in content:
        content = content.replace("hookspath=[]", "hookspath=['hooks']")

    if content != original_content:
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] spec dosyasi duzeltildi")
        return True
    else:
        print("[BILGI] spec dosyasi zaten dogru")
        return True

def clean_build():
    """Eski build dosyalarini temizle"""
    print("[2/3] Eski build dosyalari temizleniyor...")

    import shutil
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  - {folder}/ silindi")

    print("[OK] Temizlik tamamlandi")

def build():
    """PyInstaller ile build yap"""
    print("[3/3] PyInstaller build baslatiliyor...")
    print()

    try:
        subprocess.check_call([sys.executable, 'build_exe.py'])
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[HATA] Build basarisiz: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  YouT Video Mp3 Downloader - Otomatik Build")
    print("="*60)
    print()

    # 1. Spec dosyasini duzelt
    if not fix_spec_file():
        sys.exit(1)

    # 2. Temizlik yap
    clean_build()

    # 3. Build yap
    if build():
        print()
        print("="*60)
        print("[BASARILI] Build tamamlandi!")
        print("="*60)
        print()
        print("Sonraki adim: Installer olusturun")
        print('  iscc installer_script.iss')
        print()
        print('veya tam yol:')
        print('  "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" installer_script.iss')
    else:
        print()
        print("="*60)
        print("[BASARISIZ] Build hatasi!")
        print("="*60)
        sys.exit(1)
