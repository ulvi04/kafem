# SmartCafe - Restoran Sipariş Sistemi

SmartCafe, QR kod tabanlı güvenli restoran sipariş sistemidir. Token korumalı masa erişimi, rol tabanlı yönetim, fotoğraflı menü sistemi ve gelir takibi özelliklerine sahiptir.

## Özellikler

### 🔐 Güvenlik
- Her masa için benzersiz token sistemi
- QR kod ile güvenli masa erişimi
- IP adresi ve tarayıcı bilgisi loglaması
- Rate limiting ile DDoS koruması

### 👥 Rol Tabanlı Yönetim
- **Admin**: Tüm restoranları yönetir
- **Restoran Sahibi**: Kendi restoranını yönetir
- **Ofisiant**: Siparişleri görüntüler ve yönetir

### 📷 Menü Sistemi
- Fotoğraflı ürün ekleme
- Kategori bazlı düzenleme
- Fiyat ve stok yönetimi

### 🧾 Sipariş Yönetimi
- QR kod ile müşteri girişi
- Sepet sistemi
- Çek (fiş) gösterimi
- Sipariş durumu takibi

### 📊 Gelir Takibi
- Günlük, haftalık, aylık raporlar
- Restoran bazlı gelir analizi
- Sipariş istatistikleri

## Kurulum

### Gereksinimler
- Python 3.8+
- Flask ve bağımlılıkları
- SQLite (veya PostgreSQL)

### Adımlar

1. **Sanal ortam oluşturun:**
```bash
cd /workspace/smartcafe
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Ortam değişkenlerini ayarlayın:**
```bash
cp .env.example .env
```

4. **Veritabanını başlatın:**
```bash
flask init-db
```

5. **Uygulamayı çalıştırın:**
```bash
python run.py
```

Uygulama `http://localhost:5000` adresinde çalışacaktır.

## Kullanım

### İlk Giriş
Kurulum sonrası aşağıdaki hesapları kullanabilirsiniz:

- **Admin**: `admin` / `admin123`
- **Restoran Sahibi**: `restoran1` / `restoran123`
- **Ofisiant**: `ofisiant1` / `ofisiant123`

### QR Kod Kullanımı
1. Admin veya restoran sahibi olarak giriş yapın
2. Masalar bölümünden QR kodları indirin
3. QR kodları masalara yerleştirin
4. Müşteriler QR kodu okutarak sipariş verebilir

## API Endpoints

### Müşteri
- `GET /giris/masa-<id>` - QR kod giriş noktası
- `GET /customer/masa/<id>` - Menü sayfası
- `POST /customer/masa/<id>/add-to-cart` - Sepete ekleme
- `POST /customer/masa/<id>/checkout` - Sipariş verme

### Yönetim
- `GET /admin/dashboard` - Admin paneli
- `GET /restaurant/dashboard` - Restoran paneli
- `GET /waiter/dashboard` - Ofisiant paneli

## Güvenlik
- Token tabanlı masa koruması
- Session yönetimi
- Rate limiting
- Güvenlik logları
- XSS ve CSRF koruması

## Lisans
MIT License