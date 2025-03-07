document.addEventListener("DOMContentLoaded", function () {
    let equipmentFilter = document.getElementById("equipmentFilter");

    // 📌 โหลดข้อมูลประเภทอุปกรณ์ที่รวมกลุ่มแล้ว
    fetch("/dashboard/api/get_equipment_types_grouped")
        .then(response => response.json())
        .then(data => {
            let firstOption = null;  // ✅ ตัวแปรเก็บค่าแรกสุด

            Object.keys(data).forEach((deviceName, index) => {
                let option = new Option(deviceName, deviceName);
                equipmentFilter.appendChild(option);
                
                if (index === 0) {
                    firstOption = deviceName; // ✅ กำหนดค่าแรกสุด
                }
            });

            // 📌 ตั้งค่า default เป็นตัวแรกของ Dropdown
            if (firstOption) {
                equipmentFilter.value = firstOption;
                loadWorkCountByEquipmentChart(firstOption); // ✅ โหลดกราฟอัตโนมัติ
                loadWorkTrendByEquipment(firstOption); // ✅ โหลดแนวโน้มการซ่อม
            }
        });

    // 📌 เมื่อเลือกอุปกรณ์ ให้โหลด Bar Chart ตาม Line
    equipmentFilter.addEventListener("change", function () {
        let selectedEquipment = this.value;
        loadWorkCountByEquipmentChart(selectedEquipment);
    });

    // 📌 ฟังก์ชันโหลด Bar Chart
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
                        barThickness: 'flex'  // ✅ ปรับขนาดแท่งกราฟแบบ Dynamic ตามจำนวนข้อมูล
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
                            suggestedMax: Math.max(...values) * 1.2,
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

    // 📌 โหลด Line Chart สำหรับแนวโน้มงานซ่อมของอุปกรณ์ตามปี
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

    // 📌 โหลดข้อมูลเมื่อเลือกอุปกรณ์จาก Dropdown
    document.getElementById("equipmentFilter").addEventListener("change", function () {
        let equipment_name = this.value;
        if (equipment_name) {
            loadWorkTrendByEquipment(equipment_name);
        }
    });


    

});


