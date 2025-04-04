function generateColorPalette(count) {
    const baseColors = [
        "#FF6B6B", "#4D96FF", "#6BCB77", "#FFD93D", "#AF69EE",
        "#FF9F40", "#36A2EB", "#F9C74F", "#90BE6D", "#F8961E",
        "#9D4EDD", "#D72638", "#3F88C5", "#F49D37", "#FA7921",
        "#02C39A", "#2A9D8F", "#E63946", "#457B9D", "#8ECAE6",
        "#8338EC", "#FFBE0B", "#FB5607", "#A8DADC", "#264653",
        "#E76F51", "#6A994E", "#B5838D", "#C9A227", "#EE6C4D"
    ];

    let colors = [];

    // 🔁 เติมจาก baseColors แบบไม่ซ้ำก่อน
    for (let i = 0; i < count; i++) {
        if (i < baseColors.length) {
            colors.push(baseColors[i]);
        } else {
            // 🔄 ถ้าเกินแล้ว ค่อยสุ่มแบบไม่เอาสีซ้ำติดกัน
            let lastColor = colors[colors.length - 1];
            let newColor = lastColor;
            while (newColor === lastColor) {
                newColor = baseColors[Math.floor(Math.random() * baseColors.length)];
            }
            colors.push(newColor);
        }
    }

    return colors;
}


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

        let colors = generateColorPalette(2); // สร้างสีสุ่ม 2 สี
        let total = data.open_cm + data.close_cm; // หาผลรวมทั้งหมด

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
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom" },
                    datalabels: {
                        formatter: (value) => {
                            let percentage = ((value / total) * 100).toFixed(1); // คำนวณ % และให้มีทศนิยม 1 ตำแหน่ง
                            return `${percentage}%`; // แสดงค่าบนกราฟ
                        },
                        color: "#fff", // สีของข้อความ
                        font: {
                            weight: "bold",
                            size: 14
                        }
                    }
                }
            },
            plugins: [ChartDataLabels] // เปิดใช้งาน Data Labels
        });

    } catch (error) {
        console.error("❌ Error fetching CM status data:", error);
    }
}

// 📌 โหลด Pie Chart สำหรับอุปกรณ์ที่เสียบ่อยที่สุด
async function loadEquipmentFailurePieChart() {
    try {
        let equipResponse = await fetch("/dashboard/api/equipment_failure");
        let equipData = await equipResponse.json();
        console.log("📊 Equipment Data:", equipData);

        let equipCtx = document.getElementById("equipment-failure-pie-chart").getContext("2d");

        if (window.equipmentFailureChart) {
            window.equipmentFailureChart.destroy();
        }

        let dynamicColors = generateColorPalette(equipData.labels.length); // ✅ ใช้สีสุ่ม
        let total = equipData.values.reduce((sum, val) => sum + val, 0); // ✅ คำนวณผลรวมของค่าทั้งหมด

        window.equipmentFailureChart = new Chart(equipCtx, {
            type: "pie",
            data: {
                labels: equipData.labels,
                datasets: [{
                    data: equipData.values,
                    backgroundColor: dynamicColors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom" },
                    datalabels: {
                        formatter: (value) => {
                            let percentage = ((value / total) * 100).toFixed(1); // ✅ คำนวณเปอร์เซ็นต์ และปัดเศษทศนิยม 1 ตำแหน่ง
                            return `${percentage}%`; // ✅ แสดงค่าเป็นเปอร์เซ็นต์
                        },
                        color: "#fff", // ✅ กำหนดสีตัวอักษรเป็นสีขาว
                        font: {
                            weight: "bold",
                            size: 14
                        }
                    }
                }
            },
            plugins: [ChartDataLabels] // ✅ ใช้ ChartDataLabels เพื่อแสดงค่าบนกราฟ
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

        let colors = generateColorPalette(locationData.labels.length); // ✅ ใช้สีสุ่มจากฟังก์ชัน

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
                maintainAspectRatio: false, // ✅ ปรับให้ Chart เต็มพื้นที่ card
                layout: {
                    padding: {
                        top: 20  // ✅ เพิ่มระยะห่างด้านบน
                    }
                },
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                    datalabels: {
                        anchor: 'end',
                        align: 'right',
                        formatter: (value) => value,
                        color: '#000',
                        font: { weight: 'bold', size: 14 }
                    }
                },
                scales: {
                    x: { 
                        beginAtZero: true, 
                        suggestedMax: Math.max(...locationData.values) * 1.2, // ✅ เพิ่มขนาดสูงสุดอีก 20%
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

        let colors = generateColorPalette(lineData.labels.length); // ✅ ใช้สีสุ่ม

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
                maintainAspectRatio: false, // ✅ ปรับให้ Chart เต็มพื้นที่ card
                layout: {
                    padding: {
                        top: 20  // ✅ เพิ่มระยะห่างด้านบน
                    }
                },
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                    datalabels: {
                        anchor: 'end',
                        align: 'right',
                        formatter: (value) => value,
                        color: '#000',
                        font: { weight: 'bold', size: 14 }
                    }
                },
                scales: {
                    x: { beginAtZero: true, 
                        suggestedMax: Math.max(...lineData.values) * 1.2, // ✅ เพิ่มขนาดสูงสุดอีก 20%
                        ticks: { stepSize: 1, precision: 0 }
                    },
                    y: { beginAtZero: true, 
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

// 📌 เรียกใช้งานเมื่อโหลดหน้า
document.addEventListener("DOMContentLoaded", () => {
    loadCMOverviewData();
    loadCMStatusPieChart();
    loadEquipmentFailurePieChart();
    loadPendingTasksByLocationBarChart();
    loadCMByLineBarChart();
});
