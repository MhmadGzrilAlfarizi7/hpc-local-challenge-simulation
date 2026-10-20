"""
HPC Core Engine: Physics-based Atmospheric PM2.5 Dispersion & Parallel Computing Benchmark.
Inspired by Thailand's LANTA Supercomputer & Dr. Worawan Diaz Carballo's lecture:
'Global Infrastructure to Address Local Challenge with HPC'.
"""

import time
import os
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Top-level worker function for parallel chunk computing
def _compute_grid_chunk(args):
    """
    Simulates a chunk of spatial rows in a 2D atmospheric diffusion-advection equation
    across a temporal horizon (e.g. 24 forecast hours), modeling turbulent diffusion.
    Returns: (row_start, chunk_result, num_operations)
    """
    row_start, row_end, n_cols, sources, wind_u, wind_v, diff_coeff, timesteps = args
    
    # Grid coordinates for this chunk
    y = np.linspace(0, 100, row_end - row_start) + (row_start / (row_end - row_start + 1e-9))
    x = np.linspace(0, 100, n_cols)
    XX, YY = np.meshgrid(x, y)
    
    # Initialize PM2.5 concentration matrix for this chunk
    chunk_grid = np.zeros_like(XX, dtype=np.float64)
    total_flops = 0
    
    # Time-stepping atmospheric evolution loop (Forecast horizon)
    for t in range(timesteps):
        t_factor = 1.0 + 0.05 * np.sin(t * 0.25)
        w_u = wind_u * t_factor
        w_v = wind_v * t_factor
        w_speed = np.sqrt(w_u**2 + w_v**2) + 0.1
        
        for src in sources:
            sx, sy, q_rate, h_stack = src['x'], src['y'], src['strength'], src.get('stack_height', 10.0)
            
            dx = XX - sx
            dy = YY - sy
            
            downwind = (dx * w_u + dy * w_v) / w_speed
            crosswind = (-dx * w_v + dy * w_u) / w_speed
            
            sigma_y = np.maximum(diff_coeff * np.abs(downwind)**0.85, 2.0)
            sigma_z = np.maximum(diff_coeff * 0.6 * np.abs(downwind)**0.80, 2.0)
            
            exp_y = np.exp(-0.5 * (crosswind / sigma_y)**2)
            exp_z = np.exp(-0.5 * (h_stack / sigma_z)**2)
            
            upwind_mask = downwind >= -5.0
            concentration = (q_rate / (2 * np.pi * w_speed * sigma_y * sigma_z)) * exp_y * exp_z
            concentration = np.where(upwind_mask, concentration, concentration * 0.05)
            
            chunk_grid += (concentration / timesteps)
            total_flops += chunk_grid.size * 48

    return row_start, chunk_grid, total_flops


class HPCAirQualitySimulator:
    """
    High Performance Computing Simulation Engine for PM2.5 prediction and parallel benchmarking.
    """
    def __init__(self, grid_size=200, wind_speed=15.0, wind_angle_deg=45.0, diff_coeff=0.55, timesteps=16):
        self.grid_size = grid_size
        self.wind_speed = wind_speed
        self.wind_angle = np.radians(wind_angle_deg)
        self.wind_u = wind_speed * np.cos(self.wind_angle)
        self.wind_v = wind_speed * np.sin(self.wind_angle)
        self.diff_coeff = diff_coeff
        self.timesteps = timesteps
        self.cpu_count = os.cpu_count() or 4
        
        # Default realistic emission hot-spots (Industri, PLTU, Titik Karhutla, Transportasi)
        self.sources = [
            {'name': 'Kawasan Industri Utama', 'x': 30, 'y': 35, 'strength': 5500.0, 'type': 'industry'},
            {'name': 'Pusat PLTU Batubara', 'x': 75, 'y': 80, 'strength': 7200.0, 'type': 'powerplant'},
            {'name': 'Titik Karhutla / Biomass', 'x': 20, 'y': 70, 'strength': 6000.0, 'type': 'wildfire'},
            {'name': 'Koridor Transportasi Urban', 'x': 60, 'y': 45, 'strength': 3800.0, 'type': 'traffic'}
        ]

    def add_source(self, name, x, y, strength, source_type='industry'):
        self.sources.append({'name': name, 'x': x, 'y': y, 'strength': strength, 'type': source_type})

    def run_serial(self):
        """
        Runs the simulation using a Single Core CPU (Serial execution).
        """
        start_time = time.perf_counter()
        
        args = (0, self.grid_size, self.grid_size, self.sources, self.wind_u, self.wind_v, self.diff_coeff, self.timesteps)
        _, grid_result, total_flops = _compute_grid_chunk(args)
        
        elapsed_sec = time.perf_counter() - start_time
        gflops = (total_flops / 1e9) / elapsed_sec if elapsed_sec > 0 else 0
        
        return {
            'mode': 'Serial (1 Core CPU)',
            'cores': 1,
            'elapsed_sec': elapsed_sec,
            'gflops': gflops,
            'total_flops': total_flops,
            'grid': grid_result
        }

    def run_parallel(self, num_workers=None):
        """
        Runs the simulation using Multi-Core Parallel Computing (HPC Worker Pool).
        Divides spatial 2D matrix into domain-decomposed slices.
        """
        if num_workers is None:
            num_workers = self.cpu_count
            
        start_time = time.perf_counter()
        
        # Domain decomposition (Bagi grid matriks ke sejumlah core)
        rows_per_worker = self.grid_size // num_workers
        chunk_args = []
        for i in range(num_workers):
            r_start = i * rows_per_worker
            r_end = self.grid_size if i == num_workers - 1 else (i + 1) * rows_per_worker
            chunk_args.append((r_start, r_end, self.grid_size, self.sources, self.wind_u, self.wind_v, self.diff_coeff, self.timesteps))
            
        # Parallel execution across worker pool
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = list(executor.map(_compute_grid_chunk, chunk_args))
            
        # Reconstruct full 2D spatial grid from chunk results
        results.sort(key=lambda x: x[0])
        full_grid = np.vstack([res[1] for res in results])
        total_flops = sum(res[2] for res in results)
        
        elapsed_sec = time.perf_counter() - start_time
        gflops = (total_flops / 1e9) / elapsed_sec if elapsed_sec > 0 else 0
        
        return {
            'mode': f'Parallel ({num_workers} Cores CPU)',
            'cores': num_workers,
            'elapsed_sec': elapsed_sec,
            'gflops': gflops,
            'total_flops': total_flops,
            'grid': full_grid
        }

    def run_benchmark_suite(self, core_list=None):
        """
        Executes a comprehensive HPC benchmark comparing Serial vs Multi-Core Scaling.
        Returns a Pandas DataFrame formatted for analytics and visualization.
        """
        if core_list is None:
            max_c = self.cpu_count
            core_list = [1]
            if 2 <= max_c: core_list.append(2)
            if 4 <= max_c: core_list.append(4)
            if max_c not in core_list: core_list.append(max_c)
            
        results = []
        t_serial = None
        
        for cores in core_list:
            if cores == 1:
                res = self.run_serial()
                t_serial = res['elapsed_sec']
                speedup = 1.0
                efficiency = 100.0
            else:
                res = self.run_parallel(num_workers=cores)
                speedup = t_serial / res['elapsed_sec'] if res['elapsed_sec'] > 0 else 1.0
                efficiency = (speedup / cores) * 100.0
                
            # Amdahl's Law theoretical limit assuming 90% parallelizable workload (P = 0.90)
            P = 0.90
            amdahl_theoretical_speedup = 1.0 / ((1.0 - P) + (P / cores))
            
            results.append({
                'Cores': cores,
                'Mode': f"{cores} Core{'s' if cores > 1 else ''}",
                'Execution Time (s)': round(res['elapsed_sec'], 4),
                'Speedup (x)': round(speedup, 2),
                'Theoretical Speedup (Amdahl)': round(amdahl_theoretical_speedup, 2),
                'Parallel Efficiency (%)': round(efficiency, 1),
                'Compute Throughput (GFLOPS)': round(res['gflops'], 3),
                'Total Operations (MFLOP)': round(res['total_flops'] / 1e6, 2)
            })
            
        df_benchmark = pd.DataFrame(results)
        return df_benchmark, res['grid']


def evaluate_air_quality_impact(grid_matrix):
    """
    Translates computational concentration values into WHO & Indonesia Air Quality Standards (ISPU).
    Part of the 'Integrator' role: converting raw simulation data into actionable public policy.
    """
    max_pm25 = float(np.max(grid_matrix))
    mean_pm25 = float(np.mean(grid_matrix))
    p90_pm25 = float(np.percentile(grid_matrix, 90))
    
    # Categorization based on PM2.5 ug/m3
    if max_pm25 > 250:
        status = "BERBAHAYA (HAZARDOUS)"
        color = "#e53e3e"
        badge_class = "badge-danger"
        action = [
            "Rekomendasikan peringatan dini darurat kabut asap kepada pemda setempat.",
            "Wajibkan penutupan sementara aktivitas industri non-esensial dalam radius 30 km.",
            "Instruksikan belajar daring untuk sekolah dan imbauan WFH bagi pekerja rentan.",
            "Bagikan masker respirator N95 kepada kelompok rentan (anak-anak & lansia)."
        ]
    elif max_pm25 > 150:
        status = "SANGAT TIDAK SEHAT (VERY UNHEALTHY)"
        color = "#dd6b20"
        badge_class = "badge-warning"
        action = [
            "Batasi jam operasional PLTU dan kawasan industri sebesar 40%.",
            "Imbau masyarakat umum menghindari aktivitas fisik berat di luar ruangan.",
            "Aktifkan armada water-cannon spray untuk menekan partikel debu jalanan."
        ]
    elif max_pm25 > 55:
        status = "TIDAK SEHAT (UNHEALTHY)"
        color = "#d69e2e"
        badge_class = "badge-alert"
        action = [
            "Berikan peringatan kualitas udara waspada bagi penderita asma/ISPA.",
            "Perketat razia uji emisi kendaraan bermotor di koridor utama kota."
        ]
    else:
        status = "SEDANG / AMAN (MODERATE / GOOD)"
        color = "#38a169"
        badge_class = "badge-success"
        action = [
            "Kualitas udara dalam batas toleransi aman WHO / baku mutu lingkungan.",
            "Lanjutkan pemantauan rutin berkala berbasis IoT stasiun cuaca."
        ]
        
    return {
        'status': status,
        'color': color,
        'badge_class': badge_class,
        'max_pm25': round(max_pm25, 1),
        'mean_pm25': round(mean_pm25, 1),
        'p90_pm25': round(p90_pm25, 1),
        'actions': action
    }
