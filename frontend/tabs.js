// tabs.js — ES6 module for tab switching
// Handles switching between tab panels (Solar Simulation, Battery Simulation, Cost Analysis)

export function switchTab(tabId) {
    // Hide all panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.hidden = true;
    });

    // Show target panel
    document.getElementById(`panel-${tabId}`).hidden = false;

    // Update active button styling
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('tab-active');
    });
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('tab-active');
}
