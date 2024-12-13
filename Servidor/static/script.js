let charts = {};
let dateRange;
let socket;
let latestData = {1: null, 2: null, 3: null, 4: null};

document.addEventListener('DOMContentLoaded', function() {
    dateRange = flatpickr("#date-range", {
        mode: "range",
        dateFormat: "Y-m-d H:i",
        defaultDate: [new Date(Date.now() - 24*60*60*1000), new Date()],
        enableTime: true,
    });

    document.getElementById('update-btn').addEventListener('click', updateCharts);

    updateCharts();
    initSocket();
});

function initSocket() {
    socket = io();
    socket.on('new_data', function(data) {
        updateDataList([data]);
        updateChartsWithNewData(data);
    });
}

function updateCharts() {
    const [start, end] = dateRange.selectedDates;
    const url = `/api/data?start_date=${start.toISOString()}&end_date=${end.toISOString()}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const nodeData = processData(data);
            createOrUpdateChart('tempChart', createTempChart, nodeData);
            createOrUpdateChart('humidityChart', createHumidityChart, nodeData);
            updateNodeCharts(nodeData);
            updateDataList(data);
        });
}

function updateChartsWithNewData(newData) {
    latestData[newData.node_number] = newData;
    updateNodeCharts(latestData);
}

function createOrUpdateChart(chartId, createFunction, data) {
    if (charts[chartId]) {
        charts[chartId].destroy();
    }
    charts[chartId] = createFunction(data);
}

function processData(data) {
    const nodeData = {1: [], 2: [], 3: [], 4: []};
    data.forEach(item => {
        if (nodeData[item.node_number]) {
            nodeData[item.node_number].push(item);
        }
    });
    return nodeData;
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);

    // Asegurarse de que la hora se muestra en UTC
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
        timeZone: 'UTC'
    });
}

function createTempChart(nodeData) {
    const ctx = document.getElementById('tempChart').getContext('2d');
    const labels = Object.values(nodeData).map(data => data[0]?.name || 'Desconocido');
    const avgTemps = Object.values(nodeData).map(data => {
        const sum = data.reduce((acc, item) => acc + parseFloat(item.temperature), 0);
        return (sum / data.length || 0).toFixed(2);
    });

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Temperatura Promedio (°C)',
                data: avgTemps,
                backgroundColor: ['rgba(255, 99, 132, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(255, 206, 86, 0.8)', 'rgba(75, 192, 192, 0.8)'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: false }
            }
        }
    });
}

function createHumidityChart(nodeData) {
    const ctx = document.getElementById('humidityChart').getContext('2d');
    const labels = Object.values(nodeData).map(data => data[0]?.name || 'Desconocido');
    const avgHumidity = Object.values(nodeData).map(data => {
        const sum = data.reduce((acc, item) => acc + parseFloat(item.humidity), 0);
        return (sum / data.length || 0).toFixed(2);
    });

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Humedad Promedio (%)',
                data: avgHumidity,
                backgroundColor: ['rgba(255, 99, 132, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(255, 206, 86, 0.8)', 'rgba(75, 192, 192, 0.8)'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: false }
            }
        }
    });
}

function updateNodeCharts(nodeData) {
    for (let node = 1; node <= 4; node++) {
        if (nodeData[node] && nodeData[node].length > 0) {
            const nodeName = nodeData[node][0].name;
            document.getElementById(`titleNode${node}`).textContent = `Nodo ${node} - ${nodeName} (Temperatura)`;
            document.getElementById(`titleHumNode${node}`).textContent = `Nodo ${node} - ${nodeName} (Humedad)`;
            createOrUpdateChart(`tempChartNode${node}`, createNodeTempChart, {node, data: nodeData[node]});
            createOrUpdateChart(`humidityChartNode${node}`, createNodeHumidityChart, {node, data: nodeData[node]});
        }
    }
}

function createNodeTempChart({node, data}) {
    const ctx = document.getElementById(`tempChartNode${node}`).getContext('2d');
    const temperatures = data.map(item => parseFloat(item.temperature));
    const timestamps = data.map(item => formatTimestamp(item.timestamp));

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [{
                label: `Temperatura (°C)`,
                data: temperatures,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: false }
            },
            scales: { 
                y: { beginAtZero: false },
                x: {
                    ticks: {
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 6
                    }
                }
            }
        }
    });
}

function createNodeHumidityChart({node, data}) {
    const ctx = document.getElementById(`humidityChartNode${node}`).getContext('2d');
    const humidity = data.map(item => parseFloat(item.humidity));
    const timestamps = data.map(item => formatTimestamp(item.timestamp));

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [{
                label: `Humedad (%)`,
                data: humidity,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: false }
            },
            scales: { 
                y: { beginAtZero: false },
                x: {
                    ticks: {
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 6
                    }
                }
            }
        }
    });
}

function updateDataList(data) {
    const dataList = document.getElementById('data-list');
    data.slice(0, 10).forEach(item => {
        const li = document.createElement('li');
        const formattedTime = formatTimestamp(item.timestamp);
        li.textContent = `${item.name} (Nodo ${item.node_number}): Temp: ${item.temperature}°C, Humedad: ${item.humidity}%, Tiempo: ${formattedTime}`;
        dataList.insertBefore(li, dataList.firstChild);
        if (dataList.children.length > 10) {
            dataList.removeChild(dataList.lastChild);
        }
    });
}


