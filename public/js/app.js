/* ============================================================
   Main Application Controller
   ============================================================ */

(function () {
    'use strict';

    // ---- State ----
    const State = {
        currency: 'USD',
        rate: 1.0,
        currencySymbol: '$',

        lastPricingData: null,
        lastDashboardData: null,
        lastChainData: null,
        lastChainType: 'calls'
    };

    const CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'JPY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'CNY': '¥',
    };

    // ---- Navigation ----
    const navButtons = Utils.qsa('.nav-btn');
    const views = Utils.qsa('.view');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.view;
            switchView(target);
        });
    });

    function switchView(target) {
        navButtons.forEach(b => b.classList.remove('active'));
        views.forEach(v => v.classList.remove('active'));

        const activeBtn = Utils.qs(`.nav-btn[data-view="${target}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        Utils.el('view-' + target).classList.add('active');
    }

    // ---- Currency Logic ----
    const currencySelect = Utils.el('currency-select');

    currencySelect.addEventListener('change', async () => {
        const newCurrency = currencySelect.value;
        if (newCurrency === State.currency) return;

        // Disable select while loading
        currencySelect.disabled = true;
        document.body.style.cursor = 'wait';

        try {
            if (newCurrency === 'USD') {
                State.rate = 1.0;
            } else {
                // Fetch rate USD -> NewCurrency
                const data = await API.getExchangeRate('USD', newCurrency);
                State.rate = data.rate;
            }
            State.currency = newCurrency;
            State.currencySymbol = CURRENCY_SYMBOLS[newCurrency] || '$';

            // Re-render current data with new rates
            if (State.lastPricingData) renderPricingResults(State.lastPricingData);
            if (State.lastDashboardData) renderDashboard(State.lastDashboardData);
            if (State.lastChainData) renderChain(State.lastChainType);

            // Update Markets if needed (though markets are static text mostly, maybe tickers?)
            // Markets explorer is mostly navigation, so no prices to update there immediately.

        } catch (err) {
            console.error('Failed to switch currency:', err);
            // Silently revert
            currencySelect.value = State.currency;
        } finally {
            currencySelect.disabled = false;
            document.body.style.cursor = 'default';
        }
    });

    // Helper to convert and format
    function formatMoney(value, decimals = 2) {
        if (value == null) return 'N/A';
        return Utils.formatCurrency(value * State.rate, State.currencySymbol, decimals);
    }

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
            // Note: API returns data in native currency (assumed USD for now or raw match)
            // Ideally we'd know the source currency. For now assuming input is consistent.
            // If user enters non-USD ticker, yfinance returns raw values.
            // We blindly convert assuming base is USD? 
            // WAIT. If I look at RELIANCE.NS, prices are in INR.
            // Converting INR * (USD->INR rate) would be wrong (squared).
            // Complexity: The backend doesn't tell us the currency of the ticker.
            // Actually `market_data_fetcher` returns `currency`.
            // We should use that!

            const data = await API.priceOption(ticker, optionType, strike, days);
            State.lastPricingData = data;

            // Check ticker currency
            await handleTickerCurrency(data.market_data.currency || 'USD');

            renderPricingResults(data);
            Utils.el('results-panel').style.display = 'block';
        } catch (err) {
            Utils.showError('pricing-error', 'pricing-error-msg', err.message);
        } finally {
            Utils.setLoading(btnPrice, false);
        }
    });

    // Handle ticker currency vs selected currency
    async function handleTickerCurrency(tickerCurrency) {
        // If ticker is e.g. INR and User selected INR. Rate = 1.
        // If ticker is USD and User selected INR. Rate = USD->INR.
        // If ticker is INR and User selected USD. Rate = INR->USD.

        // My simple State.rate was "USD -> Selected".
        // This assumes input is always USD.
        // But RELIANCE.NS gives INR.

        // Logic adjustment:
        // We need rate: TickerCurrency -> SelectedCurrency.

        if (tickerCurrency === State.currency) {
            State.rate = 1.0;
        } else {
            // Fetch cross rate
            try {
                const data = await API.getExchangeRate(tickerCurrency, State.currency);
                State.rate = data.rate;
            } catch (e) {
                console.warn("Could not fetch cross rate, defaulting to 1.0");
                State.rate = 1.0;
            }
        }
    }

    function renderPricingResults(data) {
        // Market Data Summary
        const md = data.market_data;
        const mdGrid = Utils.el('market-data-summary');
        mdGrid.innerHTML = '';
        const mdItems = [
            ['Ticker', md.name + ' (' + md.ticker + ')'],
            ['Spot Price', formatMoney(md.spot_price)],
            ['Strike Price', formatMoney(md.strike_price)],
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
                <td>${formatMoney(price, 4)}</td>
                <td>${se != null ? Utils.formatNumber(se * State.rate, 6) : '--'}</td>
            `;
            tbody.appendChild(tr);
        });

        // Early exercise premium info
        if (bn.early_exercise_premium > 0.0001) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td colspan="2" style="color:var(--text-secondary);">Early Exercise Premium</td>
                <td style="color:var(--green);">${formatMoney(bn.early_exercise_premium, 4)}</td>
                <td style="color:var(--text-muted);">${bn.early_exercise_nodes} nodes</td>
            `;
            tbody.appendChild(tr);
        }

        // Greeks Table (Greeks are unitless except Rho/Theta maybe? standard greeks are derivatives)
        // Delta (dC/dS) - unitless (ratio)
        // Gamma (d2C/dS2) - 1/currency? No, roughly.
        // Theta (dC/dt) - currency/time. Should convert!
        // Vega (dC/dSigma) - currency. Should convert!
        // Rho (dC/dr) - currency. Should convert!

        const greeksTbody = Utils.el('greeks-tbody');
        greeksTbody.innerHTML = '';
        const bsGreeks = bs.greeks;
        const binGreeks = bn.greeks;
        const greekNames = [
            ['Delta', 'delta', false],
            ['Gamma', 'gamma', false], // Gamma is 1/S, so technically 1/Currency. If we convert S->kS, Gamma->Gamma/k. 
            // Actually Price is kP, Spot is kS. Gamma = d2(kP)/d(kS)^2 = k/k^2 = 1/k Gamma.
            // This is getting complex. Let's keep greeks raw for now or just primary ones.
            // Actually, standard practice for retail app: usually show raw greeks or dollar greeks?
            // Let's Convert Theta, Vega, Rho, leave Delta Gamma.
            ['Theta', 'theta', true],
            ['Vega', 'vega', true],
        ];
        if (bsGreeks.rho != null) {
            greekNames.push(['Rho', 'rho', true]);
        }

        greekNames.forEach(([name, key, convert]) => {
            const tr = document.createElement('tr');
            let bsVal = bsGreeks[key];
            let binVal = binGreeks != null ? binGreeks[key] : null;

            if (convert) {
                if (bsVal != null) bsVal *= State.rate;
                if (binVal != null) binVal *= State.rate;
            } else if (key === 'gamma' && State.rate !== 1.0) {
                // Gamma scales with 1/Spot. if Spot is x100, Gamma is /100.
                if (bsVal != null) bsVal /= State.rate;
                if (binVal != null) binVal /= State.rate;
            }

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
            formatMoney(conv.bs_vs_binomial.diff, 6) + ' (' + conv.bs_vs_binomial.pct.toFixed(4) + '%)'
        ));
        convGrid.appendChild(Utils.createDataItem(
            'BS vs Monte Carlo',
            formatMoney(conv.bs_vs_monte_carlo.diff, 6) + ' (' + conv.bs_vs_monte_carlo.pct.toFixed(4) + '%)'
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
            State.lastDashboardData = data;

            await handleTickerCurrency(data.stock_info.currency || 'USD');

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
            ['Market Cap', Utils.formatMarketCap(info.market_cap * State.rate)], // Approx market cap conversion
            ['Price', formatMoney(info.spot_price)],
            ['Hist. Volatility', Utils.formatPercent(info.historical_volatility)],
            ['Dividend Yield', Utils.formatPercent(info.dividend_yield)],
            ['Risk-Free Rate', Utils.formatPercent(info.risk_free_rate)],
        ];
        items.forEach(([label, value]) => {
            infoGrid.appendChild(Utils.createDataItem(label, value));
        });

        // Charts - update data with rate?
        // Charts.js usually takes raw arrays. 
        // Let's create a mapped copy for charts if we want converted axes.
        const convertedHistory = data.historical_data.map(d => ({
            ...d,
            open: d.open * State.rate,
            high: d.high * State.rate,
            low: d.low * State.rate,
            close: d.close * State.rate
        }));

        Charts.createPriceChart('price-chart', convertedHistory);
        Charts.createVolumeChart('volume-chart', convertedHistory);

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
                <td>${formatMoney(d.open)}</td>
                <td>${formatMoney(d.high)}</td>
                <td>${formatMoney(d.low)}</td>
                <td class="${cls}">${formatMoney(d.close)}</td>
                <td>${Utils.formatVolume(d.volume)}</td>
            `;
            tbody.appendChild(tr);
        });
    }


    // ---- Options Chain ----
    const chainForm = Utils.el('chain-form');
    const btnChain = Utils.el('btn-chain');

    const chainTickerInput = Utils.el('chain-ticker');
    let chainTickerDebounce = null;
    chainTickerInput.addEventListener('input', () => {
        clearTimeout(chainTickerDebounce);
        chainTickerDebounce = setTimeout(async () => {
            const ticker = chainTickerInput.value.trim().toUpperCase();
            if (ticker.length < 1) return;
            try {
                // OPTIMIZATION: Use getExpiries instead of getOptionsChain
                const data = await API.getExpiries(ticker);

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
                const expirySelect = Utils.el('chain-expiry');
                expirySelect.innerHTML = '<option value="">Select ticker...</option>';
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
            const data = await API.getOptionsChain(ticker, expiry);
            State.lastChainData = data;

            // Assume Ticker Currency is same as last fetched or default USD if we don't know
            // Ideally chain endpoint returns currency. It doesn't currently. 
            // We can infer from MarketData if we want, but that's an extra call.
            // Let's assume USD for now OR assume user flow: they likely checked market data first.
            // Better: Add currency to options_chain response in backend?
            // Creating a lightweight separate fetch for currency here might be safe.
            // For now, let's just stick to State.rate if it was set by other views, 
            // OR reset to 1.0 (assuming USD input) if we switched tickers.

            // Re-fetch rate to be safe? 
            // Let's check ticker prefix/suffix? 
            // Simple heuristic to avoid complex chaining:
            // Just use the current rate logic but maybe reset if ticker changed?
            // Actually, let's keep it simple: If user selected INR, they want INR.
            // If they are looking at AAPL (USD), we convert USD->INR.
            // If they are looking at RELIANCE (INR), we convert INR->INR (1.0).
            // We need to know ticker currency.

            // For robustness, let's quickly fetch info to get currency.
            try {
                const info = await API.getMarketData(ticker, '1mo'); // 1mo is fast
                await handleTickerCurrency(info.stock_info.currency || 'USD');
            } catch (e) {/* ignore */ }

            renderChain('calls');
            Utils.el('chain-results').style.display = 'block';
            Utils.el('chain-title').textContent = ticker + ' Options Chain';
            Utils.el('chain-spot-price').textContent = 'Spot: ' + formatMoney(data.spot_price);

            // Update expiry select
            const expirySelect = Utils.el('chain-expiry');
            expirySelect.innerHTML = '';
            if (data.expiries) {
                data.expiries.forEach(exp => {
                    const opt = document.createElement('option');
                    opt.value = exp;
                    opt.textContent = exp;
                    if (exp === data.selected_expiry) opt.selected = true;
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
            State.lastChainType = tab.dataset.chain;
            if (State.lastChainData) renderChain(tab.dataset.chain);
        });
    });

    function renderChain(type) {
        if (!State.lastChainData) return;
        const items = type === 'calls' ? State.lastChainData.calls : State.lastChainData.puts;
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
                <td>${formatMoney(row.strike)}</td>
                <td>${formatMoney(row.lastPrice, 4)}</td>
                <td>${formatMoney(row.bid, 4)}</td>
                <td>${formatMoney(row.ask, 4)}</td>
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
        if (!regionTabs) return;
        const content = Utils.el('markets-content');
        const regions = Object.keys(GLOBAL_MARKETS);

        // Create region tabs
        regionTabs.innerHTML = '';
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

        const allBtn = document.createElement('button');
        allBtn.className = 'region-tab';
        allBtn.textContent = 'All Regions';
        allBtn.addEventListener('click', () => {
            Utils.qsa('.region-tab').forEach(t => t.classList.remove('active'));
            allBtn.classList.add('active');
            renderAllRegions();
        });
        regionTabs.insertBefore(allBtn, regionTabs.firstChild);

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
        const header = document.createElement('div');
        header.className = 'market-card-header';
        header.innerHTML = `
            <span class="market-card-country">${country}</span>
            <span class="market-card-currency">${data.currency}</span>
        `;
        card.appendChild(header);

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
        switchView('pricing');
        Utils.el('ticker').focus();
    }

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
            const aText = a.children[idx]?.textContent.replace(/[$,€£₹¥A]/g, '').trim() || '';
            const bText = b.children[idx]?.textContent.replace(/[$,€£₹¥A]/g, '').trim() || '';
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
