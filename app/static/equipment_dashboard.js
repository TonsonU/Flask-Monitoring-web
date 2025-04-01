document.addEventListener("DOMContentLoaded", function () {
    let equipmentFilter = document.getElementById("equipmentFilter");

    // 📌 โหลดข้อมูลประเภทอุปกรณ์ทั้งหมดและตั้งค่า Default
    fetch("/dashboard/api/get_equipment_types_grouped")
        .then(response => response.json())
        .then(data => {
            let firstOption = null;  // ✅ เก็บค่าตัวแรก

            Object.keys(data).forEach((deviceName, index) => {
                let option = new Option(deviceName, deviceName);
                equipmentFilter.appendChild(option);

                if (index === 0) {
                    firstOption = deviceName; // ✅ กำหนดค่าแรกสุด
                }
            });

            // 📌 โหลดกราฟอัตโนมัติสำหรับตัวเลือกแรกของ Dropdown
            if (firstOption) {
                equipmentFilter.value = firstOption;
                loadWorkCountByEquipmentChart(firstOption);
                loadWorkTrendByEquipment(firstOption);
                loadBreakdownByEquipment(firstOption);
                loadDeviceLocationBreakdown(firstOption);
                loadPointCaseChart(firstOption);
                

            }
        });

    // 📌 เมื่อเปลี่ยนค่าใน Dropdown ให้โหลดกราฟใหม่
    equipmentFilter.addEventListener("change", function () {
        let selectedEquipment = this.value;
        if (selectedEquipment) {
            loadWorkCountByEquipmentChart(selectedEquipment);
            loadWorkTrendByEquipment(selectedEquipment);
            loadBreakdownByEquipment(selectedEquipment);
            loadDeviceLocationBreakdown(selectedEquipment);
            loadPointCaseChart(selectedEquipment);
        }
    });
});

document.getElementById("equipmentFilter").addEventListener("change", function () {
    const selected = this.value;

    // 👉 ถ้าเป็น Point ให้โชว์ card + โหลดกราฟ
    if (selected === "Point") {
        document.getElementById("point-card").style.display = "block";
        loadPointCaseChart();  // 📌 เรียกโหลดกราฟ
    } else {
        document.getElementById("point-card").style.display = "none";
    }
});


// 📌 โหลด Bar Chart สำหรับ Breakdown ของ Equipment ตาม Line
async function loadWorkCountByEquipmentChart(equipmentName) {
    try {
        let response = await fetch("/dashboard/api/get_equipment_types_grouped");
        let data = await response.json();
        let equipmentData = data[equipmentName] || [];

        console.log("📊 Work Count by Equipment (Grouped by Line):", equipmentData);

        let ctx = document.getElementById("work-count-by-equipment-chart").getContext("2d");

        // ❌ ทำลาย Chart เดิมถ้ามีอยู่
        if (window.workEquipmentChart) {
            window.workEquipmentChart.destroy();
        }

        let labels = equipmentData.map(item => item.line);
        let values = equipmentData.map(item => item.count);
        let colors = generateColorPalette(labels.length);

        window.workEquipmentChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: `จำนวนงานซ่อมของ ${equipmentName}`,
                    data: values,
                    backgroundColor: colors,
                    barThickness: 30  // ✅ ปรับขนาดแท่งกราฟให้เหมาะสม
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
                        color: '#000',
                        font: { weight: 'bold', size: 14 }
                    }
                },
                scales: {
                    x: { 
                        beginAtZero: true, 
                        suggestedMax: Math.max(...values) * 1.2, // ✅ เพิ่มขนาดสูงสุดอีก 20%
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
        console.error("❌ Error fetching Work Count by Equipment data:", error);
    }
}

// 📌 โหลด Line Chart สำหรับแนวโน้มปัญหาของอุปกรณ์ตามปี
async function loadWorkTrendByEquipment(equipment_name) {
    try {
        let response = await fetch(`/dashboard/api/work_trend_by_equipment?equipment_name=${encodeURIComponent(equipment_name)}`);
        let data = await response.json();
        console.log("📊 Work Trend Data:", data);  // ✅ Debug JSON Response

        let ctx = document.getElementById("work-trend-line-chart").getContext("2d");

        // ❌ ทำลาย Chart เดิมถ้ามีอยู่
        if (window.workTrendChart) {
            window.workTrendChart.destroy();
        }

        window.workTrendChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,  // 📌 ปีที่มีการซ่อมบำรุง
                datasets: [{
                    label: `แนวโน้มปัญหาของอุปกรณ์ (${equipment_name})`,
                    data: data.values,  // 📌 จำนวนงานซ่อมของอุปกรณ์ในแต่ละปี
                    borderColor: "#007bff",
                    backgroundColor: "rgba(0, 123, 255, 0.2)",
                    fill: true,
                    tension: 0.3,  // ✅ ให้เส้นโค้งเล็กน้อย
                    pointRadius: 5, // ✅ จุดกลมบนเส้นกราฟ
                    pointBackgroundColor: "#007bff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: { top: 20 }
                },
                plugins: {
                    legend: { position: "top" },
                    tooltip: { enabled: true },
                    datalabels: {
                        anchor: "end",
                        align: "top",
                        formatter: (value) => value,
                        color: "#000",
                        font: { weight: "bold", size: 14 }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    },
                    y: {
                        beginAtZero: true,
                        suggestedMax: Math.max(...data.values) * 1.2, // ✅ เพิ่มขนาดสูงสุดอีก 20%
                        ticks: { stepSize: 1, precision: 0 }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });

    } catch (error) {
        console.error("❌ Error fetching Work Trend data:", error);
    }
}

// 📌 โหลด Bar Chart สำหรับ Breakdown ของอุปกรณ์ (แสดง Device Name)
async function loadBreakdownByEquipment(equipment_name) {
    try {
        let response = await fetch(`/dashboard/api/breakdown_by_equipment?device_type_id=${equipment_name}`);
        let data = await response.json();
        console.log("📊 Breakdown by Equipment Data:", data);

        let ctx = document.getElementById("breakdown-equipment-chart").getContext("2d");

        // ❌ ทำลาย Chart เดิมถ้ามีอยู่
        if (window.breakdownChart) {
            window.breakdownChart.destroy();
        }

        let colors = generateColorPalette(data.labels.length);

        window.breakdownChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "จำนวนครั้งที่เสีย",
                    data: data.values,
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
                        color: '#000',
                        font: { weight: 'bold', size: 14 }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        suggestedMax: Math.max(...data.values) * 1.2,
                        ticks: { 
                            stepSize: 1, // ✅ บังคับให้เพิ่มทีละ 1
                            precision: 0 // ✅ บังคับให้เป็นจำนวนเต็ม
                        }
                    },
                    y: {
                        beginAtZero: true
                        
                    }
                }
            },
            plugins: [ChartDataLabels]
        });

    } catch (error) {
        console.error("❌ Error fetching Breakdown by Equipment data:", error);
    }
}

// 📌 โหลด Bar Chart แสดงจำนวนงานซ่อมของ Device Name แยกตาม Location
async function loadDeviceLocationBreakdown(device_type_name) {
    try {
        const response = await fetch(`/dashboard/api/device_location_breakdown?device_name=${encodeURIComponent(device_type_name)}`);
        const data = await response.json();
        console.log("📊 Device Breakdown by Location:", data);

        let ctx = document.getElementById("device-location-breakdown-chart").getContext("2d");

        if (window.deviceLocationChart) {
            window.deviceLocationChart.destroy();
        }

        const colors = generateColorPalette(data.labels.length);

        window.deviceLocationChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: `จำนวนเคสของ ${device_type_name} ในแต่ละ Location`,
                    data: data.values,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                layout: {
                    padding: { top: 20 }
                },
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
                        suggestedMax: Math.max(...data.values) * 1.2,
                        ticks: {
                            stepSize: 1,
                            precision: 0
                        }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });

    } catch (error) {
        console.error("❌ Error loading device breakdown by location:", error);
    }
}

async function loadPointCaseChart() {
    try {
        const response = await fetch("/dashboard/api/point_case_breakdown");
        const data = await response.json();
        console.log("📊 Point Case Breakdown:", data);

        const ctx = document.getElementById("point-case-chart").getContext("2d");

        if (window.pointChart) {
            window.pointChart.destroy();
        }

        const colors = generateColorPalette(data.labels.length);

        window.pointChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "จำนวนเคสของ Point",
                    data: data.values,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            precision: 0
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("❌ Error loading point case chart:", error);
    }
}
