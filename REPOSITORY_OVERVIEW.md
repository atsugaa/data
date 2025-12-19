# Repository Overview - Data Putusan Pengadilan Negeri

## 📋 Deskripsi Repositori

Repositori ini berisi data putusan pengadilan negeri dari berbagai wilayah di Jawa Timur, Indonesia. Data tersimpan dalam format JSON dan file teks yang berisi informasi lengkap mengenai kasus-kasus hukum pidana.

## 📁 Struktur Repositori

### File Utama:
- **README.md** - File dokumentasi utama
- **extract.json** - File JSON berisi data ekstraksi putusan pengadilan (2,657 baris)
- **test.json** - File JSON template untuk format data (101 baris)
- **list.txt** - Daftar file putusan (43 baris)
- **desktop.ini** - File konfigurasi sistem

### Direktori Data (30 Pengadilan):

Repositori ini mengandung data dari **30 Pengadilan Negeri** di Jawa Timur:

1. pn-bangkalan
2. pn-banyuwangi
3. pn-blitar
4. pn-bojonegoro
5. pn-bondowoso
6. pn-gresik
7. pn-jember
8. pn-jombang
9. pn-kediri
10. pn-kepanjen
11. pn-lamongan
12. pn-lumajang
13. pn-madiun
14. pn-magetan
15. pn-malang
16. pn-nganjuk
17. pn-ngawi
18. pn-pacitan
19. pn-pamekasan
20. pn-pasuruan
21. pn-ponorogo
22. pn-probolinggo
23. pn-sampang
24. pn-sidoarjo
25. pn-situbondo
26. pn-sumenep
27. pn-surabaya
28. pn-trenggalek
29. pn-tuban
30. pn-tulungagung

## 📊 Statistik Data

- **Total Direktori**: 120
- **Total File**: 10,951
- **Format Data**: JSON dan TXT
- **Subdirektori per PN**: 
  - `/pdf` - Dokumen PDF putusan
  - `/txt` - File teks putusan

## 📝 Format Data JSON

Setiap entri putusan dalam `extract.json` berisi informasi:

### Informasi Perkara:
- Nomor perkara
- Tanggal putusan
- Lokasi pengadilan

### Data Terdakwa:
- Identitas lengkap (nama, umur, tempat/tanggal lahir)
- Jenis kelamin, kebangsaan, agama, pekerjaan
- Alamat lengkap (kelurahan, kecamatan, kabupaten, kota)
- Tuntutan pidana (pasal, jenis peraturan, tindak pidana)
- Tuntutan hukuman
- Putusan pidana
- Putusan hukuman

### Pejabat Pengadilan:
- Hakim (ketua dan anggota)
- Panitera
- Penuntut umum
- Penasehat hukum (jika ada)

### Metadata:
- Nama file sumber
- URL (jika tersedia)

## 🔍 Contoh Data

Repositori ini mencakup berbagai jenis kasus pidana:
- **Pencurian** (Pasal 362, 363 KUHP)
- **Perjudian** (Pasal 303, 303 bis KUHP)
- **Penipuan** (Pasal 378 KUHP)
- **Penggelapan** (Pasal 372 KUHP)
- **Penganiayaan** (Pasal 351 KUHP)
- **Kekerasan** (Pasal 170 KUHP)
- **Penadahan** (Pasal 480 KUHP)
- **Peredaran Sediaan Farmasi Ilegal** (Pasal 196, 197 UU No.36/2009, Pasal 435 UU No.17/2023)
- **Kecelakaan Lalu Lintas** (Pasal 310 UU No.22/2009)
- **Tindak Pidana Kekerasan Seksual** (Pasal 81, 82 UU Perlindungan Anak, Pasal 6 UU 12/2022 TPKS)

## 🎯 Tujuan Repositori

Repositori ini dapat digunakan untuk:
- Penelitian hukum dan kriminologi
- Analisis data putusan pengadilan
- Machine learning dan NLP untuk sistem hukum
- Studi kasus hukum pidana
- Transparansi data peradilan

## 📄 Lisensi dan Catatan

Data dalam repositori ini merupakan data publik dari sistem peradilan Indonesia. Penggunaan data ini harus mematuhi regulasi privasi dan perlindungan data yang berlaku.

---

**Last Updated**: 19 Desember 2025
**Repository**: atsugaa/data
