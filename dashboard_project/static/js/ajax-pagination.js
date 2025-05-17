/**
 * ajax-pagination.js - Common JavaScript for AJAX pagination across the application
 *
 * This script handles AJAX-based pagination for all pages in the Chat Analytics Dashboard.
 * It intercepts pagination link clicks, loads content via AJAX, and updates the browser history.
 */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize AJAX pagination
  setupAjaxPagination();

  // Function to set up AJAX pagination for the entire application
  function setupAjaxPagination() {
    // Configuration - can be customized per page if needed
    const config = {
      contentContainerId: "ajax-content-container", // ID of the container to update
      loadingSpinnerId: "ajax-loading-spinner", // ID of the loading spinner
      paginationLinkClass: "pagination-link", // Class for pagination links
      retryMessage: "An error occurred while loading data. Please try again.",
    };

    // Get container elements
    const contentContainer = document.getElementById(config.contentContainerId);
    const loadingSpinner = document.getElementById(config.loadingSpinnerId);

    // Exit if the page doesn't have the required elements
    if (!contentContainer || !loadingSpinner) return;

    // Function to handle pagination clicks
    function setupPaginationListeners() {
      document.querySelectorAll("." + config.paginationLinkClass).forEach((link) => {
        link.addEventListener("click", function (e) {
          e.preventDefault();
          handleAjaxNavigation(this.href);

          // Get the page number if available
          const page = this.getAttribute("data-page");

          // Update browser URL without refreshing
          const newUrl = this.href;
          history.pushState({ url: newUrl, page: page }, "", newUrl);
        });
      });
    }

    // Function to handle AJAX navigation
    function handleAjaxNavigation(url) {
      // Show loading spinner
      contentContainer.classList.add("d-none");
      loadingSpinner.classList.remove("d-none");

      // Fetch data via AJAX
      fetch(url, {
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          if (data.status === "success") {
            // Update the content
            contentContainer.innerHTML = data.html_data;

            // Re-attach event listeners to new pagination links
            setupPaginationListeners();

            // Update any summary data if present and the page provides it
            if (typeof updateSummary === "function" && data.summary) {
              updateSummary(data);
            }

            // Hide loading spinner, show content
            loadingSpinner.classList.add("d-none");
            contentContainer.classList.remove("d-none");

            // Scroll to top of the content container
            contentContainer.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        })
        .catch((error) => {
          console.error("Error fetching data:", error);
          loadingSpinner.classList.add("d-none");
          contentContainer.classList.remove("d-none");
          alert(config.retryMessage);
        });
    }

    // Initial setup of event listeners
    setupPaginationListeners();

    // Handle browser back/forward buttons
    window.addEventListener("popstate", function (event) {
      if (event.state && event.state.url) {
        handleAjaxNavigation(event.state.url);
      } else {
        // If no state, fetch current URL
        handleAjaxNavigation(window.location.href);
      }
    });
  }
});
