(function () {
    "use strict";

    const SUPABASE_URL = "https://wesqmwjjtsefyjnluosj.supabase.co";
    const SUPABASE_KEY = "sb_publishable_tGHItRgeWDmGjnd0CK1DVQ_BIep4Ug3";
    const UNIT_ID = "8e197c74-c789-4ca7-8e95-1927cc617960";
    const LAST_DATE = "2026-10-30";
    const AUTO_REFRESH_MS = 10000;
    const FALLBACK = new Map([
        ["2026-08-19", "occupied"],
        ["2026-08-26", "occupied"],
        ["2026-08-27", "occupied"],
        ["2026-08-28", "occupied"],
        ["2026-09-05", "closed"],
        ["2026-09-15", "occupied"],
        ["2026-09-16", "occupied"],
        ["2026-09-24", "closed"],
        ["2026-09-29", "occupied"]
    ]);

    let states = new Map(FALLBACK);
    let selectedStart = null;
    let selectedEnd = null;
    let observer = null;

    function localTodayISO() {
        const now = new Date();
        return now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0");
    }

    function parseISO(value) {
        const parts = value.split("-").map(Number);
        return new Date(parts[0], parts[1] - 1, parts[2], 12, 0, 0, 0);
    }

    function iso(date) {
        return date.getFullYear() + "-" + String(date.getMonth() + 1).padStart(2, "0") + "-" + String(date.getDate()).padStart(2, "0");
    }

    function datesBetween(a, b) {
        const start = parseISO(a <= b ? a : b);
        const end = parseISO(a <= b ? b : a);
        const out = [];
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) out.push(iso(d));
        return out;
    }

    function activeState(date) {
        if (date < localTodayISO()) return null;
        return states.get(date) || null;
    }

    function rangeContainsBlocked(a, b) {
        return datesBetween(a, b).some(date => activeState(date));
    }

    async function fetchStates() {
        const params = new URLSearchParams();
        params.append("unit_id", "eq." + UNIT_ID);
        params.append("day", "gte." + localTodayISO());
        params.append("day", "lte." + LAST_DATE);
        params.append("select", "day,status");
        params.append("order", "day.asc");

        try {
            const response = await fetch(SUPABASE_URL + "/rest/v1/digiy_loc_master_unit_calendar?" + params.toString(), {
                headers: { "apikey": SUPABASE_KEY, "Accept": "application/json" },
                cache: "no-store"
            });
            if (!response.ok) throw new Error("HTTP " + response.status);
            const rows = await response.json();
            states = new Map((rows || []).map(row => [row.day, row.status]));
        } catch (_) {
            states = new Map(Array.from(FALLBACK).filter(([date]) => date >= localTodayISO()));
        }

        rebuildAvailability();
        syncCalendarGrid();
    }

    function groupStates() {
        const entries = Array.from(states.entries())
            .filter(([day]) => day >= localTodayISO() && day <= LAST_DATE)
            .sort((a, b) => a[0].localeCompare(b[0]));
        const groups = [];
        for (const [day, status] of entries) {
            const last = groups[groups.length - 1];
            if (last && last.status === status) {
                const expected = new Date(parseISO(last.end));
                expected.setDate(expected.getDate() + 1);
                if (iso(expected) === day) {
                    last.end = day;
                    continue;
                }
            }
            groups.push({ start: day, end: day, status });
        }
        return groups;
    }

    function periodLabel(startISO, endISO) {
        const start = parseISO(startISO), end = parseISO(endISO);
        if (startISO === endISO) return start.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
        if (start.getFullYear() === end.getFullYear() && start.getMonth() === end.getMonth()) {
            return start.getDate() + " au " + end.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
        }
        return start.toLocaleDateString("fr-FR", { day: "numeric", month: "long" }) + " au " + end.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
    }

    function rebuildAvailability() {
        const container = document.querySelector("#reservation .availability");
        if (!container) return;
        container.innerHTML = "";

        groupStates().forEach(group => {
            const row = document.createElement("div");
            row.className = "period";
            row.dataset.end = group.end;
            const label = document.createElement("span");
            label.textContent = periodLabel(group.start, group.end);
            const state = document.createElement("strong");
            state.textContent = group.status === "closed" ? "Fermé" : "Occupé";
            if (group.status === "closed") state.style.color = "#25190f";
            row.append(label, state);
            container.appendChild(row);
        });

        if (localTodayISO() <= LAST_DATE) {
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

    function updateSelectionDisplay() {
        const dateRange = document.getElementById("dateRange");
        const nightsDisplay = document.getElementById("nightsDisplay");
        const arrival = document.getElementById("arrival");
        const departure = document.getElementById("departure");
        const estimate = document.getElementById("estimate");

        document.querySelectorAll("#calendarGrid .day[data-date]").forEach(day => {
            day.classList.remove("selected-start", "selected-end", "in-range");
            if (!selectedStart) return;
            const value = day.dataset.date;
            const effectiveEnd = selectedEnd || selectedStart;
            if (value === selectedStart) day.classList.add("selected-start");
            if (selectedEnd && value === selectedEnd) day.classList.add("selected-end");
            if (selectedEnd && value > selectedStart && value < selectedEnd) day.classList.add("in-range");
            if (effectiveEnd < selectedStart) return;
        });

        if (!selectedStart || !selectedEnd) {
            if (dateRange) dateRange.textContent = selectedStart ? "📅 " + parseISO(selectedStart).toLocaleDateString("fr-FR", { day: "numeric", month: "short" }) + " → choisissez le départ" : "📅 Sélectionnez vos dates";
            if (nightsDisplay) nightsDisplay.textContent = "🛏️ —";
            if (arrival) arrival.value = selectedStart || "";
            if (departure) departure.value = "";
            if (estimate) estimate.innerHTML = "<strong>78 € / nuitée</strong><span>≈ 51 165 FCFA · choisissez vos dates.</span>";
            return;
        }

        const start = parseISO(selectedStart), end = parseISO(selectedEnd);
        const nights = Math.round((end - start) / 86400000);
        if (dateRange) dateRange.textContent = "📅 " + start.toLocaleDateString("fr-FR", { day: "numeric", month: "short" }) + " → " + end.toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
        if (nightsDisplay) nightsDisplay.textContent = "🛏️ " + nights + (nights === 1 ? " nuit" : " nuits");
        if (arrival) arrival.value = selectedStart;
        if (departure) departure.value = selectedEnd;
        if (estimate) estimate.innerHTML = "<strong>" + nights + " nuitée(s) : " + (nights * 78).toLocaleString("fr-FR") + " €</strong><span>≈ " + (nights * 51165).toLocaleString("fr-FR") + " FCFA</span>";
    }

    function syncCalendarGrid() {
        const today = localTodayISO();
        document.querySelectorAll("#calendarGrid .day[data-date]").forEach(day => {
            const value = day.dataset.date;
            const state = activeState(value);

            day.classList.remove("blocked");
            day.removeAttribute("aria-disabled");
            day.removeAttribute("title");

            if (value < today || value > LAST_DATE) {
                day.classList.add("disabled");
            } else if (state) {
                day.classList.add("disabled", "blocked");
                day.setAttribute("aria-disabled", "true");
                day.title = state === "closed" ? "Fermé" : "Occupé / indisponible";
            } else {
                day.classList.remove("disabled");
            }
        });
        updateSelectionDisplay();
    }

    function showMessage(text) {
        const status = document.getElementById("status");
        if (status) status.textContent = text;
    }

    function chooseDate(value) {
        if (activeState(value)) return showMessage("⚠️ Cette date est occupée ou fermée.");
        if (!selectedStart || selectedEnd) {
            selectedStart = value;
            selectedEnd = null;
            showMessage("");
        } else {
            let a = selectedStart, b = value;
            if (b < a) [a, b] = [b, a];
            if (a === b) return showMessage("⚠️ Choisissez une date de départ après l'arrivée.");
            if (rangeContainsBlocked(a, b)) return showMessage("⚠️ Cette période traverse une date occupée ou fermée.");
            selectedStart = a;
            selectedEnd = b;
            showMessage("");
        }
        syncCalendarGrid();
    }

    function validateCurrentRange(event) {
        const arrival = document.getElementById("arrival");
        const departure = document.getElementById("departure");
        if (!arrival || !departure || !arrival.value || !departure.value) return;
        if (!rangeContainsBlocked(arrival.value, departure.value)) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        showMessage("⚠️ Cette période n'est plus disponible. Choisissez d'autres dates.");
    }

    function initCalendarControl() {
        const grid = document.getElementById("calendarGrid");
        if (!grid) return;

        grid.addEventListener("click", event => {
            const day = event.target.closest(".day[data-date]");
            if (!day) return;
            event.preventDefault();
            event.stopImmediatePropagation();
            if (day.dataset.date < localTodayISO() || day.dataset.date > LAST_DATE) return;
            chooseDate(day.dataset.date);
        }, true);

        observer = new MutationObserver(syncCalendarGrid);
        observer.observe(grid, { childList: true, subtree: true });
        syncCalendarGrid();

        const form = document.getElementById("requestForm");
        if (form) form.addEventListener("submit", validateCurrentRange, true);
        const emailRequest = document.getElementById("emailRequest");
        if (emailRequest) emailRequest.addEventListener("click", validateCurrentRange, true);
    }

    function init() {
        rebuildAvailability();
        initCalendarControl();
        fetchStates();
        window.setInterval(() => { if (!document.hidden) fetchStates(); }, AUTO_REFRESH_MS);
        window.addEventListener("focus", fetchStates);
        document.addEventListener("visibilitychange", () => { if (!document.hidden) fetchStates(); });
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
    else init();
})();
