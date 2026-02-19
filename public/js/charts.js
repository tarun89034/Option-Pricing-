/* ============================================================
   Chart.js Interactive Visualizations
   ============================================================ */

const Charts = {
    instances: {},

    colors: {
        accent: '#6c7aee',
        accentLight: 'rgba(108, 122, 238, 0.2)',
        green: '#34d399',
        greenLight: 'rgba(52, 211, 153, 0.15)',
        red: '#f87171',
        redLight: 'rgba(248, 113, 113, 0.15)',
        yellow: '#fbbf24',
        gray: '#8a8a9a',
        gridLine: 'rgba(255, 255, 255, 0.04)',
        text: '#8a8a9a',
    },

    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#8a8a9a',
                    font: { family: "'Inter', sans-serif", size: 11 },
                    boxWidth: 12,
                    padding: 16,
                },
            },
            tooltip: {
                backgroundColor: 'rgba(18, 18, 30, 0.95)',
                titleColor: '#e4e4e8',
                bodyColor: '#8a8a9a',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                cornerRadius: 6,
                padding: 10,
                titleFont: { family: "'Inter', sans-serif", weight: '600', size: 12 },
                bodyFont: { family: "'JetBrains Mono', monospace", size: 11 },
                displayColors: true,
                boxWidth: 8,
                boxHeight: 8,
                boxPadding: 4,
            },
        },
        scales: {
            x: {
                ticks: { color: '#5a5a6e', font: { family: "'Inter', sans-serif", size: 10 } },
                grid: { color: 'rgba(255, 255, 255, 0.04)' },
            },
            y: {
                ticks: { color: '#5a5a6e', font: { family: "'JetBrains Mono', monospace", size: 10 } },
                grid: { color: 'rgba(255, 255, 255, 0.04)' },
            },
        },
    },

    destroy(id) {
        if (this.instances[id]) {
            this.instances[id].destroy();
            delete this.instances[id];
        }
    },

    createPriceChart(canvasId, data) {
        this.destroy(canvasId);
        const ctx = document.getElementById(canvasId).getContext('2d');
        const labels = data.map(d => d.date);
        const closes = data.map(d => d.close);

        this.instances[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Close Price',
                    data: closes,
                    borderColor: this.colors.accent,
                    backgroundColor: this.colors.accentLight,
                    borderWidth: 1.5,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    pointHoverBackgroundColor: this.colors.accent,
                    fill: true,
                    tension: 0.1,
                }],
            },
            options: {
                ...this.defaultOptions,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    ...this.defaultOptions.plugins,
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: ctx => ' ' + Utils.formatCurrency(ctx.raw),
                        },
                    },
                },
                scales: {
                    x: {
                        ...this.defaultOptions.scales.x,
                        ticks: {
                            ...this.defaultOptions.scales.x.ticks,
                            maxTicksLimit: 12,
                        },
                    },
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: v => '$' + v.toFixed(0),
                        },
                    },
                },
            },
        });
    },

    createVolumeChart(canvasId, data) {
        this.destroy(canvasId);
        const ctx = document.getElementById(canvasId).getContext('2d');
        const labels = data.map(d => d.date);
        const volumes = data.map(d => d.volume);
        const colors = data.map((d, i) => {
            if (i === 0) return this.colors.gray;
            return d.close >= data[i - 1].close ? this.colors.green : this.colors.red;
        });

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Volume',
                    data: volumes,
                    backgroundColor: colors.map(c => c + '40'),
                    borderColor: colors,
                    borderWidth: 1,
                }],
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: { display: false },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: ctx => ' Vol: ' + Utils.formatVolume(ctx.raw),
                        },
                    },
                },
                scales: {
                    x: {
                        ...this.defaultOptions.scales.x,
                        ticks: {
                            ...this.defaultOptions.scales.x.ticks,
                            maxTicksLimit: 12,
                        },
                    },
                    y: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: v => Utils.formatVolume(v),
                        },
                    },
                },
            },
        });
    },

    createModelComparisonChart(canvasId, pricingData) {
        this.destroy(canvasId);
        const ctx = document.getElementById(canvasId).getContext('2d');

        const labels = [
            'Black-Scholes',
            'Binomial (EU)',
            'Binomial (US)',
            'MC European',
            'MC Asian (A)',
            'MC Asian (G)',
            'MC Lookback',
            'MC Barrier',
        ];

        const values = [
            pricingData.black_scholes.price,
            pricingData.binomial.european_price,
            pricingData.binomial.american_price,
            pricingData.monte_carlo.european.price,
            pricingData.monte_carlo.asian_arithmetic.price,
            pricingData.monte_carlo.asian_geometric.price,
            pricingData.monte_carlo.lookback.price,
            pricingData.monte_carlo.barrier.price,
        ];

        const barColors = [
            this.colors.accent,
            this.colors.green,
            '#10b981',
            this.colors.yellow,
            '#f59e0b',
            '#d97706',
            this.colors.red,
            '#ef4444',
        ];

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Option Price',
                    data: values,
                    backgroundColor: barColors.map(c => c + '60'),
                    borderColor: barColors,
                    borderWidth: 1.5,
                    borderRadius: 4,
                }],
            },
            options: {
                ...this.defaultOptions,
                indexAxis: 'y',
                plugins: {
                    ...this.defaultOptions.plugins,
                    legend: { display: false },
                    tooltip: {
                        ...this.defaultOptions.plugins.tooltip,
                        callbacks: {
                            label: ctx => ' ' + Utils.formatCurrency(ctx.raw, 4),
                        },
                    },
                },
                scales: {
                    x: {
                        ...this.defaultOptions.scales.y,
                        ticks: {
                            ...this.defaultOptions.scales.y.ticks,
                            callback: v => '$' + v.toFixed(2),
                        },
                    },
                    y: {
                        ...this.defaultOptions.scales.x,
                        ticks: {
                            ...this.defaultOptions.scales.x.ticks,
                            font: { family: "'Inter', sans-serif", size: 10 },
                        },
                    },
                },
            },
        });
    },

    createGreeksChart(canvasId, bsGreeks, binGreeks) {
        this.destroy(canvasId);
        const ctx = document.getElementById(canvasId).getContext('2d');

        const labels = ['Delta', 'Gamma', 'Theta', 'Vega'];
        const bsValues = [bsGreeks.delta, bsGreeks.gamma, bsGreeks.theta, bsGreeks.vega];
        const binValues = [binGreeks.delta, binGreeks.gamma, binGreeks.theta, binGreeks.vega];

        this.instances[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Black-Scholes',
                        data: bsValues.map(Math.abs),
                        borderColor: this.colors.accent,
                        backgroundColor: this.colors.accentLight,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: this.colors.accent,
                    },
                    {
                        label: 'Binomial (American)',
                        data: binValues.map(Math.abs),
                        borderColor: this.colors.green,
                        backgroundColor: this.colors.greenLight,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: this.colors.green,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    ...this.defaultOptions.plugins,
                },
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.06)' },
                        grid: { color: 'rgba(255, 255, 255, 0.06)' },
                        pointLabels: {
                            color: '#8a8a9a',
                            font: { family: "'Inter', sans-serif", size: 11, weight: '500' },
                        },
                        ticks: {
                            backdropColor: 'transparent',
                            color: '#5a5a6e',
                            font: { family: "'JetBrains Mono', monospace", size: 9 },
                        },
                    },
                },
            },
        });
    },
};
