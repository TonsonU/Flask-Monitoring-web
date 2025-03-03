document.addEventListener("DOMContentLoaded", function () {
    let lineFilter = document.getElementById("lineFilter");
    let locationFilter = document.getElementById("locationFilter");
    let workTableBody = document.getElementById("workTableBody");

    // 📌 โหลดข้อมูล Line ทั้งหมด
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
        workTableBody.innerHTML = '<tr><td colspan="4" class="text-center">เลือก Location เพื่อดูข้อมูล</td></tr>'; // ล้างตาราง

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

    // 📌 เมื่อเลือก Location ให้โหลดข้อมูล Work (Data Table)
    locationFilter.addEventListener("change", function () {
        workTableBody.innerHTML = '<tr><td colspan="4" class="text-center">กำลังโหลดข้อมูล...</td></tr>'; // แสดงข้อความกำลังโหลด

        let location_id = this.value;
        if (location_id) {
            fetch(`/dashboard/api/get_work_by_location?location_id=${location_id}`)
                .then((response) => response.json())
                .then((data) => {
                    if (data.length === 0) {
                        workTableBody.innerHTML =
                            '<tr><td colspan="4" class="text-center">ไม่มีข้อมูลงานซ่อม</td></tr>';
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
                })
                .catch((error) => {
                    console.error("❌ Error fetching work data:", error);
                    workTableBody.innerHTML =
                        '<tr><td colspan="4" class="text-center">เกิดข้อผิดพลาดในการโหลดข้อมูล</td></tr>';
                });
        } else {
            workTableBody.innerHTML = '<tr><td colspan="4" class="text-center">เลือก Location เพื่อดูข้อมูล</td></tr>';
        }
    });
});
