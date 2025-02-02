// Inventory Status Functions
function loadInventoryStatus() {
    $.get("/api/v1/inventory/parts/inventory-status/", function (data) {
        let html = '<div class="table-responsive">';

        // Create an accordion for each aircraft type
        Object.entries(data).forEach(([aircraftType, parts], aircraftIndex) => {
            html += `
        <div class="card mb-2">
          <div class="card-header bg-light d-flex justify-content-between align-items-center" 
               role="button" 
               data-bs-toggle="collapse" 
               data-bs-target="#aircraft${aircraftIndex}">
            <h6 class="mb-0">${aircraftType}</h6>
            <div>
              <span class="badge bg-primary me-2">Total Parts: ${calculateTotalParts(parts)}</span>
              <i class="fas fa-chevron-down"></i>
            </div>
          </div>
          <div id="aircraft${aircraftIndex}" class="collapse">
            <div class="card-body p-0">
              <table class="table table-sm mb-0">
                <thead>
                  <tr >
                    <th>Part Type</th>
                    <th class="text-center">Total</th>
                    <th class="text-center">Available</th>
                    <th class="text-center">Used</th>
                  </tr>
                </thead>
                <tbody>`;

            // Add rows for each part type
            Object.entries(parts).forEach(([part_type, status]) => {
                html += `
          <tr>
            <td>${formatPartType(part_type)}</td>
            <td class="text-center">${status.total}</td>
            <td class="text-center">
              <span class="badge bg-success">${status.available}</span>
            </td>
            <td class="text-center">
              <span class="badge bg-secondary">${status.used}</span>
            </td>
          </tr>`;
            });

            html += `
                </tbody>
              </table>
            </div>
          </div>
        </div>`;
        });

        html += "</div>";
        $("#inventory-status").html(html);
    });
}

// Helper function to calculate total parts for an aircraft type
function calculateTotalParts(parts) {
    return Object.values(parts).reduce((sum, status) => sum + status.total, 0);
}

// Helper function to format part type name
function formatPartType(type) {
    return type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
}

// Function to refresh all components
function refreshAllComponents(refreshType = "all") {
    switch (refreshType) {
        case "parts":
            if (typeof partsTable !== "undefined") {
                partsTable.ajax.reload();
            }
            loadInventoryStatus();
            break;
        case "aircraft":
            if (typeof aircraftTable !== "undefined") {
                aircraftTable.ajax.reload();
            }
            loadInventoryStatus();
            break;
        case "inventory":
            loadInventoryStatus();
            break;
        case "all":
        default:
            if (typeof partsTable !== "undefined") {
                partsTable.ajax.reload();
            }
            if (typeof aircraftTable !== "undefined") {
                aircraftTable.ajax.reload();
            }
            loadInventoryStatus();
            break;
    }
}

// Event handlers for filters
function initFilterHandlers() {
    $(".filter-control").on("change", function () {
        const tableId = $(this).data("table");
        if (tableId === "parts") {
            refreshAllComponents("parts");
        } else if (tableId === "aircraft") {
            refreshAllComponents("aircraft");
        }
    });
}
