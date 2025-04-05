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
                loadMonthlyTrendChart(firstOption);
                loadMonthlyTrendYears(firstOption);
                loadDeviceStatusPieChart(firstOption); // ✅ โหลดกราฟ Pie Chart สถานะอุปกรณ์

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
            loadCauseCaseChart(selectedEquipment);
            loadDeviceStatusPieChart(selectedEquipment);
        }
    });
});

document.getElementById("equipmentFilter").addEventListener("change", function () {
    const selected = this.value;

    // 👉 ถ้าเป็น Point ให้โชว์ card + โหลดกราฟ
    if (selected === "Point") {
        // ✅ แสดงกราฟเฉพาะ Point
        document.getElementById("point-card").style.display = "block";
        document.getElementById("cause-card").style.display = "block";
        loadMonthlyTrendYears(equipment_name); // ✅ โหลดปีใหม่และกราฟ Line Chart
        loadPointCaseChart();
        loadCauseCaseChart();
    } else {
        document.getElementById("point-card").style.display = "none";
        document.getElementById("cause-card").style.display = "none";
    }
});

document.getElementById("equipmentFilter").addEventListener("change", function () {
    const equipment_name = this.value;
    if (equipment_name) {
        loadMonthlyTrendYears(equipment_name); // ✅ โหลดปีใหม่และกราฟ Line
    }
});



// 📌 โหลด Pie Chart สำหรับ Breakdown ของ Equipment ตาม Line
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
            type: "pie", // ✅ เปลี่ยนเป็น pie
            data: {
                labels: labels,
                datasets: [{
                    label: `จำนวนงานซ่อมของ ${equipmentName}`,
                    data: values,
                    backgroundColor: colors
                }]
            },
            options: {
                animation: {
                    duration: 1000,
                    easing: "easeOutQuart"
                },                
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom" },
                    tooltip: { enabled: true },
                    datalabels: {
                        formatter: (value, context) => {
                            // ✅ แสดงทั้งจำนวนและเปอร์เซ็นต์
                            const total = context.chart._metasets[0].total;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${percentage}%`;
                        },
                        color: "#fff",
                        font: { weight: "bold", size: 14 }
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
                animation: {
                    duration: 1000,
                    easing: "easeOutQuart"
                },                
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
                animation: {
                    duration: 1000,
                    easing: "easeOutQuart"
                },               
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

// 📌 โหลด Bar Chart แสดงจำนวนงานCM ของ Device Name แยกตาม Location
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
                animation: {
                    duration: 1000,
                    easing: "easeOutQuart"
                },                
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

// 📌 โหลด Bar Chart แสดงจำนวนประเภทของเคส CM ของ Point
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
                animation: {
                    duration: 1000,
                    easing: "easeOutQuart"
                },                
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
                    },
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
        console.error("❌ Error loading point case chart:", error);
    }
}

// 📌 โหลด Bar Chart แสดงจำนวนสาเหตุของเคส CM ของ Pointว่าเป็นที่ฝั่งไหน
async function loadCauseCaseChart() {
    try {
        const response = await fetch("/dashboard/api/cause_case_breakdown");
        const data = await response.json();
        console.log("📊 Cause Case Breakdown:", data);

        const ctx = document.getElementById("cause-case-chart").getContext("2d");

        if (window.causeChart) {
            window.causeChart.destroy();
        }

        const colors = generateColorPalette(data.labels.length);

        window.causeChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "จำนวนเคสตามสาเหตุ",
                    data: data.values,
                    backgroundColor: colors
                }]
            },
            options: {
                animation: {
                    duration: 1000,
                    easing: "easeOutQuart"
                },                
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
                    },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        suggestedMax: Math.max(...data.values) * 1.2,
                        ticks: { stepSize: 1, precision: 0 }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });
    } catch (error) {
        console.error("❌ Error loading cause case chart:", error);
    }
}

// ✅ ดึงปีที่มีข้อมูล แล้วโหลดกราฟล่าสุด
async function loadMonthlyTrendYears(equipment_name) {
    const yearSelect = document.getElementById("monthYearSelect");
    yearSelect.innerHTML = "";

    const res = await fetch(`/dashboard/api/work_years_by_equipment?equipment_name=${encodeURIComponent(equipment_name)}`);
    const years = await res.json();

    years.forEach((year, i) => {
        const option = new Option(year, year);
        if (i === years.length - 1) option.selected = true;
        yearSelect.appendChild(option);
    });

    if (years.length > 0) {
        loadMonthlyTrendChart(equipment_name, years[years.length - 1]);
    }
}

// ✅ โหลดกราฟ line ตามเดือน
async function loadMonthlyTrendChart(equipment_name, year) {
    const res = await fetch(`/dashboard/api/work_trend_by_month?equipment_name=${encodeURIComponent(equipment_name)}&year=${year}`);
    const data = await res.json();

    const ctx = document.getElementById("monthly-trend-line-chart").getContext("2d");
    if (window.monthlyChart) window.monthlyChart.destroy();

    window.monthlyChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [{
                label: `แนวโน้ม (${year})`,
                data: data.values,
                borderColor: "#0d6efd",
                backgroundColor: "rgba(13, 110, 253, 0.2)",
                fill: true,
                tension: 0.3,
                pointRadius: 5,
                pointBackgroundColor: "#0d6efd"
            }]
        },
        options: {
            animation: {
                duration: 1000,
                easing: "easeOutQuart"
            },            
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: { top: 20, bottom: 20}
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
}


// 📌 Event เมื่อเปลี่ยนปี
document.getElementById("monthYearSelect").addEventListener("change", function () {
    const year = this.value;
    const equipment = document.getElementById("equipmentFilter").value;
    if (equipment && year) {
        loadMonthlyTrendChart(equipment, year);
    }
});

// 📌 โหลด Pie Chart แสดงสัดส่วน Open / Closed ของอุปกรณ์ใน Device Type ที่เลือก
async function loadDeviceStatusPieChart(deviceTypeName) {
    const response = await fetch(`/dashboard/api/work_status_by_equipment?device_type_name=${encodeURIComponent(deviceTypeName)}`);
    const data = await response.json();
    console.log("📊 Status Data for", deviceTypeName, ":", data);

    const ctx = document.getElementById("status-pie-chart").getContext("2d");

    if (window.deviceStatusChart) {
        window.deviceStatusChart.destroy();
    }

    // 👉 รวมค่า Open / Closed
    const totalOpen = data.open_values.reduce((a, b) => a + b, 0);
    const totalClose = data.close_values.reduce((a, b) => a + b, 0);
    const total = totalOpen + totalClose;

    // ✅ ใช้ label คงที่
    const labels = ["Open", "Closed"];
    const values = [totalOpen, totalClose];
    let colors = generateColorPalette(labels.length);

    window.deviceStatusChart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: labels,
            datasets: [{
                label: `สถานะงานซ่อมของ ${deviceTypeName}`,
                data: values,
                backgroundColor: colors
            }]
        },
        options: {
            animation: {
                duration: 1000,
                easing: "easeOutQuart"
            },            
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" },
                tooltip: { enabled: true },
                datalabels: {
                    display: (context) => context.dataset.data[context.dataIndex] > 0,
                    formatter: (value, context) => {
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        return `${((value / total) * 100).toFixed(1)}%`;
                    },
                    color: "#fff",
                    font: { weight: "bold", size: 14 }
                }
            }
        },
        plugins: [ChartDataLabels]
    });
}
