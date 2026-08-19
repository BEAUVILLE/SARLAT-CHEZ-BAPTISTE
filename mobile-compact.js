(function () {
    "use strict";

    const OCCUPIED_DATES = [
        "2026-08-19",
        "2026-08-26",
        "2026-08-27",
        "2026-08-28",
        "2026-09-15",
        "2026-09-16",
        "2026-09-29"
    ];

    const PERIODS = [
        { start: "2026-08-19", end: "2026-08-19", label: "19 août 2026" },
        { start: "2026-08-26", end: "2026-08-28", label: "26 au 28 août 2026" },
        { start: "2026-09-15", end: "2026-09-16", label: "15 et 16 septembre 2026" },
        { start: "2026-09-29", end: "2026-09-29", label: "29 septembre 2026" }
    ];

    function localTodayISO() {
        const now = new Date();
        return now.getFullYear() + "-" +
            String(now.getMonth() + 1).padStart(2, "0") + "-" +
            String(now.getDate()).padStart(2, "0");
    }

    function activeOccupiedDates() {
        const today = localTodayISO();
        return new Set(OCCUPIED_DATES.filter(date => date >= today));
    }

    function rebuildAvailability() {
        const container = document.querySelector("#reservation .availability");
        if (!container) return;

        const today = localTodayISO();
        container.innerHTML = "";

        PERIODS.filter(period => period.end >= today).forEach(period => {
            const row = document.createElement("div");
            row.className = "period";
            row.dataset.end = period.end;

            const label = document.createElement("span");
            label.textContent = period.label;

            const state = document.createElement("strong");
            state.textContent = "Occupé";

            row.append(label, state);
            container.appendChild(row);
        });

        if (today <= "2026-10-30") {
            const open = document.createElement("div");
            open.className = "period open";
            open.innerHTML = "<span>Autres dates jusqu'au 30 octobre 2026</span><strong>Sur demande</strong>";
            container.appendChild(open);
        }

        const closed = document.createElement("div");
        closed.className = "period";
        closed.innerHTML = "<span>À partir du 31 octobre 2026</span><strong>Fermé</strong>";
        container.appendChild(closed);
    }

    function markCalendar() {
        const blocked = activeOccupiedDates();
        document.querySelectorAll("#calendarGrid .day[data-date]").forEach(day => {
            if (!blocked.has(day.dataset.date)) return;
            day.classList.add("disabled", "blocked");
            day.setAttribute("aria-disabled", "true");
            day.title = "Occupé / indisponible";
        });
    }

    function rangeContainsBlocked(a, b) {
        if (!a || !b) return false;
        const blocked = activeOccupiedDates();
        const start = a < b ? a : b;
        const end = a < b ? b : a;
        return Array.from(blocked).some(date => date >= start && date <= end);
    }

    function showBlockedMessage() {
        const status = document.getElementById("status");
        if (status) status.textContent = "⚠️ Cette sélection traverse une date occupée. Choisissez une autre période.";
    }

    function initCalendarGuard() {
        const grid = document.getElementById("calendarGrid");
        if (!grid) return;

        let pendingStart = null;

        grid.addEventListener("click", event => {
            const day = event.target.closest(".day[data-date]");
            if (!day) return;

            const date = day.dataset.date;
            const blocked = activeOccupiedDates();

            if (blocked.has(date)) {
                event.preventDefault();
                event.stopImmediatePropagation();
                showBlockedMessage();
                return;
            }

            if (day.classList.contains("disabled")) return;

            if (!pendingStart) {
                pendingStart = date;
                return;
            }

            if (rangeContainsBlocked(pendingStart, date)) {
                event.preventDefault();
                event.stopImmediatePropagation();
                showBlockedMessage();
                return;
            }

            pendingStart = null;
        }, true);

        const observer = new MutationObserver(markCalendar);
        observer.observe(grid, { childList: true, subtree: true });
        markCalendar();
    }

    function init() {
        rebuildAvailability();
        initCalendarGuard();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init, { once: true });
    } else {
        init();
    }
})();
