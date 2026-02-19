/* ============================================================
   API Communication Layer
   ============================================================ */

const API = {
    BASE_URL: '/api',

    async _fetch(endpoint, params = {}) {
        const url = new URL(this.BASE_URL + endpoint, window.location.origin);
        Object.entries(params).forEach(([k, v]) => {
            if (v != null && v !== '') url.searchParams.set(k, v);
        });

        const response = await fetch(url.toString());
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `Request failed with status ${response.status}`);
        }

        return data;
    },

    async getMarketData(ticker, period = '1y') {
        return this._fetch('/market_data', { ticker, period });
    },

    async priceOption(ticker, optionType, strike, daysToExpiry) {
        return this._fetch('/price_option', {
            ticker,
            option_type: optionType,
            strike: strike || undefined,
            days_to_expiry: daysToExpiry,
        });
    },

    async getOptionsChain(ticker, expiry) {
        return this._fetch('/options_chain', { ticker, expiry: expiry || undefined });
    },

    async getExpiries(ticker) {
        return this._fetch('/options_chain', { ticker, only_expiries: 'true' });
    },

    async getExchangeRate(source, target) {
        return this._fetch('/exchange_rate', { source, target });
    },
};
