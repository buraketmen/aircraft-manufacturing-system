// Init parts table and filters
let partsTable;

function initPartsTable() {
    partsTable = $("#parts-table").DataTable({
        serverSide: true,
        responsive: true,
        ajax: {
            url: "/api/v1/inventory/parts/",
            data: function (d) {
                const createdAt = $("#filter-created-at").val();
                return {
                    draw: d.draw,
                    start: d.start,
                    length: d.length,
                    ordering: d.order[0]?.dir === "desc" ? "-created_at" : "created_at",
                    is_used: $("#filter-status").val(),
                    part_type: $("#filter-type").val(),
                    aircraft_type: $("#filter-aircraft-type").val(),
                    created_at_after: createdAt ? createdAt + "T00:00:00" : null,
                    created_at_before: createdAt ? createdAt + "T23:59:59" : null,
                };
            },
        },
        columns: [
            {
                data: "serial_number",
                name: "serial_number",
                orderable: false,
            },
            {
                data: "part_type_name",
                name: "part_type__name",
                orderable: false,
                responsivePriority: 1,
            },
            {
                data: "aircraft_type_name",
                name: "aircraft_type__name",
                orderable: false,
                responsivePriority: 2,
            },
            {
                data: "owner_name",
                name: "owner__user__username",
                orderable: false,
                responsivePriority: 3,
            },
            {
                data: "is_used",
                name: "is_used",
                orderable: false,
                responsivePriority: 1,
                render: function (data) {
                    return data
                        ? '<span class="badge bg-secondary">Used</span>'
                        : '<span class="badge bg-success">Available</span>';
                },
            },
            {
                data: "created_at",
                name: "created_at",
                responsivePriority: 4,
                render: function (data) {
                    return new Date(data).toLocaleString();
                },
            },
            {
                data: null,
                orderable: false,
                responsivePriority: 1,
                render: function (data) {
                    let buttons = ``;
                    if (!data.is_used && data.owner_team === currentUserTeam) {
                        buttons += `<button class="btn btn-sm btn-danger" onclick="recyclePart(${data.id})">Recycle</button>`;
                    }
                    return buttons;
                },
            },
        ],
        order: [[5, "desc"]],
        pageLength: 10,
        processing: true,
        orderCellsTop: true,
        fixedHeader: true,
        searching: false,
        responsive: {
            details: {
                type: "column",
                target: "tr",
            },
        },
    });
}

// Init parts filters
function initPartsFilters() {
    $("#parts-table_wrapper").prepend(`
        <div class="row g-2 mb-3">
            <div class="col-12 col-sm-6 col-md-3 px-1">
                <select id="filter-status" class="form-select filter-control" data-table="parts">
                    <option value="">All Status</option>
                    <option value="true">Used</option>
                    <option value="false">Available</option>
                </select>
            </div>
            <div class="col-12 col-sm-6 col-md-3 px-1">
                <select id="filter-type" class="form-select filter-control" data-table="parts">
                    <option value="">All Types</option>
                    <option value="WING">Wing</option>
                    <option value="BODY">Body</option>
                    <option value="TAIL">Tail</option>
                    <option value="AVIONICS">Avionics</option>
                </select>
            </div>
            <div class="col-12 col-sm-6 col-md-3 px-1">
                <select id="filter-aircraft-type" class="form-select filter-control" data-table="parts">
                    <option value="">All Aircrafts</option>
                </select>
            </div>
            <div class="col-12 col-sm-6 col-md-3 px-1">
                <input type="date" id="filter-created-at" class="form-control filter-control" data-table="parts" placeholder="Created After">
            </div>
        </div>
    `);

    // Populate aircraft types from the template
    const aircraftTypeSelect = $("#filter-aircraft-type");
    $("#partAircraftType option").each(function () {
        if ($(this).val()) {
            aircraftTypeSelect.append(new Option($(this).text(), $(this).val()));
        }
    });
}

// Recycle part (delete)
function recyclePart(id) {
    // Show confirmation dialog before recycling
    if (confirm("Are you sure you want to recycle this part?")) {
        $.ajax({
            url: `/api/v1/inventory/parts/${id}/`,
            method: "DELETE",
            success: function () {
                refreshAllComponents("parts");
            },
            error: function (xhr) {
                alert(xhr.responseJSON?.error || "Error recycling part");
            },
        });
    }
}

// Create new part
function createPart() {
    const aircraftType = $("#partAircraftType").val();
    if (!aircraftType) {
        // Show alert if aircraft type is not selected
        alert("Please select an aircraft type");
        return;
    }

    $.ajax({
        url: "/api/v1/inventory/parts/",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            part_type: $("#partType").val(),
            aircraft_type: aircraftType,
        }),
        success: function () {
            // Hide modal and refresh parts table
            $("#createPartModal").modal("hide");
            refreshAllComponents("parts");
            $("#partAircraftType").val("");
        },
        error: function (xhr) {
            alert(xhr.responseJSON?.detail || "Error creating part");
        },
    });
}
