import face_recognition
import numpy as np
import cv2
from .models import Ogrenci, YoklamaKaydi
import time

# Pillow Kütüphanesinden Gerekli Modülleri Import Et (Yeni Eklendi)
from PIL import ImageFont, ImageDraw, Image

# --- Ayarlar ---
LAST_SEEN_TIME = {}
TEKRAR_SURESI = 30 # saniye

# TÜRKÇE KARAKTER İÇİN KRİTİK AYAR
# 'arial.ttf' dosyasını YoklamaProjesi klasörüne kopyaladığınızı varsayıyoruz
FONT_YOLU = "arial.ttf" 
FONT_BOYUTU = 30
# ---------------


def kodlamalari_yukle():
    """Veritabanından tüm öğrenci kodlamalarını yükler."""
    ogrenciler = Ogrenci.objects.exclude(yuz_kodlama__isnull=True)
    
    bilinen_kodlar = []
    bilinen_objeler = [] 
    
    for ogrenci in ogrenciler:
        if ogrenci.yuz_kodlama:
            kodlama = np.frombuffer(ogrenci.yuz_kodlama, dtype=np.float64)
            bilinen_kodlar.append(kodlama)
            bilinen_objeler.append(ogrenci)
            
    return bilinen_kodlar, bilinen_objeler

# yoklamaapp/face_core.py içindeki tanima_islemi fonksiyonu (GÜNCEL VE KUTU DÜZELTMELİ)

# yoklamaapp/face_core.py içindeki tanima_islemi fonksiyonu (PIL ÇİZİMİ GARANTİSİ)

# yoklamaapp/face_core.py içindeki tanima_islemi fonksiyonunun TAM VE TEMİZ HALİ

def tanima_islemi(frame):
    
    bilinen_kodlar, bilinen_objeler = kodlamalari_yukle()
    
    # 1. Türkçe karakter yazmak için çerçeveyi PIL formatına dönüştür
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype(FONT_YOLU, FONT_BOYUTU)
    except IOError:
        font = ImageFont.load_default() 
        
    
    if not bilinen_kodlar:
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Performans için kareyi küçültme ve yüz tanıma
    kare_kucuk = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_kare = cv2.cvtColor(kare_kucuk, cv2.COLOR_BGR2RGB)

    yuz_konumlar = face_recognition.face_locations(rgb_kare)
    yuz_kodlamalari = face_recognition.face_encodings(rgb_kare, yuz_konumlar)
    
    
    for yuz_kodlama, yuz_konum in zip(yuz_kodlamalari, yuz_konumlar):
        
        # Tanıma Mantığı
        eslesmeler = face_recognition.compare_faces(bilinen_kodlar, yuz_kodlama, tolerance=0.6)
        isim = "Bilinmiyor"
        renk_rgb = (255, 0, 0) # Kırmızı (PIL için RGB)
        
        if True in eslesmeler:
            yuz_mesafeleri = face_recognition.face_distance(bilinen_kodlar, yuz_kodlama)
            en_iyi_eslesme_indeksi = np.argmin(yuz_mesafeleri)
            
            if eslesmeler[en_iyi_eslesme_indeksi]:
                taninan_ogrenci = bilinen_objeler[en_iyi_eslesme_indeksi]
                isim = taninan_ogrenci.ad_soyad 
                renk_rgb = (0, 255, 0) # Yeşil (PIL için RGB)
                
                # Yoklama Kontrolü (Mantık aynı kalır)
                simdi = time.time()
                if (simdi - LAST_SEEN_TIME.get(taninan_ogrenci.ogrenci_no, 0)) > TEKRAR_SURESI:
                    son_kayit = YoklamaKaydi.objects.filter(ogrenci=taninan_ogrenci).order_by('-zaman').first()
                    yeni_durum = 'GIRIS' if son_kayit is None or son_kayit.durum == 'CIKIS' else 'CIKIS'
                    YoklamaKaydi.objects.create(ogrenci=taninan_ogrenci, durum=yeni_durum)
                    LAST_SEEN_TIME[taninan_ogrenci.ogrenci_no] = simdi
                    print(f"-> {isim} {yeni_durum} Kaydı Yapıldı.")

        # 2. Koordinatları ölçeklendir
        ust, sag, alt, sol = [k * 4 for k in yuz_konum] 
        
        # 3. Yüz çevresine kutu çizme (PIL KULLANILARAK)
        draw.rectangle(
            [(sol, ust), (sag, alt)],
            outline=renk_rgb, 
            width=2           
        )
        
        
        # 4. Türkçe Karakterli İsim Yazma (PIL üzerinde)
        
        # a) Metin Arka Planını Çiz (Kutunun hemen altı)
        draw.rectangle(
            [sol, alt - FONT_BOYUTU - 3, sag, alt], 
            fill=renk_rgb
        ) 
        
        # b) Metni çiz (KESİNLİKLE KIRMIZI)
        draw.text(
            (sol + 6, alt - FONT_BOYUTU - 3), 
            isim, 
            font=font, 
            fill=(255, 0, 0) # <--- SADECE BURADA KIRMIZIYI ZORLUYORUZ
        ) 

    
    # 5. PIL görüntüsünü tekrar OpenCV/NumPy dizisine dönüştürerek döndür
    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return frame
    
    bilinen_kodlar, bilinen_objeler = kodlamalari_yukle()
    
    # 1. Türkçe karakter yazmak için çerçeveyi PIL formatına dönüştür
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)
    # GITHUB TEST
    # GITHUB TEST-2
    # GITHUB TEST-3
    # GITHUB TEST-4
    try:
        font = ImageFont.truetype(FONT_YOLU, FONT_BOYUTU)
    except IOError:
        font = ImageFont.load_default() 
        
    
    if not bilinen_kodlar:
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Performans için kareyi küçültme ve yüz tanıma
    kare_kucuk = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_kare = cv2.cvtColor(kare_kucuk, cv2.COLOR_BGR2RGB)

    yuz_konumlar = face_recognition.face_locations(rgb_kare)
    yuz_kodlamalari = face_recognition.face_encodings(rgb_kare, yuz_konumlar)
    
    
    for yuz_kodlama, yuz_konum in zip(yuz_kodlamalari, yuz_konumlar):
        
        # Tanıma Mantığı
        eslesmeler = face_recognition.compare_faces(bilinen_kodlar, yuz_kodlama, tolerance=0.6)
        isim = "Bilinmiyor"
        renk_rgb = (255, 0, 0) # Kırmızı (PIL için RGB)
        
        if True in eslesmeler:
            yuz_mesafeleri = face_recognition.face_distance(bilinen_kodlar, yuz_kodlama)
            en_iyi_eslesme_indeksi = np.argmin(yuz_mesafeleri)
            
            if eslesmeler[en_iyi_eslesme_indeksi]:
                taninan_ogrenci = bilinen_objeler[en_iyi_eslesme_indeksi]
                isim = taninan_ogrenci.ad_soyad 
                renk_rgb = (0, 255, 0) # Yeşil (PIL için RGB)
                
                # Yoklama Kontrolü (Aynı Mantık)
                simdi = time.time()
                if (simdi - LAST_SEEN_TIME.get(taninan_ogrenci.ogrenci_no, 0)) > TEKRAR_SURESI:
                    son_kayit = YoklamaKaydi.objects.filter(ogrenci=taninan_ogrenci).order_by('-zaman').first()
                    yeni_durum = 'GIRIS' if son_kayit is None or son_kayit.durum == 'CIKIS' else 'CIKIS'
                    YoklamaKaydi.objects.create(ogrenci=taninan_ogrenci, durum=yeni_durum)
                    LAST_SEEN_TIME[taninan_ogrenci.ogrenci_no] = simdi
                    print(f"-> {isim} {yeni_durum} Kaydı Yapıldı.")

        # 2. Koordinatları ölçeklendir
        ust, sag, alt, sol = [k * 4 for k in yuz_konum] 
        
        
        # 3. Yüz çevresine kutu çizme (TAMAMEN PIL KULLANARAK)
        # Koordinatlar: (sol, üst), (sağ, alt)
        draw.rectangle(
            [(sol, ust), (sag, alt)],
            outline=renk_rgb, # Kutu rengi
            width=2           # Kutu kalınlığı
        )
        
        
        # 4. Türkçe Karakterli İsim Yazma (PIL üzerinde)
        
        # a) Metin Arka Planını Çiz (Kutunun hemen altı)
        draw.rectangle(
            [sol, alt - FONT_BOYUTU - 5, sag, alt], 
            fill=renk_rgb
        ) 
        
        # b) Metni çiz
        draw.text(
            (sol + 6, alt - FONT_BOYUTU - 5), 
            isim, 
            font=font, 
            fill=(255, 255, 255) # Metin beyaz
        ) 

    
    # 5. PIL görüntüsünü tekrar OpenCV/NumPy dizisine dönüştürerek döndür
    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return frame
    
    bilinen_kodlar, bilinen_objeler = kodlamalari_yukle()
    
    # Performans için kareyi küçültme ve yüz tanıma
    kare_kucuk = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_kare = cv2.cvtColor(kare_kucuk, cv2.COLOR_BGR2RGB)

    yuz_konumlar = face_recognition.face_locations(rgb_kare)
    yuz_kodlamalari = face_recognition.face_encodings(rgb_kare, yuz_konumlar)
    
    # 1. PIL nesnesini burada oluşturacağız, ancak içine çizim yapmayı daha sonra yapacağız
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)
    
    try:
        font = ImageFont.truetype(FONT_YOLU, FONT_BOYUTU)
    except IOError:
        font = ImageFont.load_default() 
        
    if not bilinen_kodlar:
        # Eğer kodlama yoksa, PIL'den tekrar CV2'ye çevirip döndür
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    
    for yuz_kodlama, yuz_konum in zip(yuz_kodlamalari, yuz_konumlar):
        
        # Tanıma Mantığı
        # ... (Tanıma ve Yoklama Mantığı Aynı Kalır) ...
        eslesmeler = face_recognition.compare_faces(bilinen_kodlar, yuz_kodlama, tolerance=0.6)
        isim = "Bilinmiyor"
        renk_bgr = (0, 0, 255) # Kırmızı (OpenCV için BGR)
        renk_rgb = (255, 0, 0) # Kırmızı (PIL için RGB)
        
        if True in eslesmeler:
            yuz_mesafeleri = face_recognition.face_distance(bilinen_kodlar, yuz_kodlama)
            en_iyi_eslesme_indeksi = np.argmin(yuz_mesafeleri)
            
            if eslesmeler[en_iyi_eslesme_indeksi]:
                taninan_ogrenci = bilinen_objeler[en_iyi_eslesme_indeksi]
                isim = taninan_ogrenci.ad_soyad 
                renk_bgr = (0, 255, 0) # Yeşil (BGR)
                renk_rgb = (0, 255, 0) # Yeşil (RGB)
                
                # Yoklama Kontrolü
                simdi = time.time()
                if (simdi - LAST_SEEN_TIME.get(taninan_ogrenci.ogrenci_no, 0)) > TEKRAR_SURESI:
                    son_kayit = YoklamaKaydi.objects.filter(ogrenci=taninan_ogrenci).order_by('-zaman').first()
                    yeni_durum = 'GIRIS' if son_kayit is None or son_kayit.durum == 'CIKIS' else 'CIKIS'
                    YoklamaKaydi.objects.create(ogrenci=taninan_ogrenci, durum=yeni_durum)
                    LAST_SEEN_TIME[taninan_ogrenci.ogrenci_no] = simdi
                    print(f"-> {isim} {yeni_durum} Kaydı Yapıldı.")

        # 2. Yüz çevresine kutu çizme (OpenCV frame üzerinde)
        ust, sag, alt, sol = [k * 4 for k in yuz_konum] 
        
        # Yüz Kutusu Çizimi (OpenCV)
        cv2.rectangle(frame, (sol, ust), (sag, alt), renk_bgr, 2)
        
        
        # 3. Türkçe Karakterli İsim Yazma (PIL üzerinde)
        
        # a) Metin Arka Planını PIL'e Çiz
        # Bu kısım, çizim nesnesi (draw) üzerinde çalıştığı için PIL'i kullanır.
        draw.rectangle([sol, alt - FONT_BOYUTU - 3, sag, alt], fill=renk_rgb) 
        
        # b) Metni PIL görüntüsü üzerine çiz (Türkçe karakter desteği)
        draw.text((sol + 6, alt - FONT_BOYUTU - 3), isim, font=font, fill=(255, 0, 0)) 

    
    # 4. PIL görüntüsünü tekrar OpenCV/NumPy dizisine dönüştürerek döndür
    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return frame