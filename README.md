# AITruthGuard Project

## 1. Projenin Amacı

Bu proje, yapay zeka destekli bir "Gerçeklik Koruyucusu" (Truth Guard) geliştirmeyi amaçlamaktadır. Temel olarak, kullanıcılardan gelen soruları veya iddiaları analiz ederek, mevcut bilgi tabanına (veri setine) dayanarak bu iddiaların doğruluğunu değerlendirir ve ilgili bilgileri sunar. Proje, yanlış bilginin yayılmasını engellemeye ve kullanıcılara güvenilir bilgi sağlamaya odaklanmaktadır.

## 2. Veri Seti Hakkında Bilgi

Proje, haber makalelerinden oluşan bir veri seti kullanmaktadır. Bu veri seti, hem gerçek (True) hem de sahte (Fake) haber örneklerini içermektedir. Veri setinin içeriği, doğal dil işleme (NLP) modellerinin eğitilmesi ve iddiaların doğruluğunu sınıflandırmak için kullanılmaktadır.

*   **Veri Seti İçeriği:** Haber başlıkları, metinleri ve ilgili etiketler (gerçek/sahte).
*   **Proje Konusu:** Yanlış bilgi tespiti ve doğrulama.

## 3. Kullanılan Yöntemler

Bu projede, Geri Çağırma Artırılmış Üretim (Retrieval-Augmented Generation - RAG) mimarisi kullanılmıştır. Bu mimari, bir dil modelinin (örneğin Gemini) harici bir bilgi tabanından (veri setimiz) ilgili bilgileri alarak daha doğru ve bağlamsal olarak uygun yanıtlar üretmesini sağlar.

*   **Gömme (Embedding):** `sentence-transformers` kütüphanesi kullanılarak metinlerin vektör temsilleri (embedding'ler) oluşturulmuştur.
*   **Vektör Veritabanı:** FAISS (Facebook AI Similarity Search) kullanılarak oluşturulan embedding'ler hızlı arama ve benzerlik karşılaştırmaları için indekslenmiştir.
*   **Dil Modeli:** Google'ın Gemini API'si kullanılarak kullanıcı sorgularına yanıtlar üretilmiştir.

## 4. Elde Edilen Sonuçlar

(Bu bölüm, projenin geliştirme aşamasında elde edilen spesifik sonuçları, model performans metriklerini, doğruluk oranlarını vb. içerecektir. Şu an için genel bir özet sunulmuştur.)

Proje, haber metinlerinin doğruluğunu yüksek bir başarı oranıyla sınıflandırma ve kullanıcı sorgularına ilgili ve doğru bilgilerle yanıt verme potansiyeli göstermektedir. RAG mimarisi sayesinde, modelin güncel ve spesifik bilgilere erişimi artırılmıştır.

## 5. Kodunuzun Çalışma Kılavuzu

Projenin yerel ortamda çalıştırılması için aşağıdaki adımları takip ediniz:

1.  **Python Sanal Ortamı Oluşturma:**
    ```bash
    python -m venv .venv
    ```
2.  **Sanal Ortamı Aktifleştirme:**
    *   Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
3.  **Gerekli Kütüphaneleri Yükleme:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **API Anahtarlarını Ayarlama:**
    Projenin kök dizininde `.env` adında bir dosya oluşturun ve Google Gemini API anahtarınızı aşağıdaki formatta ekleyin:
    ```
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```
    Ayrıca, eğer kullanılıyorsa, haber API anahtarınızı da ekleyin:
    ```
    NEWS_API_KEY=YOUR_NEWS_API_KEY
    ```
5.  **Backend Sunucusunu Çalıştırma:**
    ```bash
    uvicorn backend.server:app --host 0.0.0.0 --port 8000
    ```
    Bu komut, FastAPI backend sunucusunu başlatacaktır.

## 6. Çözüm Mimariniz

Proje, aşağıdaki temel bileşenlerden oluşan bir RAG (Retrieval-Augmented Generation) mimarisi kullanır:

*   **Veri Yükleyici (Data Loader):** Haber veri setini (gerçek ve sahte haberler) yükler ve işler.
*   **Gömücü (Embedder):** `sentence-transformers` kullanarak haber metinlerini ve kullanıcı sorgularını vektör uzayında temsil eden embedding'lere dönüştürür.
*   **İndeks Yöneticisi (Index Manager):** Oluşturulan embedding'leri FAISS indeksinde saklar ve hızlıca benzer metinleri bulmak için kullanılır.
*   **RAG Chatbot:** Kullanıcı sorgusunu alır, ilgili haberleri FAISS indeksinden çeker ve bu bağlamı Google Gemini dil modeline ileterek yanıt üretir.
*   **FastAPI Backend:** Frontend ile iletişim kuran ve RAG chatbot işlevselliğini sunan RESTful API endpoint'leri sağlar.
*   **Frontend:** Kullanıcı arayüzünü sağlar ve backend ile etkileşim kurar.

## 7. Web Arayüzü & Product Kılavuzu

**Deploy Linki:** [https://damlalper.github.io/AITruthGuard/](https://damlalper.github.io/AITruthGuard/)

**Çalışma Akışı ve Test:**

1.  Yukarıdaki deploy linkine tıklayarak web arayüzüne erişin.
2.  Arayüzde bir metin giriş alanı ve bir "Sor" veya "Doğrula" butonu bulunacaktır.
3.  Metin giriş alanına doğrulamak istediğiniz bir iddiayı veya sormak istediğiniz bir soruyu yazın.
4.  Butona tıklayın.
5.  Backend, sorgunuzu işleyecek, ilgili haberleri bulacak ve Gemini modelini kullanarak bir yanıt üretecektir.
6.  Yanıt, arayüzde size sunulacaktır. Bu yanıt, iddia hakkında bilgi, güven düzeyi ve ilgili haber kaynaklarını içerebilir.

(Ekran görüntüleri/video anlatım buraya eklenebilir.)
