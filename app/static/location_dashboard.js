document.addEventListener("DOMContentLoaded", function () {
    let lineFilter = document.getElementById("lineFilter");
    let locationFilter = document.getElementById("locationFilter");
    let workTableBody = document.getElementById("workTableBody");
  
});

// 📌 โหลด Bar Chart สำหรับจำนวนงานซ่อมของแต่ละ Location
async function loadBarChartByLocation() {
    try {
        let response = await fetch(`/dashboard/api/work_count_by_location`);
        let data = await response.json();
        console.log("📊 Work Count by Location:", data); // ✅ Debug JSON Response

        let ctx = document.getElementById("work-location-bar-chart").getContext("2d");

        // ❌ ทำลาย Chart เดิมถ้ามีอยู่
        if (window.workLocationChart) {
            window.workLocationChart.destroy();
        }

        let colors = generateColorPalette(data.labels.length); // ✅ ใช้สีแบบวนซ้ำ

        window.workLocationChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,  // 📌 ชื่อ Location
                datasets: [{
                    label: "จำนวนงานซ่อม",
                    data: data.values,  // 📌 จำนวนงานซ่อม
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,  // ✅ ป้องกัน Chart บีบอัด
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
                        suggestedMax: Math.max(...data.values) * 1.2, // ✅ เพิ่มขนาดสูงสุดอีก 20%
                        ticks: { stepSize: 1, precision: 0 } 
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, precision: 0 }
                    }
                },
                onClick: function(event, elements) {
                    if (elements.length > 0) {
                        let index = elements[0].index;  // ✅ ดึง Index ของแท่งที่คลิก
                        let selectedLocation = data.labels[index];  // ✅ ดึงชื่อ Location ที่เลือก
                        let selectedLocationId = data.location_ids[index];  // ✅ ดึง location_id

                        console.log("📌 Selected Location:", selectedLocation);
                        console.log("📌 Selected Location ID:", selectedLocationId);

                        // 📌 เรียกใช้งานฟังก์ชันดึงข้อมูล Data Table
                        loadWorkDataTable(selectedLocationId);
                    }
                }
            },
            plugins: [ChartDataLabels]
        });

    } catch (error) {
        console.error("❌ Error fetching Work Count data:", error);
    }
}

// 📌 โหลด Data Table ตาม Location ID ที่เลือก
async function loadWorkDataTable(location_id) {
    let workTableBody = document.getElementById("workTableBody");

    workTableBody.innerHTML = '<tr><td colspan="7" class="text-center">กำลังโหลดข้อมูล...</td></tr>'; // ✅ แสดงข้อความกำลังโหลด

    try {
        let response = await fetch(`/dashboard/api/get_work_by_location?location_id=${location_id}`);
        let data = await response.json();
        console.log("📊 Work Data for Location ID:", location_id, data);

        if (data.length === 0) {
            workTableBody.innerHTML =
                '<tr><td colspan="7" class="text-center">ไม่มีข้อมูลงานซ่อม</td></tr>';
        } else {
            workTableBody.innerHTML = "";

            // ✅ เรียงลำดับข้อมูล โดยให้ "Open" มาก่อน "Closed"
            data.sort((a, b) => {
                if (a.status === "Open" && b.status === "Closed") return -1;
                if (a.status === "Closed" && b.status === "Open") return 1;
                return 0;
            });

            data.forEach((work) => {
                let maxLength = 30; // ✅ กำหนดจำนวนตัวอักษรสูงสุดที่จะแสดง
                let truncatedDescription = work.description.length > maxLength 
                    ? work.description.substring(0, maxLength) + "..."  // ✅ ตัดข้อความแล้วเติม "..."
                    : work.description;
                
                // ✅ กำหนดสีของ Status ตามค่า Open/Closed
                let statusClass = work.status === "Open" ? "status-open" : "status-closed";

                let row = `<tr>
                    <td>${work.work_order}</td>
                    <td><span class="status-tag ${statusClass}">${work.status}</span></td> 
                    <td>${work.device_type_name}</td>
                    <td>${work.device_name_name}</td>
                    <td>${work.location_name || "ไม่ระบุ"}</td>  <!-- ✅ ป้องกัน location_name เป็น null -->
                    <td title="${work.description}">${truncatedDescription}</td>  <!-- ✅ เพิ่ม Tooltip -->
                    <td>${work.report_by}</td>                    
                </tr>`;
                workTableBody.innerHTML += row;
            });
        }
    } catch (error) {
        console.error("❌ Error fetching work data:", error);
        workTableBody.innerHTML =
            '<tr><td colspan="7" class="text-center">เกิดข้อผิดพลาดในการโหลดข้อมูล</td></tr>';
    }
}




// 📌 โหลด Stacked Bar Chart: แสดงสถานะงานซ่อมในแต่ละสถานที่ (Top 10)
async function loadWorkStatusStackedChart() {
    try {
        let response = await fetch("/dashboard/api/work_status_by_location");
        let data = await response.json();
        console.log("📊 Work Status Data:", data);

        let ctx = document.getElementById("work-status-stacked-chart").getContext("2d");

        // ❌ ทำลาย Chart เดิมถ้ามีอยู่แล้ว
        if (window.workStatusChart) {
            window.workStatusChart.destroy();
        }

        let colors = {
            open: "rgba(54, 162, 235, 0.8)",  // สีฟ้าสำหรับ Open
            close: "rgba(255, 99, 132, 0.8)"  // สีแดงสำหรับ Close
        };

        window.workStatusChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,  // 📌 ชื่อสถานที่
                datasets: [
                    {
                        label: "Open",
                        data: data.open_values,  // 📌 จำนวนงาน Open
                        backgroundColor: colors.open
                    },
                    {
                        label: "Close",
                        data: data.close_values,  // 📌 จำนวนงาน Close
                        backgroundColor: colors.close
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 20  // ✅ เพิ่มระยะห่างด้านบน
                    }
                },
                indexAxis: 'y',
                plugins: {
                    legend: { position: "top" },  // ✅ แสดง Legend บนสุด
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
                        stacked: true,  // ✅ เปิดการแสดงผลแบบ Stacked
                        beginAtZero: true,
                        suggestedMax: Math.max(
                            ...data.open_values.map((v, i) => v + data.close_values[i])  // ✅ คำนวณค่ามากสุดจาก Open+Close
                        ) * 1.2, // ✅ เพิ่มขนาดสูงสุดอีก 20%
                        ticks: { stepSize: 1, precision: 0 }
                    },
                    y: {
                        stacked: true,  // ✅ เปิดการแสดงผลแบบ Stacked
                        beginAtZero: true,
                        ticks: { stepSize: 1, precision: 0 }
                    }
                },                
            }
        });

    } catch (error) {
        console.error("❌ Error fetching Work Status data:", error);
    }
}

// 📌 โหลดกราฟเมื่อหน้า Dashboard โหลดเสร็จ
document.addEventListener("DOMContentLoaded", loadWorkStatusStackedChart);


// 📌 โหลดกราฟเมื่อหน้าเว็บโหลดเสร็จ
document.addEventListener("DOMContentLoaded", function () {
    loadBarChartByLocation();
});
