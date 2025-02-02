// Initialize all components
function initializeComponents() {
    // Setup CSRF token for all AJAX requests
    $.ajaxSetup({
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        },
    });

    // Initialize part table and filters
    if ($("#parts-table").length) {
        initPartsTable();
        initPartsFilters();
    }

    // Initialize aircraft table and filters
    if ($("#aircraft-table").length) {
        initAircraftTable();
        initAircraftFilters();
    }

    // Initialize event handlers
    initFilterHandlers();

    // Event handler for aircraft type selection in assembly modal
    $("#aircraftType").on("change", function () {
        const aircraftType = $(this).val();
        if (aircraftType) {
            loadAvailableParts(aircraftType);
        } else {
            $("#availablePartsSection").hide();
            $("#assembleButton").prop("disabled", true);
        }
    });

    // Event handler for part selection
    $(".part-select").on("change", function () {
        checkAssembleButton();
    });

    // Initial load of inventory status
    loadInventoryStatus();
}
