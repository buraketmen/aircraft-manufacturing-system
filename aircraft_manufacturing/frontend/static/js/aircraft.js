// Aircraft Table Configuration
let aircraftTable;

function initAircraftTable() {
    aircraftTable = $("#aircraft-table").DataTable({
        serverSide: true,
        responsive: true,
        ajax: {
            url: "/api/v1/assembly/aircraft/",
            data: function (d) {
                const dateFrom = $("#aircraft-filter-date-from").val();
                const dateTo = $("#aircraft-filter-date-to").val();
                return {
                    draw: d.draw,
                    start: d.start,
                    length: d.length,
                    ordering: d.order[0]?.dir === "desc" ? "-created_at" : "created_at",
                    aircraft_type: $("#aircraft-filter-type").val(),
                    assembled_after: dateFrom ? dateFrom + "T00:00:00" : null,
                    assembled_before: dateTo ? dateTo + "T23:59:59" : null,
                };
            },
        },
        columns: [
            {
                data: "serial_number",
                name: "serial_number",
                orderable: false,
                responsivePriority: 1,
            },
            {
                data: "aircraft_type_name",
                name: "aircraft_type__name",
                orderable: false,
                responsivePriority: 1,
            },
            {
                data: "owner_name",
                name: "owner__user__username",
                orderable: false,
                responsivePriority: 2,
            },
            {
                data: "created_at",
                name: "created_at",
                responsivePriority: 3,
                render: function (data) {
                    return new Date(data).toLocaleString();
                },
            },
            {
                data: null,
                orderable: false,
                responsivePriority: 1,
                render: function (data) {
                    return `<button class="btn btn-sm btn-primary" onclick="viewAircraft(${data.id})">Details</button>`;
                },
            },
        ],
        order: [[3, "desc"]],
        pageLength: 10,
        processing: true,
        orderCellsTop: true,
        fixedHeader: true,
        searching: false,
    });
}

// Init aircraft filters
function initAircraftFilters() {
    $("#aircraft-table_wrapper").prepend(`
        <div class="row mb-3">
            <div class="col-md-4">
                <input type="date" id="aircraft-filter-date-from" class="form-control filter-control" data-table="aircraft" placeholder="From Date">
            </div>
            <div class="col-md-4">
                <input type="date" id="aircraft-filter-date-to" class="form-control filter-control" data-table="aircraft" placeholder="To Date">
            </div>
            <div class="col-md-4">
                <select id="aircraft-filter-type" class="form-select filter-control" data-table="aircraft">
                    <option value="">All Aircrafts</option>
                </select>
            </div>
        </div>
    `);

    // Populate aircraft types from the template
    const aircraftTypeSelect = $("#aircraft-filter-type");
    $("#aircraftType option").each(function () {
        if ($(this).val()) {
            aircraftTypeSelect.append(new Option($(this).text(), $(this).val()));
        }
    });
}

function viewAircraft(id) {
    $.get(`/api/v1/assembly/aircraft/${id}/`, function (data) {
        // Set aircraft details
        console.log(data);
        $("#detailAircraftType").text(data.aircraft_type_name || data.aircraft_type);
        $("#detailAssembledBy").text(data.owner_name || data.owner_team);
        $("#detailAssembledAt").text(new Date(data.created_at).toLocaleString());

        // Clear and populate parts table
        const partsTableBody = $("#detailPartsTableBody");
        partsTableBody.empty();

        // Group parts by type for better organization
        const partsByType = {};
        data.used_parts.forEach((part) => {
            const type = part.part_details.part_type_name;
            if (!partsByType[type]) {
                partsByType[type] = [];
            }
            partsByType[type].push(part);
        });
        console.log(partsByType);
        // Add parts to table, grouped by type
        Object.entries(partsByType).forEach(([type, parts]) => {
            // Use part number if there are multiple parts of the same type
            parts.forEach((part, index) => {
                const partNumber = parts.length > 1 ? ` #${index + 1}` : "";
                partsTableBody.append(`
                    <tr>
                        <td>${part.part_details.serial_number || "########"}</td>
                        <td>${type}${partNumber}</td>
                        <td>${part.part_details.owner_name}</td>
                        <td>${new Date(part.part_details.created_at).toLocaleString()}</td>
                    </tr>
                `);
            });
        });

        // Show modal
        $("#aircraftDetailsModal").modal("show");
    }).fail(function (xhr) {
        alert("Error loading aircraft details");
    });
}

function loadAvailableParts(aircraftType) {
    // Clear and hide previous state
    $(".part-select").empty().prop("disabled", true);
    $("#availablePartsSection").hide();
    $("#assemblyStatus").removeClass("alert-danger alert-success").hide();
    $("#assembleButton").prop("disabled", true);

    $.get(`/api/v1/inventory/parts/available/${aircraftType}/`, function (data) {
        if (!data.can_assemble) {
            // Show error message with missing parts details
            let message = "<strong>Cannot assemble aircraft:</strong><br>";
            message += "<ul class='mb-0'>";
            data.missing_parts.forEach((part) => {
                message += `<li>${part.type}: Have ${part.available} of ${part.required} required</li>`;
            });
            message += "</ul>";

            $("#assemblyStatus").addClass("alert-danger").html(message).show();
            return;
        }

        // Show success message
        $("#assemblyStatus")
            .addClass("alert-success")
            .html(`<strong>Ready to assemble:</strong> All required parts are available.`)
            .show();

        const partsByType = {};
        data.parts.forEach((part) => {
            if (!partsByType[part.type]) {
                partsByType[part.type] = [];
            }
            partsByType[part.type].push(part);
        });

        // Main area to show available parts
        const availablePartsSection = $("#availablePartsSection");
        availablePartsSection.empty().show();

        // Add required parts to the form
        Object.entries(data.required_parts).forEach(([type, requiredCount]) => {
            const typeLower = type.toLowerCase();

            // Add a container for each part type
            const container = $(`
        <div class="mb-3">
            <label class="form-label">${type}</label>
            <div id="${typeLower}PartsContainer"></div>
        </div>
    `);

            availablePartsSection.append(container);

            const containerDiv = container.find(`#${typeLower}PartsContainer`);

            // Add select elements for each required part
            for (let i = 0; i < requiredCount; i++) {
                const select = $("<select>")
                    .addClass("form-select part-select mb-2")
                    .attr("id", `${typeLower}Part${i + 1}`)
                    .attr("data-type", typeLower);

                select.append('<option value="">Select Part</option>');

                // Add available parts as options
                const availableParts = partsByType[type] || [];
                availableParts.forEach((part) => {
                    select.append(
                        `<option value="${part.id}">${part.type} (${new Date(
                            part.created_at,
                        ).toLocaleString()})</option>`,
                    );
                });

                // Update available parts when a part is selected
                select.on("change", function () {
                    updateAvailableParts(type, availableParts);
                });

                containerDiv.append(select);
            }
        });

        // Show available parts section
        $("#availablePartsSection").show();

        // Check if all parts are selected
        checkAssembleButton();
    }).fail(function (xhr) {
        $("#assemblyStatus")
            .addClass("alert-danger")
            .html("<strong>Error:</strong> Failed to load available parts.")
            .show();
    });
}

function updateAvailableParts(type, allParts) {
    // Get all select elements for this part type
    const selects = $(`[data-type="${type.toLowerCase()}"]`);

    // Get all selected values
    const selectedValues = new Set();
    selects.each(function () {
        const value = $(this).val();
        if (value) selectedValues.add(value);
    });

    // Update each select
    selects.each(function () {
        const currentSelect = $(this);
        const currentValue = currentSelect.val();

        // Store current selection
        currentSelect.empty().append('<option value="">Select Part</option>');

        // Rebuild options
        allParts.forEach((part) => {
            const isSelected = selectedValues.has(part.id.toString());
            if (!isSelected || currentValue === part.id.toString()) {
                const option = `<option value="${part.id}" ${currentValue === part.id.toString() ? "selected" : ""}>
          ${part.type} - Created: ${new Date(part.created_at).toLocaleString()}
        </option>`;
                currentSelect.append(option);
            }
        });
    });

    checkAssembleButton();
}

function checkAssembleButton() {
    // Check if all required parts are selected
    const allSelected = $(".part-select")
        .toArray()
        .every((select) => $(select).val());
    $("#assembleButton").prop("disabled", !allSelected);
}

function assembleAircraft() {
    const aircraftType = $("#aircraftType").val();
    if (!aircraftType) {
        alert("Please select an aircraft type");
        return;
    }

    // Collect selected parts by type
    const parts = {};
    const selectedParts = new Set();
    let hasError = false;

    $(".part-select").each(function () {
        const type = $(this).data("type");
        const value = $(this).val();

        if (!value) {
            alert("Please select all required parts");
            hasError = true;
            return false;
        }

        if (selectedParts.has(value)) {
            alert("Each part can only be used once");
            hasError = true;
            return false;
        }

        selectedParts.add(value);
        // wing_ids, body_ids etc.
        if (!parts[`${type.toLowerCase()}_ids`]) {
            parts[`${type.toLowerCase()}_ids`] = [];
        }
        parts[`${type.toLowerCase()}_ids`].push(value);
    });

    if (hasError) return;

    // Show loading state
    $("#assembleButton")
        .prop("disabled", true)
        .html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Assembling...');

    $.ajax({
        url: "/api/v1/assembly/aircraft/",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            aircraft_type: aircraftType,
            parts: parts,
        }),
        success: function () {
            $("#assembleAircraftModal").modal("hide");
            refreshAllComponents("aircraft");
            refreshAllComponents("parts");
            // Reset form
            $("#assembleAircraftForm")[0].reset();
            $("#availablePartsSection").hide();
            $("#assembleButton").prop("disabled", true).html("Assemble");
        },
        error: function (xhr) {
            // Reset button state
            $("#assembleButton").prop("disabled", false).html("Assemble");

            // Show error message
            const response = xhr.responseJSON || {};
            let errorMessage = "Error assembling aircraft";

            if (response.detail) {
                errorMessage = response.detail;
            } else if (typeof response === "object") {
                // Collect all error messages
                const errors = [];
                Object.entries(response).forEach(([key, messages]) => {
                    if (Array.isArray(messages)) {
                        errors.push(`${key}: ${messages.join(", ")}`);
                    }
                });
                if (errors.length > 0) {
                    errorMessage = errors.join("\n");
                }
            }

            alert(errorMessage);
        },
    });
}
