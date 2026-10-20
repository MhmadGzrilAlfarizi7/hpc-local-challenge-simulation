# ⚡ HPC Air Quality Dispersion & Parallel Computing Benchmark

> **Implementasi Studi Kasus Kuliah Tamu Praktisi Informatika Seri 2**  
> **Tema:** *Global Infrastructure to Address Local Challenge with HPC*  
> **Narasumber:** Dr. Worawan Diaz Carballo – *Thammasat University*  
> **Konsep Kunci:** $\text{Domain Problem} + \text{Computational Logic} + \text{HPC Infrastructure} \implies \text{Real Societal Impact}$

---

## 🌟 1. Latar Belakang & Filosofi "The Integrator"

Di dunia modern, tantangan riil masyarakat lokal (seperti bencana kabut asap PM2.5 lintas negara, banjir bandang, hingga penyebaran wabah patogen baru) melibatkan pemodelan data berukuran raksasa. Komputer laptop biasa membutuhkan waktu berminggu-minggu untuk menyelesaikannya, padahal keputusan evakuasi dan mitigasi publik membutuhkan kepastian dalam hitungan jam.

Sesuai materi narasumber **Dr. Worawan Diaz Carballo**, mahasiswa Informatika memiliki peran vital sebagai **"The Integrator"** — penghubung antara domain masalah spesifik dengan infrastruktur superkomputer global. Proyek ini mendemonstrasikan secara langsung bagaimana pemodelan atmosfer dispersi partikel polusi PM2.5 (mengadopsi implementasi nyata **Superkomputer LANTA di Thailand**) diakselerasi menggunakan teknik komputasi paralel *multi-core domain-decomposition*.

---

## 🔬 2. Konsep Komputasi & Metrik HPC

1. **Floating Point Operations Per Second (FLOPS):**
   * Mengukur kapasitas komputasi riil mesin dalam mengeksekusi operasi matematika presisi (penjumlahan, perkalian, eksponensial, pembagian fluida).
2. **Speedup Factor ($S$):**
   $$S = \frac{T_{\text{serial}}}{T_{\text{paralel}}}$$
3. **Efisiensi Paralel ($E$):**
   $$E = \frac{S}{N_{\text{cores}}} \times 100\%$$
4. **Hukum Amdahl (Amdahl's Law):**
   Memprediksi batas maksimum percepatan teoritis ketika sebagian beban program bersifat serial dan sebagian dapat diparalelkan:
   $$S_{\text{teoritis}} = \frac{1}{(1 - P) + \frac{P}{N_{\text{cores}}}}$$

---

## 📁 3. Struktur Direktori Proyek

```text
hpc-local-challenge-simulation/
├── hpc_engine.py       # Engine inti: Persamaan dispersi atmosfer 2D, Pool multiprocessing, & FLOPS counter
├── app.py              # Web Dashboard Interaktif (Bespoke Dark Theme CSS/JS & Plotly Contour Heatmap)
├── main.py             # Aplikasi CLI Terminal Interaktif
├── requirements.txt    # Dependensi pustaka Python
├── .gitignore          # Konfigurasi proteksi repositori Git
└── README.md           # Dokumentasi lengkap sistem
```

---

## 🛠️ 4. Spesifikasi Teknologi

- **Bahasa Pemrograman:** Python 3.8+
- **Komputasi Paralel:** `concurrent.futures.ProcessPoolExecutor` / `multiprocessing`
- **Manipulasi & Tabulasi Data:** `pandas`, `numpy`
- **Visualisasi Interaktif:** `plotly`, `streamlit`
- **Telemetri Sistem:** `psutil`

---

## 🚀 5. Cara Instalasi & Menjalankan Program

### Langkah 1: Masuk ke Direktori Proyek
```powershell
cd "C:\Users\user\Documents\.gemini\antigravity\scratch\hpc-local-challenge-simulation"
```

### Langkah 2: Buat & Aktifkan Virtual Environment (Rekomendasi)
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```
*(Atau menggunakan `uv` jika terpasang: `uv venv; .\.venv\Scripts\activate`)*

### Langkah 3: Install Dependensi
```powershell
pip install -r requirements.txt
```
*(Atau jika menggunakan `uv`: `uv pip install -r requirements.txt`)*

---

### Pilihan Menjalankan:

#### 🌐 Opsi A: Web Dashboard Interaktif (Rekomendasi untuk Portofolio)
```powershell
streamlit run app.py
```
*Aplikasi akan otomatis terbuka di browser pada alamat `http://localhost:8501`.*

#### 💻 Opsi B: Versi Terminal Interaktif (CLI)
```powershell
python main.py
```

---

## 📊 6. Fitur Unggulan Dashboard

1. **Simulasi Dispersi Spasial PM2.5 Real-Time:** Menghitung jutaan titik grid dan memvisualisasikan peta konsentrasi polutan dengan *interactive contour heatmap* (Plotly).
2. **Benchmark CPU Multi-Core Scaling:** Membandingkan kinerja Single-Core vs Multi-Core secara langsung di komputer pengguna lengkap dengan grafik Amdahl's Law.
3. **Penerjemahan Kebijakan Publik (Integrator Engine):** Mengubah nilai konsentrasi polutan menjadi rekomendasi operasional bagi instansi kesehatan dan lingkungan hidup.
4. **Knowledge Base Skala FLOPS:** Memetakan tingkatan komputasi dari GigaFLOPS (laptop) hingga ExaFLOPS (superkomputer Frontier/El Capitan).
