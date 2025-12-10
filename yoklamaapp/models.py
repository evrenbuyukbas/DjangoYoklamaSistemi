from django.db import models

# Create your models here.
from django.db import models

class Ogrenci(models.Model):
    """Sistemdeki kayıtlı öğrencileri tutar."""
    ogrenci_no = models.CharField(max_length=10, unique=True)
    ad_soyad = models.CharField(max_length=100)
    # Yüz kodlaması (embedding) verilerini tutmak için ikili alan
    yuz_kodlama = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return f"{selfen.ogrenci_no} - {self.ad_soyad}"

class YoklamaKaydi(models.Model):
    """Öğrenci giriş/çıkış kayıtlarını tutar."""
    ogrenci = models.ForeignKey(Ogrenci, on_delete=models.CASCADE)
    zaman = models.DateTimeField(auto_now_add=True)
    durum = models.CharField(max_length=10, choices=[('GIRIS', 'Giriş'), ('CIKIS', 'Çıkış')])

    def __str__(self):
        return f"{self.ogrenci.ad_soyad} - {self.durum} @ {self.zaman.strftime('%H:%M')}"