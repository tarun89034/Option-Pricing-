/* ============================================================
   Main Application Controller
   ============================================================ */

(function () {
    'use strict';

    // ---- Navigation ----
    const navButtons = Utils.qsa('.nav-btn');
    const views = Utils.qsa('.view');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.view;
            navButtons.forEach(b => b.classList.remove('active'));
            views.forEach(v => v.classList.remove('active'));
            btn.classList.add('active');
            Utils.el('view-' + target).classList.add('active');
        });
    });

    // ---- Pricing Calculator ----
    const pricingForm = Utils.el('pricing-form');
    const btnPrice = Utils.el('btn-price');

    pricingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        Utils.hideError('pricing-error');
        Utils.el('results-panel').style.display = 'none';

        const ticker = Utils.el('ticker').value.trim().toUpperCase();
        const optionType = Utils.el('option_type').value;
        const strike = Utils.el('strike').value || null;
        const days = Utils.el('days_to_expiry').value;

        if (!ticker || !days) return;

        Utils.setLoading(btnPrice, true);

        try {
            const data = await API.priceOption(ticker, optionType, strike, days);
            renderPricingResults(data);
            Utils.el('results-panel').style.display = 'block';
        } catch (err) {
            Utils.showError('pricing-error', 'pricing-error-msg', err.message);
        } finally {
            Utils.setLoading(btnPrice, false);
        }
    });

    function renderPricingResults(data) {
        // Market Data Summary
        const md = data.market_data;
        const mdGrid = Utils.el('market-data-summary');
        mdGrid.innerHTML = '';
        const mdItems = [
            ['Ticker', md.name + ' (' + md.ticker + ')'],
            ['Spot Price', Utils.formatCurrency(md.spot_price)],
            ['Strike Price', Utils.formatCurrency(md.strike_price)],
            ['Moneyness', md.moneyness + ' (' + Utils.formatNumber(md.moneyness_ratio, 3) + ')'],
            ['Volatility', Utils.formatPercent(md.volatility)],
            ['Risk-Free Rate', Utils.formatPercent(md.risk_free_rate)],
            ['Dividend Yield', Utils.formatPercent(md.dividend_yield)],
            ['Time to Expiry', md.days_to_expiry + ' days (' + Utils.formatNumber(md.time_to_expiry_years, 4) + ' yr)'],
        ];
        mdItems.forEach(([label, value]) => {
            mdGrid.appendChild(Utils.createDataItem(label, value));
        });

        // Pricing Table
        const bs = data.black_scholes;
        const mc = data.monte_carlo;
        const bn = data.binomial;
        const tbody = Utils.el('pricing-tbody');
        tbody.innerHTML = '';

        const rows = [
            ['Black-Scholes', 'European', bs.price, null],
            ['Binomial Tree', 'European', bn.european_price, null],
            ['Binomial Tree', 'American', bn.american_price, null],
            ['Monte Carlo', 'European', mc.european.price, mc.european.std_error],
            ['Monte Carlo', 'Asian (Arith.)', mc.asian_arithmetic.price, mc.asian_arithmetic.std_error],
            ['Monte Carlo', 'Asian (Geo.)', mc.asian_geometric.price, mc.asian_geometric.std_error],
            ['Monte Carlo', 'Lookback', mc.lookback.price, mc.lookback.std_error],
            ['Monte Carlo', mc.barrier.barrier_type, mc.barrier.price, mc.barrier.std_error],
        ];

        rows.forEach(([model, style, price, se]) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${model}</td>
                <td>${style}</td>
                <td>${Utils.formatCurrency(price, 4)}</td>
                <td>${se != null ? Utils.formatNumber(se, 6) : '--'}</td>
            `;
            tbody.appendChild(tr);
        });

        // Early exercise premium info
        if (bn.early_exercise_premium > 0.0001) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td colspan="2" style="color:var(--text-secondary);">Early Exercise Premium</td>
                <td style="color:var(--green);">${Utils.formatCurrency(bn.early_exercise_premium, 4)}</td>
                <td style="color:var(--text-muted);">${bn.early_exercise_nodes} nodes</td>
            `;
            tbody.appendChild(tr);
        }

        // Greeks Table
        const greeksTbody = Utils.el('greeks-tbody');
        greeksTbody.innerHTML = '';
        const bsGreeks = bs.greeks;
        const binGreeks = bn.greeks;
        const greekNames = [
            ['Delta', 'delta'],
            ['Gamma', 'gamma'],
            ['Theta', 'theta'],
            ['Vega', 'vega'],
        ];
        if (bsGreeks.rho != null) {
            greekNames.push(['Rho', 'rho']);
        }

        greekNames.forEach(([name, key]) => {
            const tr = document.createElement('tr');
            const bsVal = bsGreeks[key];
            const binVal = binGreeks != null ? binGreeks[key] : null;
            tr.innerHTML = `
                <td>${name}</td>
                <td>${bsVal != null ? Utils.formatNumber(bsVal, 6) : '--'}</td>
                <td>${binVal != null ? Utils.formatNumber(binVal, 6) : '--'}</td>
            `;
            greeksTbody.appendChild(tr);
        });

        // Convergence Summary
        const conv = data.convergence;
        const convGrid = Utils.el('convergence-summary');
        convGrid.innerHTML = '';
        convGrid.appendChild(Utils.createDataItem(
            'BS vs Binomial',
            Utils.formatCurrency(conv.bs_vs_binomial.diff, 6) + ' (' + conv.bs_vs_binomial.pct.toFixed(4) + '%)'
        ));
        convGrid.appendChild(Utils.createDataItem(
            'BS vs Monte Carlo',
            Utils.formatCurrency(conv.bs_vs_monte_carlo.diff, 6) + ' (' + conv.bs_vs_monte_carlo.pct.toFixed(4) + '%)'
        ));

        // Charts
        Charts.createModelComparisonChart('model-comparison-chart', data);
        Charts.createGreeksChart('greeks-chart', bsGreeks, binGreeks || bsGreeks);
    }

    // ---- Historical Dashboard ----
    const dashForm = Utils.el('dashboard-form');
    const btnDash = Utils.el('btn-dashboard');

    dashForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        Utils.hideError('dashboard-error');
        Utils.el('dashboard-results').style.display = 'none';

        const ticker = Utils.el('dash-ticker').value.trim().toUpperCase();
        const period = Utils.el('dash-period').value;
        if (!ticker) return;

        Utils.setLoading(btnDash, true);

        try {
            const data = await API.getMarketData(ticker, period);
            renderDashboard(data);
            Utils.el('dashboard-results').style.display = 'block';
        } catch (err) {
            Utils.showError('dashboard-error', 'dashboard-error-msg', err.message);
        } finally {
            Utils.setLoading(btnDash, false);
        }
    });

    function renderDashboard(data) {
        const info = data.stock_info;
        Utils.el('dash-stock-title').textContent = info.name + ' (' + info.ticker + ')';

        const infoGrid = Utils.el('dash-stock-info');
        infoGrid.innerHTML = '';
        const items = [
            ['Exchange', info.exchange],
            ['Sector', info.sector],
            ['Industry', info.industry],
            ['Market Cap', Utils.formatMarketCap(info.market_cap)],
            ['Price', Utils.formatCurrency(info.spot_price)],
            ['Hist. Volatility', Utils.formatPercent(info.historical_volatility)],
            ['Dividend Yield', Utils.formatPercent(info.dividend_yield)],
            ['Risk-Free Rate', Utils.formatPercent(info.risk_free_rate)],
        ];
        items.forEach(([label, value]) => {
            infoGrid.appendChild(Utils.createDataItem(label, value));
        });

        // Charts
        Charts.createPriceChart('price-chart', data.historical_data);
        Charts.createVolumeChart('volume-chart', data.historical_data);

        // Historical Data Table
        const tbody = Utils.el('historical-tbody');
        tbody.innerHTML = '';
        const sorted = [...data.historical_data].reverse();
        sorted.forEach(d => {
            const tr = document.createElement('tr');
            const change = d.close - d.open;
            const cls = change >= 0 ? 'positive' : 'negative';
            tr.innerHTML = `
                <td>${d.date}</td>
                <td>${Utils.formatCurrency(d.open)}</td>
                <td>${Utils.formatCurrency(d.high)}</td>
                <td>${Utils.formatCurrency(d.low)}</td>
                <td class="${cls}">${Utils.formatCurrency(d.close)}</td>
                <td>${Utils.formatVolume(d.volume)}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // ---- Options Chain ----
    const chainForm = Utils.el('chain-form');
    const btnChain = Utils.el('btn-chain');
    let chainData = null;

    const chainTickerInput = Utils.el('chain-ticker');
    let chainTickerDebounce = null;
    chainTickerInput.addEventListener('input', () => {
        clearTimeout(chainTickerDebounce);
        chainTickerDebounce = setTimeout(async () => {
            const ticker = chainTickerInput.value.trim().toUpperCase();
            if (ticker.length < 1) return;
            try {
                const data = await API.getOptionsChain(ticker);
                const expirySelect = Utils.el('chain-expiry');
                expirySelect.innerHTML = '';
                if (data.expiries && data.expiries.length > 0) {
                    data.expiries.forEach(exp => {
                        const opt = document.createElement('option');
                        opt.value = exp;
                        opt.textContent = exp;
                        expirySelect.appendChild(opt);
                    });
                } else {
                    expirySelect.innerHTML = '<option value="">No options available</option>';
                }
            } catch (e) {
                // Silently handle -- user is probably still typing
            }
        }, 600);
    });

    chainForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        Utils.hideError('chain-error');
        Utils.el('chain-results').style.display = 'none';

        const ticker = Utils.el('chain-ticker').value.trim().toUpperCase();
        const expiry = Utils.el('chain-expiry').value;
        if (!ticker) return;

        Utils.setLoading(btnChain, true);

        try {
            chainData = await API.getOptionsChain(ticker, expiry);
            renderChain('calls');
            Utils.el('chain-results').style.display = 'block';
            Utils.el('chain-title').textContent = ticker + ' Options Chain';
            Utils.el('chain-spot-price').textContent = 'Spot: ' + Utils.formatCurrency(chainData.spot_price);

            // Update expiry select
            const expirySelect = Utils.el('chain-expiry');
            expirySelect.innerHTML = '';
            if (chainData.expiries) {
                chainData.expiries.forEach(exp => {
                    const opt = document.createElement('option');
                    opt.value = exp;
                    opt.textContent = exp;
                    if (exp === chainData.selected_expiry) opt.selected = true;
                    expirySelect.appendChild(opt);
                });
            }
        } catch (err) {
            Utils.showError('chain-error', 'chain-error-msg', err.message);
        } finally {
            Utils.setLoading(btnChain, false);
        }
    });

    // Chain tabs
    Utils.qsa('.chain-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            Utils.qsa('.chain-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            if (chainData) renderChain(tab.dataset.chain);
        });
    });

    function renderChain(type) {
        if (!chainData) return;
        const items = type === 'calls' ? chainData.calls : chainData.puts;
        const tbody = Utils.el('chain-tbody');
        tbody.innerHTML = '';

        if (!items || items.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="8" style="text-align:center;color:var(--text-muted);">No data available</td>';
            tbody.appendChild(tr);
            return;
        }

        items.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${Utils.formatCurrency(row.strike)}</td>
                <td>${Utils.formatCurrency(row.lastPrice, 4)}</td>
                <td>${Utils.formatCurrency(row.bid, 4)}</td>
                <td>${Utils.formatCurrency(row.ask, 4)}</td>
                <td>${Utils.formatVolume(row.volume)}</td>
                <td>${Utils.formatVolume(row.openInterest)}</td>
                <td>${Utils.formatPercent(row.impliedVolatility)}</td>
                <td><span class="itm-badge ${row.inTheMoney ? 'yes' : 'no'}">${row.inTheMoney ? 'ITM' : 'OTM'}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // ---- Global Markets Explorer ----
    function initMarkets() {
        const regionTabs = Utils.el('region-tabs');
        const content = Utils.el('markets-content');
        const regions = Object.keys(GLOBAL_MARKETS);

        // Create region tabs
        regions.forEach((region, i) => {
            const btn = document.createElement('button');
            btn.className = 'region-tab' + (i === 0 ? ' active' : '');
            btn.textContent = region;
            btn.addEventListener('click', () => {
                Utils.qsa('.region-tab').forEach(t => t.classList.remove('active'));
                btn.classList.add('active');
                renderRegion(region);
            });
            regionTabs.appendChild(btn);
        });

        // Also add an "All" tab
        const allBtn = document.createElement('button');
        allBtn.className = 'region-tab';
        allBtn.textContent = 'All Regions';
        allBtn.addEventListener('click', () => {
            Utils.qsa('.region-tab').forEach(t => t.classList.remove('active'));
            allBtn.classList.add('active');
            renderAllRegions();
        });
        regionTabs.insertBefore(allBtn, regionTabs.firstChild);

        // Render first region
        renderRegion(regions[0]);
    }

    function renderRegion(region) {
        const content = Utils.el('markets-content');
        content.innerHTML = '';
        const countries = GLOBAL_MARKETS[region];
        Object.entries(countries).forEach(([country, data]) => {
            content.appendChild(createCountryCard(country, data));
        });
    }

    function renderAllRegions() {
        const content = Utils.el('markets-content');
        content.innerHTML = '';
        Object.values(GLOBAL_MARKETS).forEach(countries => {
            Object.entries(countries).forEach(([country, data]) => {
                content.appendChild(createCountryCard(country, data));
            });
        });
    }

    function createCountryCard(country, data) {
        const card = document.createElement('div');
        card.className = 'market-card';

        // Header
        const header = document.createElement('div');
        header.className = 'market-card-header';
        header.innerHTML = `
            <span class="market-card-country">${country}</span>
            <span class="market-card-currency">${data.currency}</span>
        `;
        card.appendChild(header);

        // Exchanges
        const exchanges = document.createElement('div');
        exchanges.className = 'market-exchanges';
        data.exchanges.forEach(ex => {
            const badge = document.createElement('span');
            badge.className = 'exchange-badge';
            badge.innerHTML = ex.name + (ex.suffix ? ' <span class="exchange-suffix">' + ex.suffix + '</span>' : '');
            badge.title = ex.desc;
            exchanges.appendChild(badge);
        });
        card.appendChild(exchanges);

        // Tickers
        const tickers = document.createElement('div');
        tickers.className = 'market-tickers';
        data.tickers.forEach(t => {
            const chip = document.createElement('div');
            chip.className = 'ticker-chip';
            chip.innerHTML = `
                <span class="ticker-chip-symbol">${t.symbol}</span>
                <span class="ticker-chip-name">${t.name}</span>
            `;
            chip.title = 'Load ' + t.symbol + ' into Pricing Calculator';
            chip.addEventListener('click', () => loadTickerIntoPricer(t.symbol));
            tickers.appendChild(chip);
        });
        card.appendChild(tickers);

        return card;
    }

    function loadTickerIntoPricer(symbol) {
        Utils.el('ticker').value = symbol;
        // Switch to pricing view
        navButtons.forEach(b => b.classList.remove('active'));
        views.forEach(v => v.classList.remove('active'));
        Utils.qs('[data-view="pricing"]').classList.add('active');
        Utils.el('view-pricing').classList.add('active');
        Utils.el('ticker').focus();
    }

    // Initialize markets on load
    if (typeof GLOBAL_MARKETS !== 'undefined') {
        initMarkets();
    }

    // ---- Table Sorting ----
    document.addEventListener('click', (e) => {
        const th = e.target.closest('th[data-sort]');
        if (!th) return;
        const table = th.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const key = th.dataset.sort;
        const idx = Array.from(th.parentElement.children).indexOf(th);

        const isAsc = th.classList.contains('sort-asc');
        table.querySelectorAll('th').forEach(t => t.classList.remove('sort-asc', 'sort-desc'));
        th.classList.add(isAsc ? 'sort-desc' : 'sort-asc');

        rows.sort((a, b) => {
            const aText = a.children[idx]?.textContent.replace(/[$,%]/g, '').trim() || '';
            const bText = b.children[idx]?.textContent.replace(/[$,%]/g, '').trim() || '';
            const aNum = parseFloat(aText);
            const bNum = parseFloat(bText);
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAsc ? bNum - aNum : aNum - bNum;
            }
            return isAsc ? bText.localeCompare(aText) : aText.localeCompare(bText);
        });

        rows.forEach(row => tbody.appendChild(row));
    });
})();
