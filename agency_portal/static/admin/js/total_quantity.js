document.addEventListener("DOMContentLoaded", function () {
    function calculateTotals() {
        let totalAmount = 0;
        let totalQuantity = 0;

        // Select all visible rows in the Django admin table
        const rows = document.querySelectorAll("tbody tr");

        rows.forEach((row) => {
            // Get the value from the "Order Total Price" column (adjust the class if necessary)
            const amountCell = row.querySelector("td.field-order_item_total_price");
            if (amountCell) {
                const rawAmount = amountCell.textContent.trim();
                console.log("Raw Amount:", rawAmount); // Log raw amount content

                // Clean the amount string (remove non-numeric characters like currency symbols)
                const amount = parseFloat(rawAmount.replace(/[^\d.-]/g, "")) || 0;
                console.log("Parsed Amount:", amount); // Log parsed amount

                totalAmount += amount;
            }

            // Get the value from the "Order Quantity" column (adjust the class if necessary)
            const quantityCell = row.querySelector("td.field-quantity");
            if (quantityCell) {
                const rawQuantity = quantityCell.textContent.trim();
                console.log("Raw Quantity:", rawQuantity); // Log raw quantity content

                const quantity = parseFloat(rawQuantity) || 0;
                console.log("Parsed Quantity:", quantity); // Log parsed quantity

                totalQuantity += quantity;
            }
        });

        // Update the total amount display
        const totalAmountElement = document.getElementById("total-amount");
        if (totalAmountElement) {
            console.log("Total Amount (Final):", totalAmount); // Log final total amount
            totalAmountElement.textContent = totalAmount.toFixed(2);
        }

        // Update the total quantity display
        const totalQuantityElement = document.getElementById("total-quantity");
        if (totalQuantityElement) {
            totalQuantityElement.textContent = totalQuantity;
        }
    }

    // Calculate totals on page load
    calculateTotals();

    // Recalculate whenever filters are applied
    document.querySelectorAll(".changelist-filter a").forEach((filter) => {
        filter.addEventListener("click", () => {
            setTimeout(calculateTotals, 500); // Wait for filters to apply
        });
    });
});
