document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript is running on this page!");
    function calculateTotalAmount() {
        let totalAmount = 0;
        console.log(totalAmount)
        // Select all visible rows in the Django admin table
        const rows = document.querySelectorAll("tbody tr");

        rows.forEach((row) => {
            // Get the value from the "Order Total Price" column (adjust the index if necessary)
            const amountCell = row.querySelector("td.field-order_total_price");
            if (amountCell) {
                const amount = parseFloat(amountCell.textContent.trim()) || 0;
                totalAmount += amount;
            }
        });
        console.log(totalAmount)
        // Update the total amount display
        const totalAmountElement = document.getElementById("total-amount");
        console.log(totalAmountElement)
        if (totalAmountElement) {
            
            totalAmountElement.textContent = totalAmount.toFixed(2);
            console.log(totalAmount)
        }
        console.log(totalAmount)
    }

    // Calculate total on page load
    calculateTotalAmount();

    // Recalculate whenever filters are applied
    document.querySelectorAll(".changelist-filter a").forEach((filter) => {
        filter.addEventListener("click", () => {
            console.log("called")
            setTimeout(calculateTotalAmount, 500); // Wait for filters to apply
        });
    });
});
