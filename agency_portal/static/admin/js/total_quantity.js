document.addEventListener("DOMContentLoaded", function () {
    // Function to calculate totals (Amount and Quantity)
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

    var generateReportUrl = document
    .getElementById("generate_url_kitchen")
    .textContent.trim();
  console.log("Initial URL:", generateReportUrl); // Debugging the raw URL

  // Remove the '&amp;' part by replacing it with '&'
  generateReportUrl = generateReportUrl.replace(/&amp;/g, "&");

  
    function validateFilters() {
        console.log("called")
        // Get the 'order_date__gte' and 'order_date__lt' parameters from the URL
        const urlParams = new URLSearchParams(window.location.search);
        const status = urlParams.get("order__status__exact");
        console.log("status ",status)
    
        // console.log(order__status__exact)
        // Check if the status is 'Delivered'
        if (status !== "Pending") {
          alert(
            "Please select the 'Pending' status in the filters before generating the report."
          );
          return false;
        }
        return true
      }
    // Get the status filter element
    document
    .getElementById("download-report")
    .addEventListener("click", function (e) {
      e.preventDefault(); // Prevent the default action
      console.log("called before imgkit")
      if (validateFilters()) {
        console.log(generateReportUrl)
        if (generateReportUrl) {

          window.location.href = generateReportUrl; // Redirect to report generation
        } else {
          console.log(
            "Report generation URL is missing. Please contact the administrator."
          );
        }
      }
    });

})