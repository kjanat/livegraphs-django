/**
 * ajax-navigation.js - JavaScript for AJAX-based navigation across the entire application
 *
 * This script handles AJAX navigation between pages in the Chat Analytics Dashboard.
 * It intercepts link clicks, loads content via AJAX, and updates the browser history.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Only initialize if AJAX navigation is enabled
    if (typeof ENABLE_AJAX_NAVIGATION !== "undefined" && ENABLE_AJAX_NAVIGATION) {
        setupAjaxNavigation();
    }

    // Function to set up AJAX navigation for the application
    function setupAjaxNavigation() {
        // Configuration
        const config = {
            mainContentSelector: "#main-content", // Selector for the main content area
            navLinkSelector: ".ajax-nav-link", // Selector for links to handle with AJAX
            loadingIndicatorId: "nav-loading-indicator", // ID of the loading indicator
            excludePatterns: [
                // URL patterns to exclude from AJAX navigation
                /\.(pdf|xlsx?|docx?|csv|zip|png|jpe?g|gif|svg)$/i, // File downloads
                /\/admin\//, // Admin pages
                /\/accounts\/logout\//, // Logout page
                /\/api\//, // API endpoints
            ],
        };

        // Create and insert the loading indicator
        if (!document.getElementById(config.loadingIndicatorId)) {
            const loadingIndicator = document.createElement("div");
            loadingIndicator.id = config.loadingIndicatorId;
            loadingIndicator.className = "position-fixed top-0 start-0 end-0";
            loadingIndicator.innerHTML =
                '<div class="progress" style="height: 3px; border-radius: 0;"><div class="progress-bar progress-bar-striped progress-bar-animated bg-primary" style="width: 100%"></div></div>';
            loadingIndicator.style.display = "none";
            loadingIndicator.style.zIndex = "9999";
            document.body.appendChild(loadingIndicator);
        }

        // Get the loading indicator element
        const loadingIndicator = document.getElementById(config.loadingIndicatorId);

        // Get the main content container
        const mainContent = document.querySelector(config.mainContentSelector);
        if (!mainContent) {
            console.warn("Main content container not found. AJAX navigation disabled.");
            return;
        }

        // Function to check if a URL should be excluded from AJAX navigation
        function shouldExcludeUrl(url) {
            for (const pattern of config.excludePatterns) {
                if (pattern.test(url)) {
                    return true;
                }
            }
            return false;
        }

        // Function to show the loading indicator
        function showLoading() {
            loadingIndicator.style.display = "block";
        }

        // Function to hide the loading indicator
        function hideLoading() {
            loadingIndicator.style.display = "none";
        }

        // Function to handle AJAX page navigation
        function handlePageNavigation(url, pushState = true) {
            if (shouldExcludeUrl(url)) {
                window.location.href = url;
                return;
            }
            showLoading();
            const currentScrollPos = window.scrollY;
            fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-AJAX-Navigation": "true",
                    Accept: "text/html",
                },
            })
                .then((response) => {
                    if (!response.ok)
                        throw new Error(`Network response was not ok: ${response.status}`);
                    return response.text();
                })
                .then((html) => {
                    // Parse the HTML and extract #main-content
                    const tempDiv = document.createElement("div");
                    tempDiv.innerHTML = html;
                    const newContent = tempDiv.querySelector(config.mainContentSelector);
                    if (!newContent) throw new Error("Could not find main content in the response");
                    mainContent.innerHTML = newContent.innerHTML;
                    // Update the page title
                    const titleMatch = html.match(/<title>(.*?)<\/title>/i);
                    if (titleMatch) document.title = titleMatch[1];
                    // Re-initialize dynamic content
                    reloadScripts(mainContent);
                    attachEventListeners();
                    initializePageScripts();
                    if (pushState) {
                        history.pushState(
                            { url: url, title: document.title, scrollPos: currentScrollPos },
                            document.title,
                            url,
                        );
                        window.scrollTo({ top: 0, behavior: "smooth" });
                    } else if (window.history.state && window.history.state.scrollPos) {
                        window.scrollTo({ top: window.history.state.scrollPos });
                    }
                    hideLoading();
                })
                .catch((error) => {
                    console.error("Error during AJAX navigation:", error);
                    hideLoading();
                    window.location.href = url;
                });
        }

        // Function to reload and execute scripts in new content
        function reloadScripts(container) {
            const scripts = container.getElementsByTagName("script");
            for (let script of scripts) {
                const newScript = document.createElement("script");

                // Copy all attributes
                Array.from(script.attributes).forEach((attr) => {
                    newScript.setAttribute(attr.name, attr.value);
                });

                // Copy inline script content
                newScript.textContent = script.textContent;

                // Replace old script with new one
                script.parentNode.replaceChild(newScript, script);
            }
        }

        // Function to handle form submissions
        function handleFormSubmission(form, e) {
            e.preventDefault();

            // Show loading indicator
            showLoading();

            // Get form data
            const formData = new FormData(form);
            const method = form.method.toLowerCase();
            const url = form.action || window.location.href;

            // Configure fetch options
            const fetchOptions = {
                method: method,
                headers: {
                    "X-AJAX-Navigation": "true",
                },
            };

            // Handle different HTTP methods
            if (method === "get") {
                const queryParams = new URLSearchParams(formData).toString();
                handlePageNavigation(url + (queryParams ? "?" + queryParams : ""));
            } else {
                fetchOptions.body = formData;

                fetch(url, fetchOptions)
                    .then((response) => {
                        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                        return response.json();
                    })
                    .then((data) => {
                        if (data.redirect) {
                            // Handle server-side redirects
                            handlePageNavigation(data.redirect, true);
                        } else {
                            // Update page content
                            mainContent.innerHTML = data.html;
                            document.title = data.title || document.title;

                            // Re-initialize dynamic content
                            reloadScripts(mainContent);
                            attachEventListeners();
                            initializePageScripts();

                            // Update URL if needed
                            if (data.url) {
                                history.pushState({ url: data.url }, document.title, data.url);
                            }
                        }
                    })
                    .catch((error) => {
                        console.error("Form submission error:", error);
                        // Fallback to traditional form submission
                        form.submit();
                    })
                    .finally(() => {
                        hideLoading();
                    });
            }
        }

        // Function to initialize scripts needed for the new page content
        function initializePageScripts() {
            // Re-initialize any custom scripts that might be needed
            if (typeof setupAjaxPagination === "function") {
                setupAjaxPagination();
            }

            // Initialize Bootstrap tooltips, popovers, etc.
            if (typeof bootstrap !== "undefined") {
                // Initialize tooltips
                const tooltipTriggerList = [].slice.call(
                    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
                );
                tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });

                // Initialize popovers
                const popoverTriggerList = [].slice.call(
                    document.querySelectorAll('[data-bs-toggle="popover"]'),
                );
                popoverTriggerList.map(function (popoverTriggerEl) {
                    return new bootstrap.Popover(popoverTriggerEl);
                });
            }
        }

        // Function to attach event listeners to forms and links
        function attachEventListeners() {
            // Handle AJAX navigation links
            document.querySelectorAll(config.navLinkSelector).forEach((link) => {
                if (!link.dataset.ajaxNavInitialized) {
                    link.addEventListener("click", function (e) {
                        if (e.ctrlKey || e.metaKey || e.shiftKey || shouldExcludeUrl(this.href)) {
                            return; // Let the browser handle these cases
                        }
                        e.preventDefault();
                        handlePageNavigation(this.href);
                    });
                    link.dataset.ajaxNavInitialized = "true";
                }
            });

            // Handle forms with AJAX
            document
                .querySelectorAll("form.ajax-form, form.search-form, form.filter-form")
                .forEach((form) => {
                    if (!form.dataset.ajaxFormInitialized) {
                        form.addEventListener("submit", (e) => handleFormSubmission(form, e));
                        form.dataset.ajaxFormInitialized = "true";
                    }
                });
        }

        // Initial attachment of event listeners
        attachEventListeners();

        // Handle browser back/forward buttons
        window.addEventListener("popstate", function (event) {
            if (event.state && event.state.url) {
                handlePageNavigation(event.state.url, false);
            } else {
                // Fallback to current URL if no state
                handlePageNavigation(window.location.href, false);
            }
        });
    }
});
