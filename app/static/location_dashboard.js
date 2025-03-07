document.addEventListener("DOMContentLoaded", function () {
    let lineFilter = document.getElementById("lineFilter");
    let locationFilter = document.getElementById("locationFilter");
    let workTableBody = document.getElementById("workTableBody");

   /* // 📌 โหลดข้อมูล Line ทั้งหมด
    fetch("/dashboard/api/get_lines_locations")
        .then((response) => response.json())
        .then((data) => {
            data.lines.forEach((line) => {
                let option = new Option(line.name, line.id);
                lineFilter.appendChild(option);
            });
        });

    // 📌 เมื่อเลือก Line ให้โหลดเฉพาะ Location ของ Line นั้น
    lineFilter.addEventListener("change", function () {
        locationFilter.innerHTML = '<option value="">-- เลือก Location --</option>'; // ล้างค่า dropdown
        workTableBody.innerHTML = '<tr><td colspan="6" class="text-center">เลือก Location เพื่อดูข้อมูล</td></tr>'; // ล้างตาราง

        let line_id = this.value;

        if (line_id) {
            fetch(`/dashboard/api/get_lines_locations?line_id=${line_id}`)
                .then((response) => response.json())
                .then((data) => {
                    data.locations.forEach((location) => {
                        let option = new Option(location.name, location.id);
                        locationFilter.appendChild(option);
                    });
                });
        }
    });

    // 📌 เมื่อเลือก Location ให้โหลดข้อมูล Work (Data Table + Bar Chart)
    locationFilter.addEventListener("change", function () {
        workTableBody.innerHTML = '<tr><td colspan="6" class="text-center">กำลังโหลดข้อมูล...</td></tr>'; // แสดงข้อความกำลังโหลด

        let location_id = this.value;
        if (location_id) {
            fetch(`/dashboard/api/get_work_by_location?location_id=${location_id}`)
                .then((response) => response.json())
                .then((data) => {
                    if (data.length === 0) {
                        workTableBody.innerHTML =
                            '<tr><td colspan="6" class="text-center">ไม่มีข้อมูลงานซ่อม</td></tr>';
                    } else {
                        workTableBody.innerHTML = "";
                        data.forEach((work) => {
                            let row = `<tr>
                                <td>${work.work_order}</td>
                                <td>${work.status}</td>
                                <td>${work.device_type_name}</td>
                                <td>${work.device_name_name}</td>
                                <td>${work.description}</td>
                                <td>${work.report_by}</td>
                            </tr>`;
                            workTableBody.innerHTML += row;
                        });
                    }

                    // 📌 โหลด Bar Chart หลังจากโหลดข้อมูลสำเร็จ
                    loadBarChartByLocation(location_id);
                })
                .catch((error) => {
                    console.error("❌ Error fetching work data:", error);
                    workTableBody.innerHTML =
                        '<tr><td colspan="6" class="text-center">เกิดข้อผิดพลาดในการโหลดข้อมูล</td></tr>';
                });
        } else {
            workTableBody.innerHTML = '<tr><td colspan="6" class="text-center">เลือก Location เพื่อดูข้อมูล</td></tr>';
        }
    }); */
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



// 📌 ฟังก์ชันสร้างชุดสีแบบวนซ้ำอัตโนมัติ (ขยาย Color Palette ให้มากขึ้น)
function generateColorPalette(count) {
    let baseColors = [
        "#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#AF69EE",
        "#FFB6C1", "#FF9F40", "#36A2EB", "#B4E4FF", "#74C69D",
        "#F9C74F", "#90BE6D", "#F8961E", "#9D4EDD", "#577590",
        "#D72638", "#3F88C5", "#F49D37", "#140F2D", "#78C091",
        "#9A348E", "#FA7921", "#70A9A1", "#407899", "#B8336A",
        "#5FAD41", "#DB504A", "#218380", "#FF6700", "#007F5F",
        "#9B5DE5", "#00BBF9", "#F15BB5", "#FF7F50", "#6A0572",
        "#02C39A", "#2A9D8F", "#E63946", "#457B9D", "#8ECAE6",
        "#8338EC", "#FFBE0B", "#FB5607", "#A8DADC", "#264653",
        "#E76F51", "#D4A373", "#6A994E", "#B5838D", "#C9A227",
        "#EE6C4D", "#3D348B", "#FF006E", "#FF9E00", "#00A896"
    ];
    
    let colors = [];
    for (let i = 0; i < count; i++) {
        let randomIndex = Math.floor(Math.random() * baseColors.length);  // ✅ สุ่ม index
        colors.push(baseColors[randomIndex]);
    }
    return colors;
}
