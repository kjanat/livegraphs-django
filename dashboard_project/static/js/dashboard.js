/**
 * dashboard.js - JavaScript for the dashboard functionality
 *
 * This file handles the interactive features of the dashboard,
 * including chart refreshing, dashboard filtering, and dashboard
 * customization.
 */

document.addEventListener("DOMContentLoaded", function () {
  // Chart responsiveness
  function resizeCharts() {
    const charts = document.querySelectorAll(".chart-container");
    charts.forEach((chart) => {
      if (chart.id && window.Plotly) {
        Plotly.relayout(chart.id, {
          "xaxis.automargin": true,
          "yaxis.automargin": true,
        });
      }
    });
  }

  // Handle window resize
  window.addEventListener("resize", function () {
    if (window.Plotly) {
      resizeCharts();
    }
  });

  // Time range filtering
  const timeRangeDropdown = document.getElementById("timeRangeDropdown");
  if (timeRangeDropdown) {
    const timeRangeLinks = timeRangeDropdown.querySelectorAll(".dropdown-item");
    timeRangeLinks.forEach((link) => {
      link.addEventListener("click", function (e) {
        const url = new URL(this.href);
        const dashboardId = url.searchParams.get("dashboard_id");
        const timeRange = url.searchParams.get("time_range");

        // Fetch updated data via AJAX
        if (dashboardId) {
          fetchDashboardData(dashboardId, timeRange);
          e.preventDefault();
        }
      });
    });
  }

  // Function to fetch dashboard data
  function fetchDashboardData(dashboardId, timeRange) {
    const loadingOverlay = document.createElement("div");
    loadingOverlay.className = "loading-overlay";
    loadingOverlay.innerHTML =
      '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.querySelector("main").appendChild(loadingOverlay);

    fetch(`/dashboard/api/dashboard/${dashboardId}/data/?time_range=${timeRange || "all"}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Network response was not ok: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Dashboard API response:", data);
        updateDashboardStats(data);
        updateDashboardCharts(data);

        // Update URL without page reload
        const url = new URL(window.location.href);
        url.searchParams.set("dashboard_id", dashboardId);
        if (timeRange) {
          url.searchParams.set("time_range", timeRange);
        }
        window.history.pushState({}, "", url);

        document.querySelector(".loading-overlay").remove();
      })
      .catch((error) => {
        console.error("Error fetching dashboard data:", error);
        document.querySelector(".loading-overlay").remove();

        // Show error message
        const alertElement = document.createElement("div");
        alertElement.className = "alert alert-danger alert-dismissible fade show";
        alertElement.setAttribute("role", "alert");
        alertElement.innerHTML = `
                    Error loading dashboard data. Please try again.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
        document.querySelector("main").prepend(alertElement);
      });
  }

  // Function to update dashboard statistics
  function updateDashboardStats(data) {
    // Update total sessions
    const totalSessionsElement = document.querySelector(".stats-card:nth-child(1) h3");
    if (totalSessionsElement) {
      totalSessionsElement.textContent = data.total_sessions;
    }

    // Update average response time
    const avgResponseTimeElement = document.querySelector(".stats-card:nth-child(2) h3");
    if (avgResponseTimeElement) {
      avgResponseTimeElement.textContent = data.avg_response_time + "s";
    }

    // Update total tokens
    const totalTokensElement = document.querySelector(".stats-card:nth-child(3) h3");
    if (totalTokensElement) {
      totalTokensElement.textContent = data.total_tokens;
    }

    // Update total cost
    const totalCostElement = document.querySelector(".stats-card:nth-child(4) h3");
    if (totalCostElement) {
      totalCostElement.textContent = "€" + data.total_cost;
    }
  }

  // Function to update dashboard charts
  function updateDashboardCharts(data) {
    // Check if Plotly is available
    if (!window.Plotly) {
      console.error("Plotly library not loaded!");
      document.querySelectorAll(".chart-container").forEach((container) => {
        container.innerHTML =
          '<div class="text-center py-5"><p class="text-danger">Chart library not available. Please refresh the page.</p></div>';
      });
      return;
    }

    // Update sessions over time chart
    const timeSeriesData = data.time_series_data;
    if (timeSeriesData && timeSeriesData.length > 0) {
      try {
        const timeSeriesX = timeSeriesData.map((item) => item.date);
        const timeSeriesY = timeSeriesData.map((item) => item.count);

        Plotly.react(
          "sessions-time-chart",
          [
            {
              x: timeSeriesX,
              y: timeSeriesY,
              type: "scatter",
              mode: "lines+markers",
              line: {
                color: "rgb(75, 192, 192)",
                width: 2,
              },
              marker: {
                color: "rgb(75, 192, 192)",
                size: 6,
              },
            },
          ],
          {
            margin: { t: 10, r: 10, b: 40, l: 40 },
            xaxis: {
              title: "Date",
            },
            yaxis: {
              title: "Number of Sessions",
            },
          }
        );
      } catch (error) {
        console.error("Error rendering time series chart:", error);
        document.getElementById("sessions-time-chart").innerHTML =
          '<div class="text-center py-5"><p class="text-danger">Error rendering chart.</p></div>';
      }
    } else {
      document.getElementById("sessions-time-chart").innerHTML =
        '<div class="text-center py-5"><p class="text-muted">No time series data available</p></div>';
    }

    // Update sentiment chart
    const sentimentData = data.sentiment_data;
    if (sentimentData && sentimentData.length > 0 && window.Plotly) {
      const sentimentLabels = sentimentData.map((item) => item.sentiment);
      const sentimentValues = sentimentData.map((item) => item.count);
      const sentimentColors = sentimentLabels.map((sentiment) => {
        if (sentiment.toLowerCase().includes("positive")) return "rgb(75, 192, 92)";
        if (sentiment.toLowerCase().includes("negative")) return "rgb(255, 99, 132)";
        if (sentiment.toLowerCase().includes("neutral")) return "rgb(255, 205, 86)";
        return "rgb(201, 203, 207)";
      });

      Plotly.react(
        "sentiment-chart",
        [
          {
            values: sentimentValues,
            labels: sentimentLabels,
            type: "pie",
            marker: {
              colors: sentimentColors,
            },
            hole: 0.4,
            textinfo: "label+percent",
            insidetextorientation: "radial",
          },
        ],
        {
          margin: { t: 10, r: 10, b: 10, l: 10 },
        }
      );
    }

    // Update country chart
    const countryData = data.country_data;
    if (countryData && countryData.length > 0 && window.Plotly) {
      const countryLabels = countryData.map((item) => item.country);
      const countryValues = countryData.map((item) => item.count);

      Plotly.react(
        "country-chart",
        [
          {
            x: countryValues,
            y: countryLabels,
            type: "bar",
            orientation: "h",
            marker: {
              color: "rgb(54, 162, 235)",
            },
          },
        ],
        {
          margin: { t: 10, r: 10, b: 40, l: 100 },
          xaxis: {
            title: "Number of Sessions",
          },
        }
      );
    }

    // Update category chart
    const categoryData = data.category_data;
    if (categoryData && categoryData.length > 0 && window.Plotly) {
      const categoryLabels = categoryData.map((item) => item.category);
      const categoryValues = categoryData.map((item) => item.count);

      Plotly.react(
        "category-chart",
        [
          {
            labels: categoryLabels,
            values: categoryValues,
            type: "pie",
            textinfo: "label+percent",
            insidetextorientation: "radial",
          },
        ],
        {
          margin: { t: 10, r: 10, b: 10, l: 10 },
        }
      );
    }
  }

  // Dashboard selector
  const dashboardSelector = document.querySelectorAll('a[href^="?dashboard_id="]');
  dashboardSelector.forEach((link) => {
    link.addEventListener("click", function (e) {
      const url = new URL(this.href);
      const dashboardId = url.searchParams.get("dashboard_id");

      // Fetch updated data via AJAX
      if (dashboardId) {
        fetchDashboardData(dashboardId);
        e.preventDefault();
      }
    });
  });
});
