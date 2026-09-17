import sys, os
sys.path.insert(0, '.')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)

from core.splash_screen import SplashScreen
print("  OK splash_screen")

from core.desktop import Desktop
print("  OK desktop (con boton cierre)")

from core.sound_manager import SoundManager
print("  OK sound_manager")

from core.resource_manager import ResourceManager
r = ResourceManager()

sounds = ['startup','click','window_open','window_close','error','notification','minimize','balloon']
all_ok = True
for s in sounds:
    path = r.get_sound_path(s)
    status = "OK" if path else "FALTA"
    if not path:
        all_ok = False
    print(f"  {status} {s}.wav")

if all_ok:
    print("Todo listo! 8/8 sonidos encontrados.")
else:
    print("Faltan algunos sonidos.")
