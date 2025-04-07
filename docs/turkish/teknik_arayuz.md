# WebPush API Teknik Arayüzü

Bu doküman, WebPush bildirim sistemi için kullanıcı arayüzü ve API entegrasyonları hakkında teknik bilgiler içermektedir. Bu bilgiler, sistem wireframe çalışmaları için temel oluşturacaktır.

## 1. Kimlik Doğrulama ve Güvenlik

### 1.1 Kimlik Doğrulama Mekanizması

WebPush API'si, harici bir kimlik doğrulama sisteminden sağlanan JWT (JSON Web Token) temelli bir kimlik doğrulama mekanizması kullanır:

- Her API isteği, HTTP başlığında bir Bearer token içermelidir:
  ```
  Authorization: Bearer [TOKEN]
  ```

- Her istekte müşteri ID (customer_id) belirtilmelidir:
  ```
  X-Customer-ID: [CUSTOMER_ID]
  ```

### 1.2 Yetkilendirme

Yetkilendirme, rol tabanlı erişim kontrolü (RBAC) kullanılarak yapılır:

- Her endpoint için belirli izinler gereklidir
- İzinler rol hiyerarşisinde tanımlanır
- API istekleri, istenen işlemi gerçekleştirmek için gerekli izinlerin varlığına göre doğrulanır

## 2. API Endpoint Kategorileri

API, aşağıdaki ana kategorilerde endpoints sunar:

### 2.1 Abonelik Yönetimi
- `POST /api/v1/subscriptions` - Yeni abonelik oluşturma
- `GET /api/v1/subscriptions` - Abonelikleri listeleme
- `GET /api/v1/subscriptions/{id}` - Belirli bir abonelik detaylarını görüntüleme
- `PUT /api/v1/subscriptions/{id}` - Abonelik güncelleme
- `DELETE /api/v1/subscriptions/{id}` - Abonelik silme

### 2.2 Segment Yönetimi
- `POST /api/v1/segments` - Yeni segment oluşturma
- `GET /api/v1/segments` - Segmentleri listeleme
- `GET /api/v1/segments/{id}` - Segment detaylarını görüntüleme
- `PUT /api/v1/segments/{id}` - Segment güncelleme
- `DELETE /api/v1/segments/{id}` - Segment silme
- `POST /api/v1/segments/{id}/calculate` - Segment büyüklüğünü hesaplama
- `GET /api/v1/segments/{id}/users` - Segment kullanıcılarını listeleme
- `POST /api/v1/segments/import` - Segmente kullanıcı içe aktarma

### 2.3 Şablon Yönetimi
- `POST /api/v1/templates` - Yeni şablon oluşturma
- `GET /api/v1/templates` - Şablonları listeleme
- `GET /api/v1/templates/{id}` - Şablon detaylarını görüntüleme
- `PUT /api/v1/templates/{id}` - Şablon güncelleme
- `DELETE /api/v1/templates/{id}` - Şablon silme
- `POST /api/v1/templates/{id}/preview` - Şablon önizleme
- `POST /api/v1/templates/{id}/versions` - Yeni şablon versiyonu oluşturma
- `GET /api/v1/templates/{id}/versions` - Şablon versiyonlarını listeleme

### 2.4 Kampanya Yönetimi
- `POST /api/v1/campaigns` - Yeni kampanya oluşturma
- `GET /api/v1/campaigns` - Kampanyaları listeleme
- `GET /api/v1/campaigns/{id}` - Kampanya detaylarını görüntüleme
- `PUT /api/v1/campaigns/{id}` - Kampanya güncelleme
- `DELETE /api/v1/campaigns/{id}` - Kampanya silme
- `POST /api/v1/campaigns/{id}/activate` - Kampanyayı etkinleştirme
- `POST /api/v1/campaigns/{id}/pause` - Kampanyayı duraklatma
- `POST /api/v1/campaigns/{id}/resume` - Kampanyayı devam ettirme
- `POST /api/v1/campaigns/{id}/preview` - Kampanya önizleme
- `GET /api/v1/campaigns/{id}/stats` - Kampanya istatistiklerini görüntüleme

### 2.5 Tetikleyici Yönetimi
- `POST /api/v1/triggers` - Yeni tetikleyici oluşturma
- `GET /api/v1/triggers` - Tetikleyicileri listeleme
- `GET /api/v1/triggers/{id}` - Tetikleyici detaylarını görüntüleme
- `PUT /api/v1/triggers/{id}` - Tetikleyici güncelleme
- `DELETE /api/v1/triggers/{id}` - Tetikleyici silme
- `POST /api/v1/triggers/{id}/activate` - Tetikleyiciyi etkinleştirme
- `POST /api/v1/triggers/{id}/deactivate` - Tetikleyiciyi devre dışı bırakma
- `POST /api/v1/events` - Olay tetikleme (harici sistemlerden)

### 2.6 A/B Test Yönetimi
- `POST /api/v1/tests` - Yeni A/B testi oluşturma
- `GET /api/v1/tests` - A/B testlerini listeleme
- `GET /api/v1/tests/{id}` - A/B test detaylarını görüntüleme
- `PUT /api/v1/tests/{id}` - A/B test güncelleme
- `DELETE /api/v1/tests/{id}` - A/B test silme
- `POST /api/v1/tests/{id}/start` - A/B testi başlatma
- `POST /api/v1/tests/{id}/stop` - A/B testi durdurma
- `GET /api/v1/tests/{id}/results` - A/B test sonuçlarını görüntüleme
- `POST /api/v1/tests/{id}/declare-winner` - Kazanan varyantı ilan etme

### 2.7 Analitik ve Raporlama
- `GET /api/v1/analytics/overview` - Genel bakış istatistiklerini alma
- `GET /api/v1/analytics/campaigns` - Kampanya analitiklerini görüntüleme
- `GET /api/v1/analytics/segments` - Segment analitiklerini görüntüleme
- `GET /api/v1/analytics/users` - Kullanıcı analitiklerini görüntüleme
- `GET /api/v1/reports/performance` - Performans raporlarını oluşturma
- `GET /api/v1/reports/engagement` - Etkileşim raporlarını oluşturma
- `GET /api/v1/reports/conversion` - Dönüşüm raporlarını oluşturma
- `POST /api/v1/reports/export` - Rapor dışa aktarma

### 2.8 Webhook Yönetimi
- `POST /api/v1/webhooks` - Yeni webhook oluşturma
- `GET /api/v1/webhooks` - Webhook'ları listeleme
- `GET /api/v1/webhooks/{id}` - Webhook detaylarını görüntüleme
- `PUT /api/v1/webhooks/{id}` - Webhook güncelleme
- `DELETE /api/v1/webhooks/{id}` - Webhook silme
- `POST /api/v1/webhooks/{id}/test` - Webhook'u test etme
- `GET /api/v1/webhooks/{id}/logs` - Webhook loglarını görüntüleme

### 2.9 CDP ve CEP Entegrasyonları
- `POST /api/v1/integrations/cdp/sync` - CDP ile senkronizasyon başlatma
- `GET /api/v1/integrations/cdp/status` - CDP senkronizasyon durumunu görüntüleme
- `POST /api/v1/integrations/cep/optimize` - CEP kanal optimizasyonu talep etme
- `GET /api/v1/integrations/cep/decisions` - CEP kararlarını görüntüleme

## 3. Kullanıcı Arayüzü Gereksinimleri

WebPush yönetim arayüzü aşağıdaki temel bölümleri içermelidir:

### 3.1 Kontrol Paneli
- Genel istatistikler ve performans göstergeleri
- Son kampanya aktiviteleri
- Aktif kampanyaların durumu
- Segment büyüklükleri
- Abonelik trendleri

### 3.2 Abonelik Yönetimi
- Abone olma akışı yapılandırması
- Abone listesi yönetimi
- Abonelik istatistikleri
- Opt-out ve yeniden hedefleme yönetimi

### 3.3 Segment Yönetimi
- Segment oluşturma ve düzenleme arayüzü
- Segment filtre oluşturucu (sürükle-bırak arayüzü)
- Kullanıcı içe aktarma arayüzü
- Segment önizleme ve test etme

### 3.4 Şablon Yönetimi
- Görsel şablon düzenleyici
- Dinamik değişken tanımlama
- Çoklu cihaz önizleme
- Şablon versiyonlama
- Şablon kategorileri ve etiketleme

### 3.5 Kampanya Yönetimi
- Kampanya oluşturma sihirbazı
- Zamanlama arayüzü (takvim görünümü)
- Tekrarlanan kampanya yapılandırması
- Kampanya performans izleme
- A/B test yapılandırması

### 3.6 Tetikleyici Yönetimi
- Tetikleyici oluşturma arayüzü
- Olay ve koşul tanımlama
- Gecikme ayarlama
- Tetikleyici izleme ve performans

### 3.7 Analitik ve Raporlama
- İnteraktif analitik panoları
- Özelleştirilebilir raporlar
- Veri görselleştirme grafikleri
- Rapor zamanlama ve paylaşma

### 3.8 Sistem Yapılandırması
- Webhook yapılandırması
- CDP entegrasyon ayarları
- CEP entegrasyon ayarları
- Kullanıcı ve rol yönetimi
- Sistem log izleme

## 4. Mobil Uyumluluk

Yönetim arayüzü, aşağıdaki cihaz türleri için duyarlı tasarıma sahip olmalıdır:

- Masaüstü (1200px ve üzeri)
- Dizüstü (992px - 1199px)
- Tablet (768px - 991px)
- Mobil (767px ve altı)

Kritik işlevler mobil cihazlarda da tam olarak çalışmalıdır.

## 5. Tarayıcı Uyumluluğu

Sistem aşağıdaki tarayıcıların en son iki ana sürümünü desteklemelidir:

- Google Chrome
- Mozilla Firefox
- Safari
- Microsoft Edge

WebPush bildirimleri için tarayıcı desteği özellikle kontrol edilmelidir.

## 6. Erişilebilirlik Gereksinimleri

Arayüz, WCAG 2.1 AA seviyesi erişilebilirlik standartlarını karşılamalıdır:

- Uygun renk kontrastı
- Klavye navigasyonu
- Ekran okuyucu uyumluluğu
- Alt metinler ve açıklamalar

## 7. Wireframe Kapsamı

Wireframe çalışması aşağıdaki ekranları içermelidir:

1. Kullanıcı abonelik akışı (son kullanıcı tarafı)
2. Dashboard / Kontrol paneli
3. Segment oluşturma ve düzenleme
4. Şablon oluşturma ve düzenleme
5. Kampanya oluşturma sihirbazı
6. Tetikleyici yapılandırma
7. A/B test kurulumu
8. Analitik panelleri
9. Webhook yapılandırması
10. Sistem ayarları

Her ekran için mobil ve masaüstü versiyonlar hazırlanmalıdır.

---

Bu teknik arayüz dokümanı, wireframe çalışmaları için gerekli API yapısını ve kullanıcı arayüzü gereksinimlerini içermektedir. Grafik tasarımcı, bu dokümanı kullanarak sistemin temel işlevselliğini yansıtan wireframe'ler oluşturabilir.
