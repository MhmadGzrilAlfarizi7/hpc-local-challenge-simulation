import os
import time
import psutil
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import hpc_engine

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="HPC Air Quality & Parallel Benchmark",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Prevent browser auto-translate DOM corruptions
st.markdown('<meta name="google" content="notranslate" />', unsafe_allow_html=True)

# Load External Custom CSS stylesheet (style.css)
css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style.css')
if os.path.exists(css_file):
    with open(css_file, 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ==========================================================
# BESPOKE CSS & JAVASCRIPT INJECTION (Anti-Generic Styling)
# ==========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Gradient header title */
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.6;
        margin-bottom: 1.8rem;
    }

    /* Glassmorphism Metric Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.55);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 18px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.25);
    }

    .glass-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.35);
        box-shadow: 0 12px 28px -4px rgba(56, 189, 248, 0.15);
    }

    /* Custom KPI Display */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 18px 0;
    }

    .kpi-box {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 14px;
        padding: 16px 20px;
        position: relative;
        overflow: hidden;
    }

    .kpi-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #38BDF8, #818CF8);
    }

    .kpi-label {
        color: #94A3B8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
    }

    .kpi-subtext {
        font-size: 0.8rem;
        color: #38BDF8;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .badge-danger {
        background: rgba(239, 68, 68, 0.18);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.18);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }

    .badge-alert {
        background: rgba(234, 179, 8, 0.18);
        color: #FACC15;
        border: 1px solid rgba(234, 179, 8, 0.4);
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.18);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    /* Custom Table Styling */
    .custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin: 16px 0;
    }

    .custom-table th {
        background: rgba(30, 41, 59, 0.8);
        color: #38BDF8;
        font-size: 0.85rem;
        font-weight: 600;
        text-align: left;
        padding: 14px 18px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .custom-table td {
        background: rgba(15, 23, 42, 0.4);
        color: #E2E8F0;
        font-size: 0.88rem;
        padding: 12px 18px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        font-family: 'JetBrains Mono', monospace;
    }

    .custom-table tr:hover td {
        background: rgba(56, 189, 248, 0.08);
    }

    /* Action item cards */
    .action-item {
        display: flex;
        align-items: flex-start;
        padding: 12px 16px;
        background: rgba(15, 23, 42, 0.5);
        border-left: 3px solid #38BDF8;
        border-radius: 0 10px 10px 0;
        margin-bottom: 10px;
        font-size: 0.92rem;
        color: #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# Hardware Detection
cpu_cores_logical = os.cpu_count() or 4
cpu_cores_physical = psutil.cpu_count(logical=False) or (cpu_cores_logical // 2)
cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else 0

# ==========================================================
# SIDEBAR NAVIGATION & HARDWARE TELEMETRY
# ==========================================================
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 10px 0 20px 0;">
    <div style="font-size: 2.2rem; margin-bottom: 6px;">⚡</div>
    <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">HPC SIMULATION LAB</div>
    <div style="font-size: 0.78rem; color: #38BDF8; letter-spacing: 0.05em; font-weight: 600;">HIGH PERFORMANCE COMPUTING</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🧭 Navigasi Menu")
menu = st.sidebar.radio(
    "Pilih Modul:",
    [
        "1. Simulasi Polusi PM2.5 (Kasus LANTA)",
        "2. HPC Multi-Core Scaling & FLOPS Benchmark",
        "3. Konsep 'The Integrator' & Info HPC"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 14px;">
    <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">
        🖥️ Telemetri Node Komputasi
    </div>
    <div style="font-size: 0.85rem; color: #F1F5F9; line-height: 1.7; font-family: 'JetBrains Mono', monospace;">
        • Logical Cores : <strong style="color: #38BDF8;">{cpu_cores_logical} Cores</strong><br>
        • Physical Cores: <strong style="color: #818CF8;">{cpu_cores_physical} Cores</strong><br>
        • Max Frequency : <strong style="color: #34D399;">{cpu_freq:.0f} MHz</strong><br>
        • Engine Status : <strong style="color: #38BDF8;">Multi-Process Pool</strong>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="margin-top: 20px; font-size: 0.76rem; color: #64748B; line-height: 1.5;">
    <strong>Informatics Lecture Series:</strong><br>
    Narasumber: Dr. Worawan Diaz Carballo<br>
    (Thammasat University - HPC Expert)
</div>
""", unsafe_allow_html=True)

# ==========================================================
# PAGE 1: AIR QUALITY PM2.5 DISPERSION SIMULATION
# ==========================================================
if menu == "1. Simulasi Polusi PM2.5 (Kasus LANTA)":
    st.markdown('<div class="hero-title">Simulasi Prediksi Kualitas Udara (PM2.5)</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Implementasi studi kasus nyata Superkomputer LANTA (Thailand): Mempercepat pemodelan atmosfer 2D dari hitungan hari menjadi detik menggunakan domain-decomposition paralel.</div>', unsafe_allow_html=True)

    col_ctrl, col_view = st.columns([1, 2.2])

    with col_ctrl:
        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top: 0; color: #38BDF8;">⚙️ Parameter Simulasi Fisika</h4>
        """, unsafe_allow_html=True)

        grid_res = st.select_slider(
            "Resolusi Grid Spasial (N x N Cell)",
            options=[100, 150, 200, 250, 300],
            value=150,
            help="Semakin besar grid, semakin banyak titik kalkulasi floating-point (FLOPs) yang harus dihitung."
        )

        wind_speed = st.slider("Kecepatan Angin (km/jam)", min_value=5.0, max_value=50.0, value=18.0, step=1.0)
        wind_angle = st.slider("Arah Embusan Angin (° Derajat)", min_value=0, max_value=360, value=45, step=15)
        diff_rate = st.slider("Koefisien Dispersi Difusi Udara", min_value=0.2, max_value=1.0, value=0.55, step=0.05)

        st.markdown("---")
        exec_mode = st.radio(
            "Metode Eksekusi Komputasi:",
            ["Single-Core (Serial CPU)", f"Multi-Core Paralel ({cpu_cores_logical} Cores)"],
            index=1
        )
        
        btn_simulate = st.button("🚀 Jalankan Komputasi Simulasi", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_view:
        simulator = hpc_engine.HPCAirQualitySimulator(
            grid_size=grid_res,
            wind_speed=wind_speed,
            wind_angle_deg=wind_angle,
            diff_coeff=diff_rate
        )

        # Run or load simulation
        if btn_simulate or 'sim_res' not in st.session_state:
            with st.spinner("⚡ Mengalokasikan thread komputasi paralel dan memproses persamaan fluida..."):
                if "Single-Core" in exec_mode:
                    res = simulator.run_serial()
                else:
                    res = simulator.run_parallel(num_workers=cpu_cores_logical)
                st.session_state['sim_res'] = res
                st.session_state['sim_impact'] = hpc_engine.evaluate_air_quality_impact(res['grid'])
        
        res = st.session_state['sim_res']
        impact = st.session_state['sim_impact']

        # KPI Dashboard Cards
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-box">
                <div class="kpi-label">Mode Komputasi</div>
                <div class="kpi-value" style="font-size: 1.25rem;">{res['cores']} Core{'s' if res['cores'] > 1 else ''}</div>
                <div class="kpi-subtext">{res['mode'].split('(')[0].strip()}</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">Waktu Eksekusi (Latency)</div>
                <div class="kpi-value">{res['elapsed_sec']*1000:.1f} <span style="font-size: 1rem; color: #94A3B8;">ms</span></div>
                <div class="kpi-subtext">{res['elapsed_sec']:.4f} detik</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">Kapasitas Throughput</div>
                <div class="kpi-value">{res['gflops']:.3f} <span style="font-size: 1rem; color: #94A3B8;">GFLOPS</span></div>
                <div class="kpi-subtext">{res['total_flops']/1e6:.1f} MFLOPs terhitung</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">Konsentrasi PM2.5 Puncak</div>
                <div class="kpi-value">{impact['max_pm25']} <span style="font-size: 1rem; color: #94A3B8;">µg/m³</span></div>
                <div class="kpi-subtext">Rata-rata: {impact['mean_pm25']} µg/m³</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Plotly Interactive Scientific Contour Heatmap
        grid = res['grid']
        fig = go.Figure(data=go.Contour(
            z=grid,
            colorscale='Inferno',
            contours=dict(
                coloring='heatmap',
                showlabels=True,
                labelfont=dict(size=10, color='white')
            ),
            colorbar=dict(
                title=dict(text="PM2.5 (µg/m³)", font=dict(color="#F8FAFC")),
                tickfont=dict(color="#94A3B8")
            ),
            hovertemplate="Koordinat (X:%{x}, Y:%{y})<br>Konsentrasi: %{z:.2f} µg/m³<extra></extra>"
        ))

        # Add Source Markers
        for src in simulator.sources:
            norm_x = (src['x'] / 100.0) * (grid_res - 1)
            norm_y = (src['y'] / 100.0) * (grid_res - 1)
            fig.add_trace(go.Scatter(
                x=[norm_x], y=[norm_y],
                mode='markers+text',
                marker=dict(symbol='star', size=13, color='#38BDF8', line=dict(width=1.5, color='#FFFFFF')),
                text=[src['name']],
                textposition='top center',
                textfont=dict(color='#F8FAFC', size=11, family='Plus Jakarta Sans'),
                name=src['name'],
                hoverinfo='text'
            ))

        fig.update_layout(
            title=dict(
                text=f"Peta Dispersi Spasial PM2.5 ({grid_res}x{grid_res} Cells - {grid_res*grid_res:,} Titik Kalkulasi)",
                font=dict(family="Plus Jakarta Sans", size=15, color="#F8FAFC")
            ),
            paper_bgcolor='rgba(15, 23, 42, 0.4)',
            plot_bgcolor='rgba(15, 23, 42, 0.4)',
            margin=dict(l=40, r=40, t=50, b=40),
            height=480,
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#64748B")),
            yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#64748B")),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Actionable Public Policy (The Integrator Value)
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid {impact['color']};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="margin: 0; color: #F8FAFC;">🎯 Keputusan Aksi Kebijakan Publik (Hasil Integrasi HPC)</h4>
                <span class="badge {impact['badge_class']}">{impact['status']}</span>
            </div>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 14px;">
                Sebagai <em>'Integrator'</em>, hasil simulasi komputasi super tidak berhenti di angka, melainkan diterjemahkan langsung menjadi tindakan taktis mitigasi bagi pemerintah dan masyarakat lokal:
            </p>
        """, unsafe_allow_html=True)

        for act in impact['actions']:
            st.markdown(f'<div class="action-item"><span style="margin-right: 10px;">📋</span>{act}</div>', unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# PAGE 2: HPC MULTI-CORE SCALING & FLOPS BENCHMARK
# ==========================================================
elif menu == "2. HPC Multi-Core Scaling & FLOPS Benchmark":
    st.markdown('<div class="hero-title">Benchmark Akselerasi Paralel & Hukum Amdahl</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Uji langsung kemampuan komputasi CPU Anda: Mengukur percepatan (Speedup), efisiensi paralel, dan throughput GFLOPS dari 1 Core hingga Multi-Core.</div>', unsafe_allow_html=True)

    col_bench_ctrl, col_bench_view = st.columns([1, 2.5])

    with col_bench_ctrl:
        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top: 0; color: #38BDF8;">⚡ Konfigurasi Uji Beban</h4>
        """, unsafe_allow_html=True)

        test_grid = st.select_slider(
            "Beban Komputasi (Ukuran Grid)",
            options=[150, 200, 250, 300],
            value=200,
            help="Ukuran 200x200 menghasilkan puluhan juta operasi floating point."
        )

        # Select cores to test
        available_cores = [1]
        if cpu_cores_logical >= 2: available_cores.append(2)
        if cpu_cores_logical >= 4: available_cores.append(4)
        if cpu_cores_logical >= 6 and 6 not in available_cores: available_cores.append(6)
        if cpu_cores_logical not in available_cores: available_cores.append(cpu_cores_logical)

        st.write(f"**Core yang akan diuji:** {available_cores}")

        run_bench = st.button("🔥 Mulai HPC Stress-Test Benchmark", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_bench_view:
        if run_bench or 'df_benchmark' not in st.session_state:
            with st.spinner("⏳ Menjalankan benchmark serial dan paralel di seluruh core CPU..."):
                sim = hpc_engine.HPCAirQualitySimulator(grid_size=test_grid)
                df_bench, _ = sim.run_benchmark_suite(core_list=available_cores)
                st.session_state['df_benchmark'] = df_bench
                st.session_state['bench_grid'] = test_grid

        df_bench = st.session_state['df_benchmark']
        grid_used = st.session_state.get('bench_grid', 200)

        # Render Benchmark Comparison Charts (Plotly)
        fig_bench = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Percepatan (Speedup) vs Hukum Amdahl", "Throughput Operasi Komputasi (GFLOPS)"),
            horizontal_spacing=0.12
        )

        # Speedup vs Theoretical
        fig_bench.add_trace(go.Scatter(
            x=df_bench['Cores'], y=df_bench['Speedup (x)'],
            mode='lines+markers',
            name='Speedup Aktual CPU',
            line=dict(color='#38BDF8', width=3),
            marker=dict(size=9, color='#38BDF8')
        ), row=1, col=1)

        fig_bench.add_trace(go.Scatter(
            x=df_bench['Cores'], y=df_bench['Theoretical Speedup (Amdahl)'],
            mode='lines',
            name='Teori Amdahl (P=90%)',
            line=dict(color='#F43F5E', width=2, dash='dot')
        ), row=1, col=1)

        # Linear ideal line
        fig_bench.add_trace(go.Scatter(
            x=df_bench['Cores'], y=df_bench['Cores'],
            mode='lines',
            name='Ideal Linear Scaling',
            line=dict(color='#10B981', width=1.5, dash='dash')
        ), row=1, col=1)

        # GFLOPS Bar Chart
        fig_bench.add_trace(go.Bar(
            x=df_bench['Mode'], y=df_bench['Compute Throughput (GFLOPS)'],
            name='Throughput (GFLOPS)',
            marker=dict(
                color=df_bench['Compute Throughput (GFLOPS)'],
                colorscale='Viridis'
            )
        ), row=1, col=2)

        fig_bench.update_layout(
            paper_bgcolor='rgba(15, 23, 42, 0.4)',
            plot_bgcolor='rgba(15, 23, 42, 0.4)',
            font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
            height=390,
            margin=dict(l=40, r=40, t=50, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_bench, use_container_width=True)

        # HTML Formatted Pandas Benchmark Table
        st.markdown(f"#### 📊 Tabel Ringkasan Metrik Kinerja HPC ({grid_used}x{grid_used} Grid)")
        
        table_html = "<table class='custom-table'><thead><tr>"
        for col in df_bench.columns:
            table_html += f"<th>{col}</th>"
        table_html += "</tr></thead><tbody>"
        
        for _, row in df_bench.iterrows():
            table_html += "<tr>"
            for col in df_bench.columns:
                val = row[col]
                if col == 'Mode':
                    table_html += f"<td style='font-weight: 700; color: #38BDF8;'>{val}</td>"
                elif col == 'Speedup (x)':
                    table_html += f"<td style='color: #34D399; font-weight: 700;'>{val}x</td>"
                else:
                    table_html += f"<td>{val}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"

        st.markdown(table_html, unsafe_allow_html=True)

        # Insight box
        max_speedup = df_bench['Speedup (x)'].max()
        time_saved = (df_bench.iloc[0]['Execution Time (s)'] - df_bench.iloc[-1]['Execution Time (s)'])
        pct_saved = (time_saved / df_bench.iloc[0]['Execution Time (s)']) * 100 if df_bench.iloc[0]['Execution Time (s)'] > 0 else 0

        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #10B981;">
            <h4 style="margin: 0 0 8px 0; color: #34D399;">💡 Analisis Hasil Uji Komputasi</h4>
            <p style="color: #CBD5E1; font-size: 0.92rem; line-height: 1.6; margin: 0;">
                Dengan memanfaatkan arsitektur multi-core paralel pada mesin Anda, proses komputasi mendapatkan percepatan maksimal sebesar 
                <strong style="color: #38BDF8;">{max_speedup:.2f}x lebih cepat</strong> dan memangkas waktu kalkulasi hingga 
                <strong style="color: #34D399;">{pct_saved:.1f}%</strong> dibandingkan komputasi serial single-core tradisional. 
                Hal ini membuktikan efektivitas <em>domain decomposition</em> dalam menangani persoalan simulasi berskala besar.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ==========================================================
# PAGE 3: THE INTEGRATOR & HPC KNOWLEDGE BASE
# ==========================================================
else:
    st.markdown('<div class="hero-title">Konsep "The Integrator" & Ekosistem HPC</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Menghubungkan Infrastruktur Komputasi Global dengan Solusi Tantangan Nyata di Masyarakat Lokal.</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #38BDF8; margin-top: 0;">🌐 Mengapa Kita Membutuhkan "Integrator"?</h4>
            <p style="color: #CBD5E1; line-height: 1.6; font-size: 0.92rem;">
                Materi kuliah tamu oleh <strong>Dr. Worawan Diaz Carballo</strong> menekankan bahwa memiliki superkomputer bernilai jutaan dolar tidak akan berguna jika tidak ada talenta yang mampu menghubungkannya dengan masalah nyata.
            </p>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 14px 18px; border-radius: 12px; margin: 14px 0; border: 1px solid rgba(255, 255, 255, 0.05);">
                <div style="font-weight: 700; color: #F8FAFC; margin-bottom: 4px;">🎯 Formula "The Integrator":</div>
                <div style="color: #94A3B8; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">
                    Solusi Nyata = Domain Problem + Computational Logic + HPC Infrastructure
                </div>
            </div>
            <p style="color: #CBD5E1; line-height: 1.6; font-size: 0.92rem;">
                Mahasiswa Informatika berada di posisi strategis untuk menerjemahkan model fisik/biologis menjadi skrip paralel (MPI, OpenMP, CUDA, Multiprocessing) yang efisien.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #818CF8; margin-top: 0;">🌏 4 Studi Kasus Nyata di Kuliah Tamu</h4>
            <div style="margin-bottom: 12px;">
                <strong style="color: #38BDF8;">1. Banjir Bandang di Bangladesh:</strong><br>
                <span style="color: #94A3B8; font-size: 0.88rem;">Pemodelan hidrologi prediktif dijalankan sebelum hujan lebat turun, memungkinkan bantuan didistribusikan sebelum banjir melanda.</span>
            </div>
            <div style="margin-bottom: 12px;">
                <strong style="color: #38BDF8;">2. Polusi PM2.5 & Superkomputer LANTA (Thailand):</strong><br>
                <span style="color: #94A3B8; font-size: 0.88rem;">Penyusunan prediksi kualitas udara dipercepat dari 3 hari menjadi 7 hari ke depan dengan waktu pemrosesan hitungan jam.</span>
            </div>
            <div style="margin-bottom: 12px;">
                <strong style="color: #38BDF8;">3. Pertanian Cerdas di Norwegia:</strong><br>
                <span style="color: #94A3B8; font-size: 0.88rem;">Klaster GPU digunakan untuk memproses citra satelit resolusi tinggi guna memetakan kesuburan lahan secara presisi.</span>
            </div>
            <div>
                <strong style="color: #38BDF8;">4. Genomik Patogen di Uganda:</strong><br>
                <span style="color: #94A3B8; font-size: 0.88rem;">Analisis metagenomik untuk mendeteksi varian virus baru sebelum menjadi epidemi luas.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #C084FC; margin-top: 0;">📈 Skala Daya Komputasi (FLOPS Hierarchy)</h4>
            <table class="custom-table">
                <thead>
                    <tr>
                        <th>Tingkatan FLOPS</th>
                        <th>Orde</th>
                        <th>Contoh Penggunaan Riil</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="color: #94A3B8;">kiloFLOPS</td>
                        <td>10³</td>
                        <td>Kalkulator & micro-controller awal</td>
                    </tr>
                    <tr>
                        <td style="color: #94A3B8;">megaFLOPS</td>
                        <td>10⁶</td>
                        <td>Komputer era 80-an & simulasi grafis dasar</td>
                    </tr>
                    <tr>
                        <td style="color: #38BDF8;">gigaFLOPS</td>
                        <td>10⁹</td>
                        <td>Laptop & Smartphone modern saat ini</td>
                    </tr>
                    <tr>
                        <td style="color: #38BDF8;">teraFLOPS</td>
                        <td>10¹²</td>
                        <td>GPU Gaming (RTX), AI Inference, Workstation</td>
                    </tr>
                    <tr>
                        <td style="color: #F43F5E; font-weight: 700;">petaFLOPS</td>
                        <td>10¹⁵</td>
                        <td>Superkomputer LANTA (Thailand), Iklim, Fisika</td>
                    </tr>
                    <tr>
                        <td style="color: #F43F5E; font-weight: 700;">exaFLOPS</td>
                        <td>10¹⁸</td>
                        <td>Superkomputer Frontier & El Capitan (Exascale AI)</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <h4 style="color: #34D399; margin-top: 0;">🛠️ Skillset Wajib untuk Praktisi HPC</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;">
                <span style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; padding: 5px 12px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">Linux & SSH</span>
                <span style="background: rgba(129, 140, 248, 0.15); color: #818CF8; padding: 5px 12px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">Job Scripting (SLURM)</span>
                <span style="background: rgba(52, 211, 153, 0.15); color: #34D399; padding: 5px 12px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">Python & Pandas</span>
                <span style="background: rgba(244, 63, 94, 0.15); color: #F43F5E; padding: 5px 12px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">Parallel (MPI / OpenMP)</span>
                <span style="background: rgba(251, 191, 36, 0.15); color: #FBBF24; padding: 5px 12px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">GPU CUDA Computing</span>
                <span style="background: rgba(192, 132, 252, 0.15); color: #C084FC; padding: 5px 12px; border-radius: 8px; font-size: 0.82rem; font-weight: 600;">Git & Version Control</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
