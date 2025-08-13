document.addEventListener("DOMContentLoaded", () => {

    const tbody = document.getElementById("project-table-body");
    const createRsqrForm = document.getElementById("create-rsqr-form");
    const createRsqrBtn = document.getElementById("create-rsqr-btn");

    // ========== ADD PROJECT ==========
    document.querySelector(".add-project-btn").addEventListener("click", () => {
        const today = new Date().toISOString().split('T')[0];

        fetch("/dashboard/add_project", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({
                title: "Untitled Project",
                date: today
            }),
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const row = document.createElement("tr");
                row.setAttribute("data-id", data.project_id);
                row.innerHTML = `
                    <td>${data.created_date}</td>
                    <td contenteditable="true">Untitled Project</td>
                    <td contenteditable="true"></td>
                    <td contenteditable="true"></td>
                    <td><span class="status status-${data.status.replace(/\s/g, '')}">${data.status}</span></td>
                    <td><button class="save-btn styled-btn"><i class="fas fa-save"></i> Save</button></td>
                    <td><a href="/rsqr/${data.project_id}"><button class="view-btn styled-btn"><i class="fas fa-eye"></i> View</button></a></td>
                    <td><button class="delete-btn styled-btn"><i class="fas fa-trash"></i> Delete</button></td>
                `;
                tbody.prepend(row);

                // ✅ Enable RSQR for new project
                updateRsqrButton(data.project_id);
            }
        })
        .catch(err => console.error("Add Project Error:", err));
    });

    // ========== SAVE PROJECT ==========
    tbody.addEventListener("click", (e) => {
        if (e.target.closest(".save-btn")) {
            const row = e.target.closest("tr");
            const projectId = row.dataset.id;
            if (!projectId) return;

            const cells = row.querySelectorAll("td");
            const title = cells[1].innerText.trim();
            const pi = cells[2].innerText.trim();
            const institute = cells[3].innerText.trim();

            fetch(`/dashboard/update_project/${projectId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "same-origin",
                body: JSON.stringify({ title, pi, institute }),
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    row.querySelector(".status").textContent = data.status;
                    row.querySelector(".status").className = `status status-${data.status.replace(/\s/g, '')}`;
                    alert("✅ Project saved successfully");

                    // ✅ Make RSQR point to saved project
                    updateRsqrButton(projectId);
                } else {
                    alert("❌ Failed to save project");
                }
            })
            .catch(err => console.error("Save Project Error:", err));
        }
    });

    // ========== DELETE PROJECT ==========
    tbody.addEventListener("click", (e) => {
        if (e.target.closest(".delete-btn")) {
            const row = e.target.closest("tr");
            const projectId = row.dataset.id;
            if (!projectId) return;

            if (!confirm("Are you sure you want to delete this project and all its related data?")) {
                return;
            }

            fetch(`/dashboard/delete_project/${projectId}`, {
                method: "POST",
                credentials: "same-origin",
                headers: { "Accept": "application/json" }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    row.remove();
                    alert("🗑️ Project deleted successfully");

                    const remainingRows = tbody.querySelectorAll("tr");
                    if (remainingRows.length === 0) {
                        // No projects left → disable RSQR
                        disableRsqrButton();
                    } else {
                        // Always pick the first (topmost) row as latest
                        const latestId = remainingRows[0].dataset.id;
                        updateRsqrButton(latestId);
                    }
                } else {
                    alert("❌ Failed to delete project");
                }
            })
            .catch(err => console.error("Delete Project Error:", err));
        }
    });

    // ========== RSQR Button Handlers ==========
    function updateRsqrButton(projectId) {
        if (createRsqrForm) {
            createRsqrForm.action = `/rsqr/${projectId}`;
        }
        if (createRsqrBtn) {
            createRsqrBtn.disabled = false;
        }
    }

    function disableRsqrButton() {
        if (createRsqrForm) {
            createRsqrForm.action = "#";
        }
        if (createRsqrBtn) {
            createRsqrBtn.disabled = true;
        }
    }

    // ========== Logout ==========
    const logoutBtn = document.querySelector(".logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = "/logout";
        });
    }
});
