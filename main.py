"""
Interactive CLI version for HPC Air Quality & Parallel Benchmark.
Connects academic theory with practical execution in the terminal.
"""

import os
import sys
import time
import pandas as pd
import hpc_engine

def print_banner():
    print("=" * 70)
    print("⚡ HPC AIR QUALITY DISPERSION & PARALLEL COMPUTING BENCHMARK")
    print("   Studi Kasus Kuliah Tamu Informatika: Dr. Worawan Diaz Carballo")
    print("   Topik: Global Infrastructure to Address Local Challenge with HPC")
    print("=" * 70)

def run_simulation_cli():
    print("\n--- [1] SIMULASI DISPERSI POLUSI UDARA PM2.5 ---")
    try:
        grid_input = input("Masukkan ukuran grid N (misal 150 untuk 150x150) [default: 150]: ").strip()
        grid_size = int(grid_input) if grid_input else 150
        
        sim = hpc_engine.HPCAirQualitySimulator(grid_size=grid_size)
        
        print(f"\n[*] Menjalankan komputasi SERIAL (1 Core CPU)...")
        res_serial = sim.run_serial()
        print(f"    ✓ Waktu Eksekusi : {res_serial['elapsed_sec']:.4f} detik ({res_serial['gflops']:.3f} GFLOPS)")
        
        max_cores = os.cpu_count() or 4
        print(f"\n[*] Menjalankan komputasi PARALEL ({max_cores} Cores CPU)...")
        res_parallel = sim.run_parallel(num_workers=max_cores)
        print(f"    ✓ Waktu Eksekusi : {res_parallel['elapsed_sec']:.4f} detik ({res_parallel['gflops']:.3f} GFLOPS)")
        
        speedup = res_serial['elapsed_sec'] / res_parallel['elapsed_sec'] if res_parallel['elapsed_sec'] > 0 else 1.0
        efficiency = (speedup / max_cores) * 100.0
        
        print("\n" + "-" * 50)
        print("📊 HASIL PERBANDINGAN PERFORMA HPC:")
        print(f"• Percepatan (Speedup) : {speedup:.2f}x lebih cepat")
        print(f"• Efisiensi Paralel   : {efficiency:.1f}%")
        print("-" * 50)
        
        impact = hpc_engine.evaluate_air_quality_impact(res_parallel['grid'])
        print(f"\n🎯 KEPUTUSAN KESEHATAN PUBLIK (PERAN INTEGRATOR):")
        print(f"• Status Kualitas Udara : [{impact['status']}]")
        print(f"• Puncak Polutan PM2.5 : {impact['max_pm25']} µg/m³")
        print("• Rekomendasi Tindakan :")
        for i, act in enumerate(impact['actions'], 1):
            print(f"  {i}. {act}")
            
    except Exception as e:
        print(f"[!] Terjadi kesalahan: {e}")

def run_benchmark_cli():
    print("\n--- [2] FULL MULTI-CORE SCALING BENCHMARK ---")
    try:
        grid_size = 200
        sim = hpc_engine.HPCAirQualitySimulator(grid_size=grid_size)
        print(f"[*] Melakukan stress-test komputasi di grid {grid_size}x{grid_size}...")
        
        df_bench, _ = sim.run_benchmark_suite()
        
        print("\n" + "=" * 70)
        print("📊 TABEL HASIL BENCHMARK PARALEL (PANDAS DATAFRAME):")
        print("=" * 70)
        print(df_bench.to_string(index=False))
        print("=" * 70)
        
    except Exception as e:
        print(f"[!] Terjadi kesalahan: {e}")

def show_integrator_info():
    print("\n" + "=" * 70)
    print("🌐 RINGKASAN KONSEP 'THE INTEGRATOR' (WORAWAN DIAZ CARBALLO)")
    print("=" * 70)
    print("""
1. Definisi Integrator:
   Penghubung antara pemangku kepentingan masalah lokal (cuaca, banjir,
   kesehatan, pertanian) dengan kapabilitas infrastruktur superkomputer global.

2. Skala Komputasi (FLOPS):
   • GigaFLOPS (10⁹)  : Laptop dan perangkat mobile
   • TeraFLOPS (10¹²) : Workstation & GPU AI (NVIDIA RTX)
   • PetaFLOPS (10¹⁵) : Superkomputer (LANTA - Thailand)
   • ExaFLOPS (10¹⁸)  : Exascale Supercomputer (El Capitan / Frontier)

3. Keterampilan yang Harus Dikuasai:
   Linux & SSH, Parallel Computing (MPI/OpenMP), Multiprocessing Python,
   GPU Programming (CUDA), Manajemen Data (Pandas), dan Version Control (Git).
    """)
    print("=" * 70)

def main():
    while True:
        print_banner()
        print(" [1] Jalankan Simulasi Dispersi PM2.5 (Serial vs Paralel)")
        print(" [2] Jalankan Full Multi-Core Scaling Benchmark")
        print(" [3] Pelajari Konsep 'The Integrator' & Info HPC")
        print(" [0] Keluar")
        print("=" * 70)
        
        choice = input("Pilih menu (0-3): ").strip()
        if choice == '1':
            run_simulation_cli()
        elif choice == '2':
            run_benchmark_cli()
        elif choice == '3':
            show_integrator_info()
        elif choice == '0':
            print("\nTerima kasih! Sampai jumpa.\n")
            break
        else:
            print("[!] Pilihan tidak valid, coba lagi.")
        
        input("\nTekan Enter untuk melanjutkan...")

if __name__ == '__main__':
    main()
