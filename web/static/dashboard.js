/**
 * S&P 500 Iron Condor Trading Bot Dashboard
 * JavaScript for interactive dashboard
 */

// WebSocket connection
let socket = null;
let priceChart = null;
const priceHistory = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    initializeWebSocket();
    initializeChart();
    refreshData();
    checkHealth();
});

/**
 * Initialize WebSocket connection
 */
function initializeWebSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('WebSocket connected');
        document.getElementById('streamingStatus').classList.add('active');
    });

    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        document.getElementById('streamingStatus').classList.remove('active');
    });

    socket.on('price_update', (data) => {
        updatePrice(data.price);
    });

    socket.on('market_update', (data) => {
        updatePrice(data.price);
    });
}

/**
 * Initialize price chart
 */
function initializeChart() {
    const ctx = document.getElementById('priceChart').getContext('2d');

    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'S&P 500 Price',
                data: [],
                borderColor: '#2E86AB',
                backgroundColor: 'rgba(46, 134, 171, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#eee'
                    }
                }
            },
            scales: {
                y: {
                    ticks: { color: '#eee' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                x: {
                    ticks: { color: '#eee' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                }
            }
        }
    });
}

/**
 * Update price display and chart
 */
function updatePrice(price) {
    // Update display
    document.getElementById('currentPrice').textContent = `$${price.toFixed(2)}`;
    document.getElementById('spPrice').textContent = `$${price.toFixed(2)}`;

    // Update chart
    const now = new Date().toLocaleTimeString();
    priceHistory.push({ time: now, price: price });

    // Keep last 50 points
    if (priceHistory.length > 50) {
        priceHistory.shift();
    }

    priceChart.data.labels = priceHistory.map(p => p.time);
    priceChart.data.datasets[0].data = priceHistory.map(p => p.price);
    priceChart.update('none'); // Update without animation for performance
}

/**
 * Check system health
 */
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.ml_trained) {
            document.getElementById('mlStatus').classList.add('active');
        }

        if (data.streaming) {
            document.getElementById('streamingStatus').classList.add('active');
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

/**
 * Refresh all dashboard data
 */
async function refreshData() {
    await Promise.all([
        loadMarketData(),
        loadPortfolioSummary(),
        loadOpenPositions()
    ]);
}

/**
 * Load current market data
 */
async function loadMarketData() {
    try {
        const response = await fetch('/api/market/current');
        const data = await response.json();

        // Update market data
        document.getElementById('spPrice').textContent = `$${data.price.toFixed(2)}`;
        document.getElementById('currentPrice').textContent = `$${data.price.toFixed(2)}`;
        document.getElementById('volatility').textContent = `${(data.volatility.current_volatility * 100).toFixed(2)}%`;
        document.getElementById('volRegime').textContent = data.volatility.volatility_regime;
        document.getElementById('high52w').textContent = `$${data.stats.max_price.toFixed(2)}`;
        document.getElementById('low52w').textContent = `$${data.stats.min_price.toFixed(2)}`;

        // Color code volatility regime
        const regime = data.volatility.volatility_regime;
        const regimeEl = document.getElementById('volRegime');
        regimeEl.className = 'metric-value';
        if (regime === 'LOW') regimeEl.classList.add('positive');
        else if (regime === 'HIGH') regimeEl.classList.add('negative');

    } catch (error) {
        console.error('Error loading market data:', error);
    }
}

/**
 * Analyze Iron Condor strategy
 */
async function analyzeStrategy() {
    try {
        showLoading('Analyzing strategy...');

        const response = await fetch('/api/strategy/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ days_to_expiration: 45 })
        });

        const data = await response.json();

        // Update strategy display
        document.getElementById('longPut').textContent = `$${data.strikes.long_put.toFixed(0)}`;
        document.getElementById('shortPut').textContent = `$${data.strikes.short_put.toFixed(0)}`;
        document.getElementById('shortCall').textContent = `$${data.strikes.short_call.toFixed(0)}`;
        document.getElementById('longCall').textContent = `$${data.strikes.long_call.toFixed(0)}`;
        document.getElementById('maxProfit').textContent = `$${data.profit_loss.max_profit.toFixed(2)}`;
        document.getElementById('maxLoss').textContent = `$${data.profit_loss.max_loss.toFixed(2)}`;
        document.getElementById('pop').textContent = `${data.probability.probability_of_profit.toFixed(2)}%`;

        // Show ML predictions if available
        if (data.ml_predictions) {
            displayMLPredictions(data.ml_predictions);
        }

        hideLoading();
        showNotification('Strategy analysis complete!', 'success');

    } catch (error) {
        console.error('Error analyzing strategy:', error);
        hideLoading();
        showNotification('Error analyzing strategy', 'error');
    }
}

/**
 * Display ML predictions
 */
function displayMLPredictions(predictions) {
    const card = document.getElementById('mlPredictionsCard');
    card.style.display = 'block';

    const price = predictions.price_prediction;
    const vol = predictions.volatility_forecast;
    const rec = predictions.recommendation;

    // Price predictions
    document.getElementById('predictedDirection').textContent =
        price.direction.toUpperCase();
    document.getElementById('predictedPrice').textContent =
        `$${price.predicted_price.toFixed(2)}`;
    document.getElementById('priceChange').textContent =
        `${price.price_change > 0 ? '+' : ''}${price.price_change.toFixed(2)} (${price.price_change_percent.toFixed(2)}%)`;

    // Volatility forecast
    document.getElementById('forecastedVol').textContent =
        `${(vol.forecasted_volatility * 100).toFixed(2)}%`;

    // Recommendation
    document.getElementById('recommendation').textContent = rec.action;
    document.getElementById('mlConfidence').textContent =
        `${(rec.confidence * 100).toFixed(0)}% Confidence`;

    // Confidence bar
    document.getElementById('confidenceBar').style.width =
        `${rec.confidence * 100}%`;

    // Recommendation text
    document.getElementById('recommendationText').textContent =
        rec.rationale.join('. ');

    // Color code recommendation
    const recEl = document.getElementById('recommendation');
    recEl.className = 'metric-value';
    if (rec.action === 'ENTER') recEl.classList.add('positive');
    else if (rec.action === 'AVOID') recEl.classList.add('negative');
}

/**
 * Train ML models
 */
async function trainMLModels() {
    try {
        showLoading('Training ML models... This may take a few minutes.');

        const response = await fetch('/api/ml/train', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        hideLoading();
        showNotification('ML models trained successfully!', 'success');
        document.getElementById('mlStatus').classList.add('active');

    } catch (error) {
        console.error('Error training ML models:', error);
        hideLoading();
        showNotification('Error training ML models', 'error');
    }
}

/**
 * Start real-time streaming
 */
async function startStreaming() {
    try {
        const response = await fetch('/api/streaming/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ demo: true }) // Use demo mode
        });

        const data = await response.json();
        showNotification('Real-time streaming started', 'success');
        document.getElementById('streamingStatus').classList.add('active');

    } catch (error) {
        console.error('Error starting streaming:', error);
        showNotification('Error starting streaming', 'error');
    }
}

/**
 * Stop real-time streaming
 */
async function stopStreaming() {
    try {
        const response = await fetch('/api/streaming/stop', {
            method: 'POST'
        });

        const data = await response.json();
        showNotification('Real-time streaming stopped', 'info');
        document.getElementById('streamingStatus').classList.remove('active');

    } catch (error) {
        console.error('Error stopping streaming:', error);
    }
}

/**
 * Load portfolio summary
 */
async function loadPortfolioSummary() {
    try {
        const response = await fetch('/api/portfolio/summary');
        const data = await response.json();

        document.getElementById('openPositions').textContent = data.open_positions;
        document.getElementById('totalPositions').textContent = data.total_positions;

        const unrealized = document.getElementById('unrealizedPnl');
        unrealized.textContent = `$${data.total_unrealized_pnl.toFixed(2)}`;
        unrealized.className = 'metric-value';
        if (data.total_unrealized_pnl > 0) unrealized.classList.add('positive');
        else if (data.total_unrealized_pnl < 0) unrealized.classList.add('negative');

        const realized = document.getElementById('realizedPnl');
        realized.textContent = `$${data.total_realized_pnl.toFixed(2)}`;
        realized.className = 'metric-value';
        if (data.total_realized_pnl > 0) realized.classList.add('positive');
        else if (data.total_realized_pnl < 0) realized.classList.add('negative');

        const total = document.getElementById('totalPnl');
        total.textContent = `$${data.total_pnl.toFixed(2)}`;
        total.className = 'metric-value';
        if (data.total_pnl > 0) total.classList.add('positive');
        else if (data.total_pnl < 0) total.classList.add('negative');

        document.getElementById('winRate').textContent = `${data.win_rate.toFixed(1)}%`;

    } catch (error) {
        console.error('Error loading portfolio summary:', error);
    }
}

/**
 * Load open positions
 */
async function loadOpenPositions() {
    try {
        const response = await fetch('/api/positions/open');
        const data = await response.json();

        const container = document.getElementById('positionsContainer');

        if (data.positions.length === 0) {
            container.innerHTML = '<p style="text-align:center; padding:20px;">No open positions</p>';
            return;
        }

        // Create table
        let html = '<table class="positions-table"><thead><tr>';
        html += '<th>ID</th><th>Entry Date</th><th>DTE</th><th>Entry Price</th>';
        html += '<th>Current Price</th><th>P&L</th><th>Actions</th>';
        html += '</tr></thead><tbody>';

        data.positions.forEach(pos => {
            const pnlClass = pos.current.pnl >= 0 ? 'positive' : 'negative';
            html += `<tr>
                <td>${pos.id}</td>
                <td>${new Date(pos.entry_date).toLocaleDateString()}</td>
                <td>${pos.days_to_expiration}</td>
                <td>$${pos.underlying_price_at_entry.toFixed(2)}</td>
                <td>$${pos.current.underlying_price ? pos.current.underlying_price.toFixed(2) : '--'}</td>
                <td class="${pnlClass}">$${pos.current.pnl.toFixed(2)} (${pos.current.pnl_percent.toFixed(1)}%)</td>
                <td><button class="btn btn-danger" onclick="closePosition(${pos.id})">Close</button></td>
            </tr>`;
        });

        html += '</tbody></table>';
        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading positions:', error);
        document.getElementById('positionsContainer').innerHTML =
            '<p style="text-align:center; padding:20px; color:#e74c3c;">Error loading positions</p>';
    }
}

/**
 * Close a position
 */
async function closePosition(positionId) {
    if (!confirm('Are you sure you want to close this position?')) {
        return;
    }

    try {
        const response = await fetch(`/api/positions/${positionId}/close`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();
        showNotification('Position closed successfully', 'success');
        await loadOpenPositions();
        await loadPortfolioSummary();

    } catch (error) {
        console.error('Error closing position:', error);
        showNotification('Error closing position', 'error');
    }
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Loading...') {
    // Simple console log for now
    console.log(message);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    console.log('Loading complete');
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message); // Simple alert for now
}

// Auto-refresh every 30 seconds
setInterval(() => {
    if (!document.getElementById('streamingStatus').classList.contains('active')) {
        loadMarketData();
        loadPortfolioSummary();
    }
}, 30000);
