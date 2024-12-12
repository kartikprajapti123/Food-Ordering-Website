document.addEventListener("DOMContentLoaded", function () {
  console.log("JavaScript is running on this page!");

  // Get the total amount element
  const totalAmountElement = document.getElementById("total-amount");
  if (!totalAmountElement) {
    console.error("The #total-amount element is missing!");
    return;
  }
  console.log("Found #total-amount element:", totalAmountElement);

  // Get the generate_report_url passed from Django and decode it
  var generateReportUrl = document
    .getElementById("generateReportUrl")
    .textContent.trim();
  console.log("Initial URL:", generateReportUrl); // Debugging the raw URL

  // Remove the '&amp;' part by replacing it with '&'
  generateReportUrl = generateReportUrl.replace(/&amp;/g, "&");

  var generateBulkOrderReportUrl = document
    .getElementById("generateBulkOrderReportUrl")
    .textContent.trim();
  console.log("Initial URL:", generateBulkOrderReportUrl); // Debugging the raw URL

  // Remove the '&amp;' part by replacing it with '&'
  generateBulkOrderReportUrl = generateBulkOrderReportUrl.replace(/&amp;/g, "&");

  // Function to validate required filters
  function validateFilters() {
    // Get the 'order_date__gte' and 'order_date__lt' parameters from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const dateFilterGte = urlParams.get("order_date__gte");
    const dateFilterLt = urlParams.get("order_date__lt");
    const status = urlParams.get("status__exact");
    const agencyFilter = urlParams.get("user__id__exact");

    console.log("Current status filter:", status);
    console.log("order_date__gte:", dateFilterGte);
    console.log("order_date__lt:", dateFilterLt);

    // Check if the status is 'Delivered'
    if (status !== "Delivered") {
      alert(
        "Please select the 'Delivered' status in the filters before generating the report."
      );
      return false;
    }

    // Check if the date range is for today (single day)
    const dateFilterStart = urlParams.get("order_date__gte"); // Start date
    const dateFilterEnd = urlParams.get("order_date__lt"); // End date

    if (dateFilterStart && dateFilterEnd) {
      const startDate = new Date(dateFilterStart);
      const endDate = new Date(dateFilterEnd);

      // Calculate the difference between the two dates
      const timeDifference = endDate - startDate;
      const oneDayInMs = 1000 * 60 * 60 * 24;

      // Check if the date range is exactly 8 days
      if (timeDifference !== 8 * oneDayInMs) {
        alert(
            "Please select the 'Past 7 days' date range in the filters before generating the report."

        );
        return false;
      }
    } else {
      alert(
        "Please select the 'Past 7 days' date range in the filters before generating the report."
      );
      return false;
    }
    // Check if the 'agency' filter is applied
    if (!agencyFilter) {
      alert("Please select the 'Agency' filter before generating the report.");
      return false;
    }

    return true;
  }

  function BulkOrdervalidateFilters() {
    // Get the 'order_date__gte' and 'order_date__lt' parameters from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const status = urlParams.get("status__exact");

    // Check if the status is 'Delivered'
    if (status !== "Delivered") {
      alert(
        "Please select the 'Delivered' status in the filters before generating the 'Bulk Orders Receipt'."
      );
      return false;
    }

    return true
  }

  // Function to handle the 'Generate Report' button click
  document
    .getElementById("download-report")
    .addEventListener("click", function (e) {
      e.preventDefault(); // Prevent the default action

      if (validateFilters()) {
        if (generateReportUrl) {
          window.location.href = generateReportUrl; // Redirect to report generation
        } else {
          console.log(
            "Report generation URL is missing. Please contact the administrator."
          );
        }
      }
    });

    document
    .getElementById("download-bulk-order-report")
    .addEventListener("click", function (e) {
      e.preventDefault(); // Prevent the default action
      if (BulkOrdervalidateFilters()) {
        if (generateBulkOrderReportUrl) {
          window.location.href = generateBulkOrderReportUrl; // Redirect to report generation
        } else {
          console.log(
            "Report generation URL is missing. Please contact the administrator."
          );
        }
      }
    });
  // Initial calculation of total amount (if needed)
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
