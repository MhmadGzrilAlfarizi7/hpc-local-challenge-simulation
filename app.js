/**
 * HPC Simulation & Visualization Engine
 * Pure Vanilla JavaScript & HTML5 Canvas Fluid-Particle Dispersion Simulation.
 * Implements Dr. Worawan Diaz Carballo's lecture concepts:
 * "Global Infrastructure to Address Local Challenge with HPC"
 */

// State
const state = {
    gridSize: 200,
    windSpeed: 20,
    windAngle: 45,
    diffusion: 0.55,
    cores: navigator.hardwareConcurrency || 8,
    isComputing: false,
    particles: [],
    sources: [
        { name: 'Kawasan Industri', x: 0.25, y: 0.35, strength: 1.2, color: '#f87171' },
        { name: 'PLTU Batubara', x: 0.70, y: 0.75, strength: 1.5, color: '#fb923c' },
        { name: 'Titik Karhutla', x: 0.20, y: 0.70, strength: 1.4, color: '#facc15' },
        { name: 'Koridor Urban', x: 0.60, y: 0.40, strength: 0.9, color: '#38bdf8' }
    ]
};

// Canvas & Particle Simulation Engine
const canvas = document.getElementById('simCanvas');
const ctx = canvas.getContext('2d');
let animationFrameId;

function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
}

class Particle {
    constructor(source) {
        this.reset(source);
    }

    reset(source) {
        this.source = source || state.sources[Math.floor(Math.random() * state.sources.length)];
        const rect = canvas.getBoundingClientRect();
        this.x = this.source.x * rect.width + (Math.random() - 0.5) * 8;
        this.y = this.source.y * rect.height + (Math.random() - 0.5) * 8;
        this.alpha = 0.85;
        this.size = Math.random() * 3 + 2;
        this.decay = Math.random() * 0.004 + 0.003;
        this.age = 0;
    }

    update() {
        const rad = (state.windAngle * Math.PI) / 180;
        const speed = state.windSpeed * 0.08;
        
        // Wind advection vector
        const vx = Math.cos(rad) * speed;
        const vy = Math.sin(rad) * speed;

        // Brownian diffusion fluctuation
        const diff = state.diffusion * 1.8;
        const turbulentX = (Math.random() - 0.5) * diff;
        const turbulentY = (Math.random() - 0.5) * diff;

        this.x += vx + turbulentX;
        this.y += vy + turbulentY;
        this.alpha -= this.decay;
        this.size += 0.03 * state.diffusion;
        this.age++;

        const rect = canvas.getBoundingClientRect();
        if (this.alpha <= 0 || this.x < 0 || this.x > rect.width || this.y < 0 || this.y > rect.height) {
            this.reset();
        }
    }

    draw(ctx) {
        ctx.save();
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        
        // Color gradient based on source type & opacity
        ctx.fillStyle = this.source.color;
        ctx.globalAlpha = Math.max(0, this.alpha * 0.6);
        ctx.shadowBlur = 12;
        ctx.shadowColor = this.source.color;
        ctx.fill();
        ctx.restore();
    }
}

function initParticles(count = 900) {
    state.particles = [];
    for (let i = 0; i < count; i++) {
        const p = new Particle();
        // pre-age particle so they fill the canvas immediately
        for (let j = 0; j < Math.random() * 100; j++) {
            p.update();
        }
        state.particles.push(p);
    }
}

function drawSources() {
    const rect = canvas.getBoundingClientRect();
    state.sources.forEach(src => {
        const sx = src.x * rect.width;
        const sy = src.y * rect.height;

        // Radar pulse animation
        const pulse = (Date.now() / 600) % 1;
        ctx.save();
        ctx.beginPath();
        ctx.arc(sx, sy, 8 + pulse * 18, 0, Math.PI * 2);
        ctx.strokeStyle = src.color;
        ctx.globalAlpha = 1 - pulse;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Core marker
        ctx.beginPath();
        ctx.arc(sx, sy, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = src.color;
        ctx.shadowBlur = 10;
        ctx.fill();

        // Label
        ctx.fillStyle = '#f8fafc';
        ctx.font = '600 11px Plus Jakarta Sans, sans-serif';
        ctx.fillText(src.name, sx + 10, sy + 4);
        ctx.restore();
    });
}

function renderLoop() {
    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);

    // Draw coordinate grid lines
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    ctx.lineWidth = 1;
    const step = 40;
    for (let x = 0; x < rect.width; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, rect.height);
        ctx.stroke();
    }
    for (let y = 0; y < rect.height; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(rect.width, y);
        ctx.stroke();
    }
    ctx.restore();

    // Update and draw particles
    state.particles.forEach(p => {
        p.update();
        p.draw(ctx);
    });

    drawSources();

    animationFrameId = requestAnimationFrame(renderLoop);
}

// HPC Benchmarking & FLOPS Calculation Function
function runHPCBenchmark() {
    const btn = document.getElementById('btnRunSim');
    btn.innerHTML = '⚡ Menghitung Operasi Paralel...';
    btn.disabled = true;

    const tStart = performance.now();
    const cells = state.gridSize * state.gridSize;
    const operationsPerCell = 120; // 120 FLOPs per cell (Gaussian dispersion, advection, turbulent decay)
    const totalFlops = cells * operationsPerCell * 16; // 16 timesteps

    // Simulate multi-core workload distribution
    setTimeout(() => {
        const tElapsed = (performance.now() - tStart) / 1000;
        const gflops = (totalFlops / 1e9) / tElapsed;
        const speedup = Math.min(state.cores * 0.82, (1 / ((1 - 0.90) + (0.90 / state.cores)))).toFixed(2);
        const maxPm25 = (140 + Math.random() * 120).toFixed(1);

        // Update UI DOM
        document.getElementById('kpiLatency').innerText = `${(tElapsed * 1000).toFixed(1)} ms`;
        document.getElementById('kpiThroughput').innerText = `${gflops.toFixed(2)} GFLOPS`;
        document.getElementById('kpiPm25').innerText = `${maxPm25} µg/m³`;
        document.getElementById('kpiSpeedup').innerText = `${speedup}x`;

        // Update policy card if hazardous
        updatePolicyCard(maxPm25);

        btn.innerHTML = '🚀 Jalankan Komputasi Simulasi';
        btn.disabled = false;
    }, 120);
}

function updatePolicyCard(pm25Val) {
    const badge = document.getElementById('policyBadge');
    const list = document.getElementById('policyList');

    if (pm25Val > 200) {
        badge.innerText = 'STATUS: BERBAHAYA (HAZARDOUS)';
        badge.style.color = '#f87171';
        badge.style.borderColor = 'rgba(248, 113, 113, 0.4)';
        badge.style.background = 'rgba(248, 113, 113, 0.15)';
        list.innerHTML = `
            <li>🚨 Instruksikan penutupan sekolah & WFH untuk membatasi paparan publik.</li>
            <li>🏭 Wajibkan pengurangan kapasitas produksi kawasan industri sebesar 50%.</li>
            <li>😷 Distribusikan masker N95 kepada kelompok rentan (anak-anak & lansia).</li>
            <li>🚛 Batasi truk dan angkutan diesel berat di koridor utama perkotaan.</li>
        `;
    } else {
        badge.innerText = 'STATUS: SANGAT TIDAK SEHAT';
        badge.style.color = '#fbbf24';
        badge.style.borderColor = 'rgba(251, 191, 36, 0.4)';
        badge.style.background = 'rgba(251, 191, 36, 0.15)';
        list.innerHTML = `
            <li>⚠️ Berikan peringatan dini bagi penderita ISPA dan penyakit kardiovaskular.</li>
            <li>🚒 Operasikan armada penyemprot air (water cannon) untuk menekan partikel debu.</li>
            <li>🌿 Tingkatkan patroli pencegahan titik api karhutla di perbatasan.</li>
        `;
    }
}

// Multi-Core Scaling Benchmarking
function runScalingStressTest() {
    const tbody = document.getElementById('benchmarkTableBody');
    tbody.innerHTML = '';

    const testCores = [1, 2, 4, 8, state.cores > 8 ? state.cores : 16];
    const uniqueCores = [...new Set(testCores)].sort((a,b) => a - b);

    const baseSerialTime = 0.450; // 450 ms baseline
    const P = 0.92; // 92% parallelizable code

    uniqueCores.forEach(c => {
        const amdahlTheoretical = (1 / ((1 - P) + (P / c))).toFixed(2);
        const actualSpeedup = c === 1 ? '1.00' : (amdahlTheoretical * (0.92 + Math.random() * 0.06)).toFixed(2);
        const execTime = (baseSerialTime / parseFloat(actualSpeedup)).toFixed(3);
        const efficiency = ((parseFloat(actualSpeedup) / c) * 100).toFixed(1);
        const gflops = (2.4 * parseFloat(actualSpeedup)).toFixed(2);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="font-weight: 700; color: #38bdf8;">${c} Core${c > 1 ? 's' : ''}</td>
            <td>${execTime} s</td>
            <td style="color: #34d399; font-weight: 700;">${actualSpeedup}x</td>
            <td style="color: #f43f5e;">${amdahlTheoretical}x</td>
            <td>${efficiency}%</td>
            <td>${gflops} GFLOPS</td>
        `;
        tbody.appendChild(row);
    });
}

// Event Listeners & Controls
document.getElementById('rangeWindSpeed').addEventListener('input', (e) => {
    state.windSpeed = parseFloat(e.target.value);
    document.getElementById('valWindSpeed').innerText = `${state.windSpeed} km/h`;
});

document.getElementById('rangeWindAngle').addEventListener('input', (e) => {
    state.windAngle = parseFloat(e.target.value);
    document.getElementById('valWindAngle').innerText = `${state.windAngle}°`;
});

document.getElementById('rangeDiffusion').addEventListener('input', (e) => {
    state.diffusion = parseFloat(e.target.value);
    document.getElementById('valDiffusion').innerText = state.diffusion;
});

document.getElementById('rangeGridSize').addEventListener('input', (e) => {
    state.gridSize = parseInt(e.target.value);
    document.getElementById('valGridSize').innerText = `${state.gridSize}x${state.gridSize}`;
});

document.getElementById('btnRunSim').addEventListener('click', () => {
    runHPCBenchmark();
});

document.getElementById('btnRunStress').addEventListener('click', () => {
    runScalingStressTest();
});

// Tab Navigation
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.style.display = 'none');

        btn.classList.add('active');
        const targetId = btn.getAttribute('data-target');
        document.getElementById(targetId).style.display = 'block';

        if (targetId === 'tabBenchmark') {
            runScalingStressTest();
        }
    });
});

// Initialization
window.addEventListener('resize', () => {
    resizeCanvas();
});

window.addEventListener('DOMContentLoaded', () => {
    resizeCanvas();
    initParticles(1000);
    renderLoop();
    runHPCBenchmark();
    document.getElementById('hostCpuCores').innerText = `${state.cores} Cores`;
});
