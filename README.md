# 🐶 Sistem Pakar Diagnosa Penyakit Kulit Anjing  
**Metode Forward Chaining dan Certainty Factor**

## 📌 Deskripsi Proyek
Proyek ini merupakan implementasi **sistem pakar** yang bertujuan untuk membantu proses **diagnosa penyakit kulit pada anjing** berdasarkan gejala yang dialami. Sistem bekerja dengan menirukan cara berpikir pakar menggunakan **metode forward chaining** sebagai mesin inferensi dan **Certainty Factor (CF)** untuk menangani ketidakpastian dalam proses diagnosis.

Sistem akan menanyakan gejala kepada pengguna, kemudian menghitung tingkat keyakinan terhadap masing-masing penyakit dan menampilkan hasil diagnosis beserta nilai CF dan solusi penanganannya.

---

## 🎯 Tujuan
- Membantu pengguna (pemilik anjing) dalam mengetahui kemungkinan penyakit kulit yang dialami anjing.
- Mengimplementasikan metode **Forward Chaining** dan **Certainty Factor** dalam sistem pakar.
- Menyajikan hasil diagnosis beserta tingkat keyakinannya secara transparan.

---

## 🧠 Metode yang Digunakan
- **Forward Chaining**  
  Digunakan sebagai mesin inferensi yang melakukan penalaran dari gejala menuju kesimpulan penyakit.
  
- **Certainty Factor (CF)**  
  Digunakan untuk menghitung tingkat keyakinan diagnosis berdasarkan bobot gejala dari pakar dan jawaban pengguna.

---

## 🛠️ Tools & Teknologi
- **Bahasa Pemrograman** : Python  
- **Basis Pengetahuan** : Neo4j (Graph Database)  
- **Mesin Inferensi** : Forward Chaining  
- **Antarmuka Pengguna** : Streamlit  
- **Database Query** : Cypher Query Language  

---