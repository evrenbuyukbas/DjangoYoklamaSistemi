from django.shortcuts import render

# Create your views here.
# yoklamaapp/views.py

from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .face_core import tanima_islemi, kodlamalari_yukle
from .models import Ogrenci, YoklamaKaydi
import cv2
import numpy as np
import base64
import face_recognition

# Kamerayı global olarak başlat
try:
    Kamera = cv2.VideoCapture(0)
except Exception:
    Kamera = None

def gen(kamera):
    """Video akışını JPEG formatında bayt bayt yayınlamak için generator."""
    if kamera is None or not kamera.isOpened():
        # Kamera yoksa boş bir kare döndür (Hata mesajı için)
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(img, "Kamera Acilamadi!", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        ret, jpeg = cv2.imencode('.jpg', img)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        return

    while True:
        ret, frame = kamera.read()
        if not ret:
            break
        
        # Yüz tanıma işlemini frame üzerinde yap
        frame = tanima_islemi(frame)
        
        # Frame'i JPEG formatında baytlara dönüştür
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        
        # Stream yanıtı için format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def video_feed(request):
    """Video feed'i HTTP üzerinden yayınlar."""
    return StreamingHttpResponse(gen(Kamera), content_type='multipart/x-mixed-replace; boundary=frame')

def dashboard(request):
    """Ana kontrol paneli görünümü."""
    
    # Sınıfın anlık mevcudunu hesapla
    mevcut_ogrenciler = []
    
    # Tüm öğrencilerin son durumunu kontrol et
    for ogrenci in Ogrenci.objects.all().order_by('ad_soyad'):
        son_kayit = YoklamaKaydi.objects.filter(ogrenci=ogrenci).order_by('-zaman').first()
        
        durum = 'CIKIS' # Varsayılan: Dışarıda
        if son_kayit and son_kayit.durum == 'GIRIS':
            durum = 'GIRIS'
            
        mevcut_ogrenciler.append({
            'ad_soyad': ogrenci.ad_soyad,
            'ogrenci_no': ogrenci.ogrenci_no,
            'durum': durum,
            'son_zaman': son_kayit.zaman if son_kayit else '---'
        })

    return render(request, 'yoklamaapp/dashboard.html', {
        'mevcut_listesi': mevcut_ogrenciler,
        'kamera_acik': Kamera is not None and Kamera.isOpened()
    })

@csrf_exempt
def kayit_ekle(request):
    """Yeni öğrenci kaydı yapar ve kodlamayı veritabanına kaydeder."""
    
    if request.method == 'POST':
        ogrenci_no = request.POST.get('ogrenci_no')
        ad_soyad = request.POST.get('ad_soyad')
        foto_base64 = request.POST.get('foto')

        if not ogrenci_no or not ad_soyad or not foto_base64:
            return JsonResponse({'success': False, 'message': 'Eksik bilgi.'})

        try:
            # 1. Fotoğrafı Base64'ten NumPy dizisine çevir
            foto_bytes = base64.b64decode(foto_base64.split(',')[1])
            np_arr = np.frombuffer(foto_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # 2. Yüzü bul ve kodla
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yuz_kodlamalari = face_recognition.face_encodings(rgb_frame)

            if len(yuz_kodlamalari) == 0:
                return JsonResponse({'success': False, 'message': 'Fotoğrafta yüz bulunamadı.'})
            
            yuz_kodlama = yuz_kodlamalari[0]
            
            # 3. Öğrenciyi veritabanına kaydet
            ogrenci, created = Ogrenci.objects.update_or_create(
                ogrenci_no=ogrenci_no,
                defaults={
                    'ad_soyad': ad_soyad,
                    'yuz_kodlama': yuz_kodlama.tobytes() # numpy array'i binary olarak kaydet
                }
            )

            return JsonResponse({'success': True, 'message': f'{ad_soyad} başarıyla kaydedildi!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Hata oluştu: {str(e)}'})

    return render(request, 'yoklamaapp/kayit_ekle.html')