/**
 * main.js - Global JavaScript functionality
 *
 * This file contains general JavaScript functionality used across
 * the entire application, including navigation, forms, and UI interactions.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Toggle sidebar on mobile
    const sidebarToggle = document.querySelector("#sidebarToggle");
    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", function () {
            document.querySelector(".sidebar").classList.toggle("show");
        });
    }

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function () {
        var alerts = document.querySelectorAll(".alert:not(.alert-important)");
        alerts.forEach(function (alert) {
            if (alert && bootstrap.Alert.getInstance(alert)) {
                bootstrap.Alert.getInstance(alert).close();
            }
        });
    }, 5000);

    // Form validation
    const forms = document.querySelectorAll(".needs-validation");
    forms.forEach(function (form) {
        form.addEventListener(
            "submit",
            function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add("was-validated");
            },
            false,
        );
    });

    // Confirm dialogs
    const confirmButtons = document.querySelectorAll("[data-confirm]");
    confirmButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            if (!confirm(this.dataset.confirm || "Are you sure?")) {
                event.preventDefault();
            }
        });
    });

    // Back button
    const backButtons = document.querySelectorAll(".btn-back");
    backButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            window.history.back();
        });
    });

    // File input customization
    const fileInputs = document.querySelectorAll(".custom-file-input");
    fileInputs.forEach(function (input) {
        input.addEventListener("change", function (e) {
            const fileName = this.files[0]?.name || "Choose file";
            const nextSibling = this.nextElementSibling;
            if (nextSibling) {
                nextSibling.innerText = fileName;
            }
        });
    });

    // Search form submit on enter
    const searchInputs = document.querySelectorAll(".search-input");
    searchInputs.forEach(function (input) {
        input.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                this.closest("form").submit();
            }
        });
    });

    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll(".toggle-password");
    togglePasswordButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const target = document.querySelector(this.dataset.target);
            if (target) {
                const type = target.getAttribute("type") === "password" ? "text" : "password";
                target.setAttribute("type", type);
                this.querySelector("i").classList.toggle("fa-eye");
                this.querySelector("i").classList.toggle("fa-eye-slash");
            }
        });
    });

    // Dropdown menu positioning
    const dropdowns = document.querySelectorAll(".dropdown-menu");
    dropdowns.forEach(function (dropdown) {
        dropdown.addEventListener("click", function (e) {
            e.stopPropagation();
        });
    });

    // Responsive table handling
    const tables = document.querySelectorAll(".table-responsive");
    if (window.innerWidth < 768) {
        tables.forEach(function (table) {
            table.classList.add("table-responsive-force");
        });
    }

    // Handle special links (printable views, exports)
    const printLinks = document.querySelectorAll(".print-link");
    printLinks.forEach(function (link) {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            window.print();
        });
    });

    const exportLinks = document.querySelectorAll("[data-export]");
    exportLinks.forEach(function (link) {
        link.addEventListener("click", function (e) {
            // Handle export functionality if needed
            console.log("Export requested:", this.dataset.export);
        });
    });

    // Handle sidebar collapse on small screens
    function handleSidebarOnResize() {
        if (window.innerWidth < 768) {
            document.querySelector(".sidebar")?.classList.remove("show");
        }
    }

    window.addEventListener("resize", handleSidebarOnResize);
});
