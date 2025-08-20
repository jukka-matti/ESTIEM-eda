/**
 * ESTIEM EDA Toolkit - Web Application
 * Browser-based exploratory data analysis with Pyodide
 */

// Global variables
let pyodide = null;
let currentData = null;
let analysisResults = null;
let isInitialized = false;

// Initialize application when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

/**
 * Initialize Pyodide and Python environment
 */
async function initializeApp() {
    try {
        showLoading('Initializing Python Environment...', 'Loading scientific computing libraries');
        updateProgress(10);
        
        // Load Pyodide
        pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
        });
        updateProgress(30);
        
        // Install required packages (no pandas needed!)
        showLoading('Installing Packages...', 'Loading NumPy, SciPy');
        await pyodide.loadPackage(['numpy', 'scipy']);
        updateProgress(60);
        
        // Load our statistical tools
        showLoading('Loading ESTIEM Tools...', 'Preparing exploratory data analysis functions');
        const response = await fetch('eda_tools.py');
        const pythonCode = await response.text();
        pyodide.runPython(pythonCode);
        updateProgress(90);
        
        isInitialized = true;
        updateProgress(100);
        
        setTimeout(() => {
            hideLoading();
            showWelcomeMessage();
        }, 500);
        
        console.log('SUCCESS: ESTIEM EDA Toolkit ready');
        
    } catch (error) {
        console.error('ERROR: Initialization failed:', error);
        showError('Failed to initialize. Please refresh the page.', error.message);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    // File upload handling
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFileUpload(e.dataTransfer.files[0]);
    });
    
    fileInput.addEventListener('change', (e) => {
        handleFileUpload(e.target.files[0]);
    });
    
    // Modal event listeners
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

/**
 * Handle file upload
 */
function handleFileUpload(file) {
    if (!file) return;
    
    if (!file.name.toLowerCase().endsWith('.csv')) {
        showError('Invalid file type', 'Please upload a CSV file (.csv)');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        showError('File too large', 'Please upload a file smaller than 10MB');
        return;
    }
    
    showLoading('Reading CSV file...', 'Processing your data');
    
    Papa.parse(file, {
        complete: function(results) {
            hideLoading();
            if (results.errors.length > 0) {
                console.warn('CSV parsing warnings:', results.errors);
            }
            
            currentData = {
                data: results.data,
                headers: results.meta.fields || Object.keys(results.data[0] || {}),
                filename: file.name
            };
            
            displayDataPreview();
            showTools();
        },
        error: function(error) {
            hideLoading();
            showError('Failed to read CSV', error.message);
        },
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim()
    });
}

/**
 * Load sample data
 */
async function loadSampleData(type) {
    if (!isInitialized) {
        showError('Please wait', 'Application is still initializing...');
        return;
    }
    
    showLoading('Loading sample data...', 'Generating realistic dataset');
    
    try {
        // Generate sample data using Python
        pyodide.globals.set('sample_type', type);
        const pythonCode = `
import json
sample_data = generate_sample_data('${type}')
json.dumps(sample_data)
        `;
        
        const result = pyodide.runPython(pythonCode);
        const sampleData = JSON.parse(result);
        
        currentData = {
            data: sampleData.data,
            headers: sampleData.headers,
            filename: sampleData.filename
        };
        
        hideLoading();
        displayDataPreview();
        showTools();
        
    } catch (error) {
        hideLoading();
        showError('Failed to load sample data', error.message);
    }
}

/**
 * Display data preview
 */
function displayDataPreview() {
    const previewSection = document.getElementById('dataPreview');
    const tableContainer = document.getElementById('dataTable');
    const dataSizeElement = document.getElementById('dataSize');
    
    if (!currentData || !currentData.data.length) return;
    
    const data = currentData.data;
    const headers = currentData.headers;
    
    // Create preview table (first 5 rows)
    const previewData = data.slice(0, 5);
    let tableHTML = '<table class="data-table"><thead><tr>';
    
    headers.forEach(header => {
        tableHTML += `<th>${escapeHtml(header)}</th>`;
    });
    tableHTML += '</tr></thead><tbody>';
    
    previewData.forEach(row => {
        tableHTML += '<tr>';
        headers.forEach(header => {
            const value = row[header];
            const displayValue = value !== null && value !== undefined ? 
                (typeof value === 'number' ? value.toFixed(3) : String(value)) : '';
            tableHTML += `<td>${escapeHtml(displayValue)}</td>`;
        });
        tableHTML += '</tr>';
    });
    
    tableHTML += '</tbody></table>';
    tableContainer.innerHTML = tableHTML;
    
    // Update data info
    dataSizeElement.textContent = `${data.length} rows × ${headers.length} columns`;
    
    previewSection.style.display = 'block';
    previewSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Show analysis tools
 */
function showTools() {
    const toolsSection = document.getElementById('toolsSection');
    toolsSection.style.display = 'block';
    toolsSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Run analysis
 */
async function runAnalysis(analysisType) {
    if (!isInitialized) {
        showError('Please wait', 'Application is still initializing...');
        return;
    }
    
    if (!currentData) {
        showError('No data loaded', 'Please upload a CSV file first');
        return;
    }
    
    // Show parameter modal for analyses that need parameters
    if (['capability', 'anova'].includes(analysisType)) {
        showParameterModal(analysisType);
        return;
    }
    
    await executeAnalysis(analysisType, {});
}

/**
 * Show parameter input modal
 */
function showParameterModal(analysisType) {
    const modal = document.getElementById('parameterModal');
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');
    const runBtn = document.getElementById('runAnalysisBtn');
    
    title.textContent = getAnalysisTitle(analysisType) + ' - Parameters';
    
    let formHTML = '';
    
    if (analysisType === 'capability') {
        formHTML = `
            <div class="form-group">
                <label for="lsl">Lower Specification Limit (LSL):</label>
                <input type="number" id="lsl" step="any" placeholder="e.g. 9.5" required>
            </div>
            <div class="form-group">
                <label for="usl">Upper Specification Limit (USL):</label>
                <input type="number" id="usl" step="any" placeholder="e.g. 10.5" required>
            </div>
            <div class="form-group">
                <label for="target">Target Value (optional):</label>
                <input type="number" id="target" step="any" placeholder="e.g. 10.0">
            </div>
        `;
    } else if (analysisType === 'anova') {
        const numericColumns = currentData.headers.filter(header => {
            return currentData.data.some(row => typeof row[header] === 'number');
        });
        
        const categoricalColumns = currentData.headers.filter(header => {
            return currentData.data.some(row => typeof row[header] === 'string');
        });
        
        formHTML = `
            <div class="form-group">
                <label for="valueColumn">Value Column:</label>
                <select id="valueColumn" required>
                    <option value="">Select column...</option>
                    ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label for="groupColumn">Group Column:</label>
                <select id="groupColumn" required>
                    <option value="">Select column...</option>
                    ${categoricalColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                </select>
            </div>
        `;
    }
    
    body.innerHTML = formHTML;
    
    // Setup run button
    runBtn.onclick = () => {
        const params = collectParameters(analysisType);
        if (params) {
            closeModal();
            executeAnalysis(analysisType, params);
        }
    };
    
    modal.style.display = 'flex';
}

/**
 * Collect parameters from modal
 */
function collectParameters(analysisType) {
    if (analysisType === 'capability') {
        const lsl = parseFloat(document.getElementById('lsl').value);
        const usl = parseFloat(document.getElementById('usl').value);
        const target = document.getElementById('target').value ? 
            parseFloat(document.getElementById('target').value) : null;
        
        if (isNaN(lsl) || isNaN(usl)) {
            showError('Invalid parameters', 'Please enter valid LSL and USL values');
            return null;
        }
        
        if (lsl >= usl) {
            showError('Invalid parameters', 'LSL must be less than USL');
            return null;
        }
        
        return { lsl, usl, target };
    } else if (analysisType === 'anova') {
        const valueColumn = document.getElementById('valueColumn').value;
        const groupColumn = document.getElementById('groupColumn').value;
        
        if (!valueColumn || !groupColumn) {
            showError('Missing parameters', 'Please select both value and group columns');
            return null;
        }
        
        return { valueColumn, groupColumn };
    }
    
    return {};
}

/**
 * Execute analysis
 */
async function executeAnalysis(analysisType, parameters) {
    const analysisTitle = getAnalysisTitle(analysisType);
    showLoading(`Running ${analysisTitle}...`, 'Performing statistical calculations');
    
    try {
        // Prepare data for Python
        pyodide.globals.set('js_data', currentData.data);
        pyodide.globals.set('js_headers', currentData.headers);
        pyodide.globals.set('js_params', parameters);
        
        // Run analysis
        const pythonCode = `
import json
result = run_analysis('${analysisType}', js_data, js_headers, js_params)
json.dumps(result)
        `;
        
        const result = pyodide.runPython(pythonCode);
        analysisResults = JSON.parse(result);
        
        hideLoading();
        displayResults(analysisType, analysisResults);
        
    } catch (error) {
        hideLoading();
        console.error('Analysis error:', error);
        showError('Analysis failed', error.message);
    }
}

/**
 * Display analysis results
 */
function displayResults(analysisType, results) {
    const resultsSection = document.getElementById('resultsSection');
    const analysisTitle = document.getElementById('analysisTitle');
    const chartContainer = document.getElementById('chartContainer');
    const statsContainer = document.getElementById('statsContainer');
    const interpretationContainer = document.getElementById('interpretationContainer');
    
    analysisTitle.textContent = getAnalysisTitle(analysisType) + ' Results';
    
    // Display chart
    if (results.chart_data) {
        const chartData = JSON.parse(results.chart_data);
        Plotly.newPlot(chartContainer, chartData.data, chartData.layout, {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
        });
    }
    
    // Display statistics
    if (results.statistics) {
        displayStatistics(results.statistics);
    }
    
    // Display interpretation
    if (results.interpretation) {
        displayInterpretation(results.interpretation);
    }
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Display statistics table
 */
function displayStatistics(stats) {
    const container = document.getElementById('statsContainer');
    
    let html = '<table class="stats-table">';
    for (const [key, value] of Object.entries(stats)) {
        const label = formatLabel(key);
        const formattedValue = formatValue(value);
        html += `
            <tr>
                <td class="stat-label">${label}</td>
                <td class="stat-value">${formattedValue}</td>
            </tr>
        `;
    }
    html += '</table>';
    
    container.innerHTML = html;
}

/**
 * Display interpretation
 */
function displayInterpretation(interpretation) {
    const container = document.getElementById('interpretationContainer');
    
    container.innerHTML = `
        <div class="interpretation-content">
            <p>${interpretation}</p>
            <div class="learn-more">
                <p><strong>Want to learn more?</strong></p>
                <a href="https://estiem.org/leansixsigma" target="_blank" class="learn-link">
                    Take ESTIEM's Lean Six Sigma Course
                </a>
            </div>
        </div>
    `;
}

/**
 * Download chart as PNG
 */
function downloadChart() {
    if (!analysisResults) return;
    
    Plotly.downloadImage('chartContainer', {
        format: 'png',
        width: 1200,
        height: 800,
        filename: `estiem_eda_${analysisResults.analysis_type || 'analysis'}_${new Date().getTime()}`
    });
}

/**
 * Download report as HTML
 */
function downloadReport() {
    if (!analysisResults) return;
    
    const reportHTML = generateHTMLReport();
    const blob = new Blob([reportHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ESTIEM_EDA_Report_${new Date().getTime()}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Generate HTML report
 */
function generateHTMLReport() {
    const timestamp = new Date().toLocaleString();
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESTIEM EDA Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .stats-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .stats-table td { padding: 8px; border-bottom: 1px solid #ddd; }
        .interpretation { background: #f0f8ff; padding: 20px; margin: 20px 0; border-left: 4px solid #0066cc; }
        .footer { margin-top: 40px; text-align: center; font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ESTIEM EDA Analysis Report</h1>
        <p>Generated on ${timestamp}</p>
        <p>Data: ${currentData.filename}</p>
    </div>
    
    <div id="chart"></div>
    
    <h2>Statistical Summary</h2>
    <table class="stats-table">
        ${Object.entries(analysisResults.statistics || {}).map(([key, value]) => `
            <tr>
                <td><strong>${formatLabel(key)}</strong></td>
                <td>${formatValue(value)}</td>
            </tr>
        `).join('')}
    </table>
    
    <h2>Interpretation</h2>
    <div class="interpretation">
        <p>${analysisResults.interpretation || 'No interpretation available'}</p>
    </div>
    
    <div class="footer">
        <p>Generated by <strong>ESTIEM EDA Toolkit</strong> - <a href="https://estiem.github.io/eda-toolkit">https://estiem.github.io/eda-toolkit</a></p>
        <p>ESTIEM - Connecting 60,000+ Industrial Engineering students across Europe</p>
    </div>
    
    <script>
        // Embed chart data
        const chartData = ${analysisResults.chart_data};
        Plotly.newPlot('chart', chartData.data, chartData.layout);
    </script>
</body>
</html>
    `;
}

/**
 * Share results
 */
function shareResults() {
    // Create shareable URL with compressed data
    const shareData = {
        analysis: analysisResults.analysis_type,
        timestamp: new Date().getTime()
    };
    
    const shareUrl = `${window.location.origin}${window.location.pathname}?share=${btoa(JSON.stringify(shareData))}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'ESTIEM EDA Analysis Results',
            text: 'Check out my exploratory data analysis results!',
            url: shareUrl
        });
    } else {
        navigator.clipboard.writeText(shareUrl).then(() => {
            showSuccess('Share link copied to clipboard!');
        }).catch(() => {
            prompt('Copy this link to share:', shareUrl);
        });
    }
}

/**
 * Utility functions
 */

function scrollToUpload() {
    document.getElementById('uploadSection').scrollIntoView({ behavior: 'smooth' });
}

function scrollToTools() {
    document.getElementById('toolsSection').scrollIntoView({ behavior: 'smooth' });
}

function loadDemo() {
    loadSampleData('manufacturing');
}

function closeModal() {
    document.getElementById('parameterModal').style.display = 'none';
}

function showFullData() {
    // Implementation for showing full data in modal
    console.log('Show full data - to be implemented');
}

function showLoading(title, message) {
    const overlay = document.getElementById('loadingOverlay');
    document.getElementById('loadingTitle').textContent = title;
    document.getElementById('loadingMessage').textContent = message;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function updateProgress(percent) {
    document.getElementById('progressFill').style.width = `${percent}%`;
}

function showError(title, message) {
    hideLoading();
    alert(`${title}\n\n${message}`); // TODO: Replace with nicer modal
}

function showSuccess(message) {
    // TODO: Replace with nicer notification
    console.log('SUCCESS:', message);
}

function showWelcomeMessage() {
    console.log('Welcome to ESTIEM EDA Toolkit!');
}

function getAnalysisTitle(type) {
    const titles = {
        'i_chart': 'Individual Control Chart',
        'capability': 'Process Capability Analysis',
        'anova': 'Analysis of Variance (ANOVA)',
        'pareto': 'Pareto Analysis',
        'probability_plot': 'Probability Plot'
    };
    return titles[type] || 'Exploratory Data Analysis';
}

function formatLabel(key) {
    return key
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
        .replace(/Cp([k]?)\b/g, 'Cp$1')
        .replace(/Ucl/g, 'UCL')
        .replace(/Lcl/g, 'LCL')
        .replace(/Ppm/g, 'PPM');
}

function formatValue(value) {
    if (typeof value === 'number') {
        if (Number.isInteger(value)) {
            return value.toString();
        } else {
            return value.toFixed(4);
        }
    }
    return String(value);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

// Handle shared results on page load
window.addEventListener('load', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const shareData = urlParams.get('share');
    
    if (shareData) {
        try {
            const shared = JSON.parse(atob(shareData));
            console.log('Loading shared analysis:', shared);
            // TODO: Load shared analysis
        } catch (error) {
            console.warn('Invalid share data:', error);
        }
    }
});