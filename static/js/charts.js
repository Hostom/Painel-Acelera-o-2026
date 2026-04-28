/* static/js/charts.js */
document.addEventListener('DOMContentLoaded', function() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const bgColor = isDark ? '#1E293B' : '#FFFFFF';
    const textColor = isDark ? '#F1F5F9' : '#0F172A';
    const gridColor = isDark ? '#334155' : '#E2E8F0';

    // Helper para extrair dados do JSON seguro injetado pelo Django
    function getJson(id) {
        return JSON.parse(document.getElementById(id).textContent);
    }

    // === GAUGE CHART (Termômetro) ===
    const gauge = getJson('gauge-data');
    Plotly.newPlot('gauge-chart', [{
        type: 'indicator',
        mode: 'gauge+number',
        value: gauge.value,
        number: { suffix: '%', font: { size: 28, family: 'Manrope', color: textColor } },
        gauge: {
            axis: { range: [0, 120], tickcolor: gridColor },
            bar: { color: gauge.value >= 71 ? '#10B981' : gauge.value >= 40 ? '#F59E0B' : '#EF4444' },
            bgcolor: isDark ? '#334155' : '#F1F5F9',
            steps: [
                { range: [0, 70], color: isDark ? '#451a03' : '#FEF3C7' },
                { range: [70, 100], color: isDark ? '#052e16' : '#D1FAE5' },
            ]
        }
    }], {
        paper_bgcolor: 'transparent',
        margin: { t: 20, b: 10, l: 30, r: 30 },
    }, { responsive: true, displayModeBar: false });

    // === FUNIL CHART (FDL) ===
    const funil = getJson('funil-data');
    Plotly.newPlot('funil-chart', [
        {
            type: 'bar',
            name: 'Imobiliária',
            x: funil.fases,
            y: funil.valores,
            marker: { color: '#2563EB' },
        },
        {
            type: 'scatter',
            name: 'Ref. Nacional (%)',
            x: funil.fases,
            y: funil.referencia,
            yaxis: 'y2',
            mode: 'lines+markers',
            line: { color: '#F59E0B', dash: 'dash' }
        }
    ], {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 20, b: 40, l: 40, r: 50 },
        font: { family: 'Inter', color: textColor },
        yaxis: { title: 'Quantidade', gridcolor: gridColor },
        yaxis2: { title: 'Ref. (%)', overlaying: 'y', side: 'right', range: [0, 110] },
        legend: { orientation: 'h', y: 1.2 }
    }, { responsive: true, displayModeBar: false });

    // === BAIRROS CHART ===
    const bairros = getJson('bairros-data');
    Plotly.newPlot('bairros-chart', [{
        type: 'bar',
        y: bairros.nomes,
        x: bairros.alugados,
        orientation: 'h',
        marker: { color: '#10B981' },
    }], {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 10, b: 30, l: 100, r: 10 },
        font: { family: 'Inter', color: textColor, size: 11 },
        xaxis: { gridcolor: gridColor },
        yaxis: { autorange: 'reversed' }
    }, { responsive: true, displayModeBar: false });
});
