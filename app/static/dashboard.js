function generateColorPalette(count) {
    const baseColors = [
        "#FF6B6B", "#4D96FF", "#6BCB77", "#FFD93D", "#AF69EE",
        "#FF9F40", "#36A2EB", "#F9C74F", "#90BE6D", "#F8961E",
        "#9D4EDD", "#D72638", "#3F88C5", "#F49D37", "#FA7921",
        "#02C39A", "#2A9D8F", "#E63946", "#457B9D", "#8ECAE6",
        "#8338EC", "#FFBE0B", "#FB5607", "#A8DADC", "#264653"
    ];
    const shuffled = [...baseColors].sort(() => 0.5 - Math.random());
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(shuffled[i % shuffled.length]);
    }
    return colors;
}

// กำหนดสี Data Labels แบบคงที่ (static) เป็นสีดำ
const defaultDataLabelColor = "#000";

/// 📌 โหลด Pie Chart สำหรับสถานะ CM (Open / Close)
async function loadCMStatusPieChart() {
    try {
        let response = await fetch("/dashboard/api/overview_data");
        let data = await response.json();
        console.log("📊 Overview Data:", data);

        let statusCtx = document.getElementById("cm-status-pie-chart").getContext("2d");

        if (window.cmStatusChart) {
            window.cmStatusChart.destroy();
        }

        let colors = generateColorPalette(2);
        let total = data.open_cm + data.close_cm;

        window.cmStatusChart = new Chart(statusCtx, {
            type: "pie",
            data: {
                labels: ["Open", "Close"],
                datasets: [{
                    data: [data.open_cm, data.close_cm],
                    backgroundColor: colors
                }]
            },
            options: {
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                },
                responsive: true,
                responsiveAnimationDuration: 500,
                maintainAspectRatio: false,
                layout: {
                    padding: { top: 20, bottom: 20 }
                },
                plugins: {
                    legend: { position: "bottom" },
                    datalabels: {
                        formatter: (value) => {
                            let percentage = ((value / total) * 100).toFixed(1);
                            return `${percentage}%`;
                        },
                        color: defaultDataLabelColor,
                        font: { weight: "bold", size: 14 }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });
    } catch (error) {
        console.error("❌ Error fetching CM status data:", error);
        console.log("📌 Status Chart Element:", document.getElementById("cm-status-pie-chart"));

    }
}

// 📌 โหลด Pie Chart สำหรับอุปกรณ์ที่เสียบ่อยที่สุด
async function loadEquipmentFailurePieChart() {
    try {
        const equipResponse = await fetch("/dashboard/api/equipment_failure");
        const rawData = await equipResponse.json();

        const rawLabels = rawData.labels;
        const rawValues = rawData.values;

        const total = rawValues.reduce((sum, val) => sum + val, 0) || 1;
        const dynamicColors = generateColorPalette(rawLabels.length);
        const defaultDataLabelColor = "#333";

        const ctx = document.getElementById("equipment-failure-pie-chart").getContext("2d");

        if (window.equipmentFailureChart) {
            window.equipmentFailureChart.destroy();
        }

        window.equipmentFailureChart = new Chart(ctx, {
            type: "pie",
            data: {
                labels: rawLabels,
                datasets: [{
                    data: rawValues,
                    backgroundColor: dynamicColors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom" },
                    datalabels: {
                        formatter: (value, context) => {
                            const index = context.dataIndex;
                            if (index < 5) {  // เฉพาะ 5 อันดับแรก
                                const percent = ((value / total) * 100).toFixed(1);
                                return `${percent}%`;
                            }
                            return '';
                        },
                        color: defaultDataLabelColor,
                        font: { weight: "bold", size: 14 }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });

    } catch (error) {
        console.error("❌ Error fetching Equipment Failure data:", error);
    }
}

// 📌 โหลด Bar Chart สำหรับงานซ่อมที่ค้างอยู่ในแต่ละสถานที่
async function loadPendingTasksByLocationBarChart() {
    try {
        let locationResponse = await fetch("/dashboard/api/pending_tasks_location");
        let locationData = await locationResponse.json();
        console.log("📊 Location Data:", locationData);

        let locationCtx = document.getElementById("pending-tasks-by-location-bar-chart").getContext("2d");

        if (window.locationChart) {
            window.locationChart.destroy();
        }

        let colors = generateColorPalette(locationData.labels.length);

        window.locationChart = new Chart(locationCtx, {
            type: "bar",
            data: {
                labels: locationData.labels,
                datasets: [{
                    label: "งานที่ค้างอยู่",
                    data: locationData.values,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: { top: 20 }
                },
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                    datalabels: {
                        anchor: 'end',
                        align: 'right',
                        formatter: (value) => value,
                        color: defaultDataLabelColor,
                        font: { weight: 'bold', size: 14 }
                    }
                },
                scales: {
                    x: { 
                        beginAtZero: true, 
                        suggestedMax: Math.max(...locationData.values) * 1.2,
                        ticks: { stepSize: 1, precision: 0 }
                    },
                    y: { 
                        beginAtZero: true, 
                        ticks: { stepSize: 1, precision: 0 }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });
    } catch (error) {
        console.error("❌ Error fetching Pending Tasks data:", error);
    }
}

// 📌 โหลด Bar Chart สำหรับงาน CM ตาม Line
async function loadCMByLineBarChart() {
    try {
        let lineResponse = await fetch("/dashboard/api/cm_by_line");
        let lineData = await lineResponse.json();
        console.log("📊 CM by Line Data:", lineData);

        let lineCtx = document.getElementById("cm-by-line-bar-chart").getContext("2d");

        if (window.lineChart) {
            window.lineChart.destroy();
        }

        let colors = generateColorPalette(lineData.labels.length);

        window.lineChart = new Chart(lineCtx, {
            type: "bar",
            data: {
                labels: lineData.labels,
                datasets: [{
                    label: "จำนวนงาน CM",
                    data: lineData.values,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: { top: 20 }
                },
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                    datalabels: {
                        anchor: 'end',
                        align: 'right',
                        formatter: (value) => value,
                        color: defaultDataLabelColor,
                        font: { weight: 'bold', size: 14 }
                    }
                },
                scales: {
                    x: { 
                        beginAtZero: true, 
                        suggestedMax: Math.max(...lineData.values) * 1.2,
                        ticks: { stepSize: 1, precision: 0 }
                    },
                    y: { 
                        beginAtZero: true, 
                        ticks: { stepSize: 1, precision: 0 }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });
    } catch (error) {
        console.error("❌ Error fetching CM by Line data:", error);
    }
}

// 📌 โหลดข้อมูลสรุปงาน CM
async function loadCMOverviewData() {
    try {
        let response = await fetch("/dashboard/api/overview_data");
        let data = await response.json();
        console.log("📊 Overview Data:", data);

        document.getElementById("total_cm").innerText = data.total_cm;
        document.getElementById("open_cm").innerText = data.open_cm;
        document.getElementById("close_cm").innerText = data.close_cm;
    } catch (error) {
        console.error("❌ Error fetching overview data:", error);
    }
}

// เรียกใช้งานเมื่อโหลดหน้า
document.addEventListener("DOMContentLoaded", () => {
    loadCMOverviewData();
    loadCMStatusPieChart();
    loadEquipmentFailurePieChart();
    loadPendingTasksByLocationBarChart();
    loadCMByLineBarChart();
});
