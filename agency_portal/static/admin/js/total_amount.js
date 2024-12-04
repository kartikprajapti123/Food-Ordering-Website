document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript is running on this page!");

    const totalAmountElement = document.getElementById("total-amount");
    if (!totalAmountElement) {
        console.error("The #total-amount element is missing!");
        return;
    }
    console.log("Found #total-amount element:", totalAmountElement);

    function calculateTotalAmount() {
        let totalAmount = 0;

        // Select all visible rows in the Django admin table
        const rows = document.querySelectorAll("tbody tr");
        if (rows.length === 0) {
            console.warn("No rows found in the table.");
        } else {
            console.log(`Found ${rows.length} rows.`);
        }

        rows.forEach((row) => {
            const amountCell = row.querySelector("td.field-order_total_price");
            if (amountCell) {
                const amount = parseFloat(amountCell.textContent.trim()) || 0;
                totalAmount += amount;
            } else {
                console.warn("No amountCell found for a row.");
            }
        });

        // Update the total amount display
        console.log("Total amount calculated:", totalAmount);
        totalAmountElement.textContent = totalAmount.toFixed(2);
    }

    // Initial calculation
    calculateTotalAmount();

    // Handle filter changes
    document.querySelectorAll(".changelist-filter a").forEach((filter) => {
        filter.addEventListener("click", () => {
            console.log("Filter clicked, recalculating...");
            setTimeout(calculateTotalAmount, 500);
        });
    });
});
