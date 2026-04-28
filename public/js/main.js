/**
 * Painel 220 — Main JS (Vanilla)
 * Gerencia Fetch API, Reatividade e Gráficos Plotly.
 */

async function refreshData() {
    const mes = document.getElementById('mes-select').value;
    const ano = 2026;
    
    // Atualiza Labels
    document.getElementById('mes-label').innerText = mes;
    
    try {
        const response = await fetch(`/api/dashboard?ano=${ano}&mes=${mes}`);
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        updateKPIs(data.kpis);
        renderCharts(data);
        
    } catch (error) {
        console.error("Erro ao buscar dados:", error);
    }
}

function updateKPIs(kpis) {
    const formatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
    
    document.getElementById('kpi-vgl').innerText = formatter.format(kpis.vgl);
    document.getElementById('kpi-vgc').innerText = formatter.format(kpis.vgc);
    document.getElementById('kpi-alugados').innerText = kpis.alugados;
    document.getElementById('kpi-churn').innerText = kpis.churn.toFixed(1) + '%';
}

function renderCharts(data) {
    // 1. Gauge Chart (Termômetro)
    const gaugeTrace = {
        type: "indicator",
        mode: "gauge+number",
        value: data.kpis.termometro_vgl * 100,
        number: { suffix: "%", font: { size: 40, family: 'Manrope' } },
        gauge: {
            axis: { range: [0, 120], tickcolor: "#cbd5e1" },
            bar: { color: "#2563eb" },
            bgcolor: "white",
            steps: [
                { range: [0, 70], color: "#fee2e2" },
                { range: [70, 100], color: "#dcfce7" }
            ]
        }
    };
    
    Plotly.newPlot('chart-gauge', [gaugeTrace], {
        margin: { t: 0, b: 0, l: 30, r: 30 },
        paper_bgcolor: "transparent"
    });

    // 2. Funil Chart (FDL)
    const funnelTrace = {
        type: 'bar',
        x: ['Leads', 'Interação', 'Visita', 'Condição', 'Alugado'],
        y: [data.funil.leads, data.funil.interacoes, data.funil.visitas, data.funil.condicoes, data.funil.alugados],
        marker: { color: '#2563eb' },
        name: 'Realizado'
    };

    const refTrace = {
        type: 'scatter',
        x: ['Leads', 'Interação', 'Visita', 'Condição', 'Alugado'],
        y: data.referencia_nacional,
        yaxis: 'y2',
        mode: 'lines+markers',
        name: 'Ref. Nacional %',
        line: { color: '#f59e0b', dash: 'dot' }
    };

    Plotly.newPlot('chart-fdl', [funnelTrace, refTrace], {
        margin: { t: 20, b: 40, l: 40, r: 40 },
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        yaxis: { title: 'Qtd' },
        yaxis2: { overlaying: 'y', side: 'right', title: '%', range: [0, 110] },
        legend: { orientation: 'h', y: -0.2 }
    });
}

function toggleDarkMode() {
    document.body.classList.toggle('dark');
    // Implementação simplificada: em produção usaria CSS variables
}

// Inicialização
document.addEventListener('DOMContentLoaded', refreshData);
