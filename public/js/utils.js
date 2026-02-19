/* ============================================================
   Utility Functions
   ============================================================ */

const Utils = {
    formatCurrency(value, sentCurrency = '$', decimals = 2) {
        if (value == null || isNaN(value)) return 'N/A';
        return sentCurrency + Number(value).toFixed(decimals);
    },

    formatPercent(value, decimals = 2) {
        if (value == null || isNaN(value)) return 'N/A';
        return (Number(value) * 100).toFixed(decimals) + '%';
    },

    formatNumber(value, decimals = 4) {
        if (value == null || isNaN(value)) return 'N/A';
        return Number(value).toFixed(decimals);
    },

    formatVolume(value) {
        if (value == null || isNaN(value)) return 'N/A';
        const n = Number(value);
        if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
        if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
        if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
        return n.toLocaleString();
    },

    formatMarketCap(value) {
        if (value == null || isNaN(value)) return 'N/A';
        const n = Number(value);
        if (n >= 1e12) return '$' + (n / 1e12).toFixed(2) + 'T';
        if (n >= 1e9) return '$' + (n / 1e9).toFixed(2) + 'B';
        if (n >= 1e6) return '$' + (n / 1e6).toFixed(2) + 'M';
        return '$' + n.toLocaleString();
    },

    el(id) {
        return document.getElementById(id);
    },

    qs(selector, parent) {
        return (parent || document).querySelector(selector);
    },

    qsa(selector, parent) {
        return (parent || document).querySelectorAll(selector);
    },

    createDataItem(label, value, className) {
        const div = document.createElement('div');
        div.className = 'data-item';
        div.innerHTML = `
            <span class="data-label">${label}</span>
            <span class="data-value ${className || ''}">${value}</span>
        `;
        return div;
    },

    setLoading(button, loading) {
        const text = button.querySelector('.btn-text');
        const loader = button.querySelector('.btn-loader');
        if (loading) {
            text.style.display = 'none';
            loader.style.display = 'inline-block';
            button.disabled = true;
        } else {
            text.style.display = 'inline';
            loader.style.display = 'none';
            button.disabled = false;
        }
    },

    showError(panelId, msgId, message) {
        const panel = Utils.el(panelId);
        const msg = Utils.el(msgId);
        panel.style.display = 'block';
        msg.textContent = message;
    },

    hideError(panelId) {
        Utils.el(panelId).style.display = 'none';
    },
};
