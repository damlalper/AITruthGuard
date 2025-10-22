# Haber Doğrulama Chatbot'u (Akbank GenAI Bootcamp)

## 1. Proje Amacı
Retrieval Augmented Generation (RAG) mimarisi kullanılarak, kullanıcıların sunduğu haber metninin **doğru**, **yalan** veya **yanıltıcı** olup olmadığını tespit eden ve kararını **güncel, güvenilir kanıtlarla destekleyen** bir sohbet botu geliştirmek.

Sistem, hem **statik veri setlerinden (Kaggle)** hem de **dinamik kaynaklardan (News API)** faydalanarak güncel doğrulama yapacaktır.

---

## 2. Hedefler
- RAG mimarisiyle doğrulama sürecinde güncel bilgi entegrasyonu sağlamak.
- Halüsinasyon oranı düşük, açıklamalı sonuçlar üreten bir chatbot oluşturmak.
- Sonuçları web tabanlı bir arayüzde kullanıcıya görsel ve metinsel olarak sunmak.

---

## 3. Kullanıcı Akışı
1. Kullanıcı, doğrulamak istediği haber metnini girer.
2. (Opsiyonel) Haber kaynağı URL’si ve tarihi ekler.
3. “Doğrula” butonuna basar.
4. Backend, RAG pipeline’ını çalıştırır:
   - Haber iddialarını çıkarır (LLM).
   - Vector DB’de benzer haberleri ve kanıtları arar.
   - News API’den güncel haberleri çeker.
   - LLM, kanıtları değerlendirip sonucu üretir.
5. UI, sonucu şu şekilde gösterir:
   - **Sonuç**: Gerçek / Yalan / Yanıltıcı
   - **Açıklama**: LLM gerekçesi
   - **Kaynaklar**: URL + alıntı metin

---

## 4. Mimarinin Genel Görünümü
| Katman | Teknoloji | Açıklama |
|--------|------------|----------|
| RAG Framework | LangChain / Haystack | Retrieval + Generation süreci |
| LLM | Gemini API | Son karar üretimi ve açıklama |
| Embedding | Google text-embedding-004 / Cohere | Vektörleştirme |
| Vektör DB | Chroma / FAISS | Kanıtların hızlı aranması |
| Backend | FastAPI / Flask | API uçları |
| Frontend | React | Web UI |
| API Kaynakları | News API, PolitiFact, Snopes | Gerçek zamanlı kanıt toplama |

---

## 5. Başarı Kriterleri
- RAG pipeline’ın doğru şekilde haberleri doğrulaması
- API entegrasyonlarının hatasız çalışması
- UI’nin kullanıcı dostu ve açıklayıcı olması
- En az bir örnek senaryonun (yalan ve gerçek haber) test edilmesi

---

## 6. Teslimatlar
- GitHub reposu (README.md, kodlar, notebook)
- requirements.txt
- deploy.md (çalıştırma ve yayınlama rehberi)
- React tabanlı web arayüzü
- Video veya ekran görüntüsü ile demo