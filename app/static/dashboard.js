window.onload = async function () {
    console.log("✅ Dashboard.js Loaded");

    try {
        // 📌 ดึงข้อมูล "อุปกรณ์ที่เสียบ่อยที่สุด"
        let equipResponse = await fetch("/dashboard/api/equipment_failure");
        let equipData = await equipResponse.json();
        console.log("📊 Equipment Data:", equipData);  // ✅ Debugging JSON

        let equipCtx = document.getElementById("equipment-failure-pie-chart").getContext("2d");

        // ❌ ทำลาย Chart เดิมถ้ามีอยู่แล้ว
        if (window.equipmentFailureChart) {
            window.equipmentFailureChart.destroy();
        }

        // ✅ สร้าง Pie Chart ใหม่
        window.equipmentFailureChart = new Chart(equipCtx, {
            type: "pie",
            data: {
                labels: equipData.labels,
                datasets: [{
                    data: equipData.values,
                    backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff", "#ff9f40"]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });

        // 📌 ดึงข้อมูล "งานซ่อมที่ค้างในแต่ละสถานที่"
        let locationResponse = await fetch("/dashboard/api/pending_tasks_location");
        let locationData = await locationResponse.json();
        console.log("📊 Location Data:", locationData);  // ✅ Debugging JSON

        let locationCtx = document.getElementById("pending-tasks-by-location-bar-chart").getContext("2d");

        // ❌ ทำลาย Chart เดิมถ้ามีอยู่แล้ว
        if (window.locationChart) {
            window.locationChart.destroy();
        }

        // ✅ สร้าง Bar Chart ใหม่
        window.locationChart = new Chart(locationCtx, {
            type: "bar",
            data: {
                labels: locationData.labels,       // 📌 ใช้ชื่อสถานที่
                datasets: [{
                    label: "งานที่ค้างอยู่",
                    data: locationData.values,     // 📌 จำนวนงานที่ค้างอยู่
                    backgroundColor: "#36a2eb"
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',  // ✅ แสดงแนวแกนนอน
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1, // ✅ บังคับให้เพิ่มทีละ 1 (ไม่มีเลขทศนิยม)
                            precision: 0  // ✅ บังคับให้แสดงเฉพาะจำนวนเต็ม
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("❌ Error fetching CM data:", error);
    }

    // 📌 ดึงข้อมูล Overview (Total CM, Open, Close)
    fetch("/dashboard/api/overview_data")
        .then(response => response.json())
        .then(data => {
            console.log("📊 Overview Data:", data);  // ✅ Debugging JSON
            document.getElementById("total_cm").innerText = data.total_cm;
            document.getElementById("open_cm").innerText = data.open_cm;
            document.getElementById("close_cm").innerText = data.close_cm;
        })
        .catch(error => console.error("❌ Error fetching overview data:", error));
};
