// tabs.js — ES6 module for tab switching
// Handles switching between tab panels (Solar Simulation, Battery Simulation, Cost Analysis)
// Includes keyboard navigation: Arrow keys for tab switching, Tab key for focus order

let keyboardInitialized = false;

export function switchTab(tabId) {
    // Validate tab ID format and existence before switching
    if (!tabId || typeof tabId !== 'string') {
        console.error(`Invalid tab ID: "${tabId}" must be a non-empty string`);
        return;
    }

    const targetPanel = document.getElementById(`panel-${tabId}`);
    const activeTab = document.querySelector(`[data-tab="${tabId}"]`);

    if (!targetPanel) {
        console.error(`Tab panel "panel-${tabId}" not found in DOM`);
        return;
    }
    if (!activeTab) {
        console.error(`Tab button with data-tab="${tabId}" not found in DOM`);
        return;
    }

    // Hide all panels and update ARIA state
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.hidden = true;
    });

    // Show target panel
    targetPanel.hidden = false;

    // Update active button styling and ARIA attributes
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('tab-active');
        btn.setAttribute('aria-selected', 'false');
    });
    activeTab.classList.add('tab-active');
    activeTab.setAttribute('aria-selected', 'true');
}

// Initialize keyboard navigation for tabs (prevent duplicate initialization)
export function initTabKeyboard() {
    if (keyboardInitialized) return;
    keyboardInitialized = true;

    const tabs = document.querySelectorAll('[role="tab"]');
    const tabArray = Array.from(tabs);

    tabs.forEach((tab, index) => {
        tab.addEventListener('keydown', (e) => {
            let targetIndex = index;

            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    // Move to previous tab, wrapping to last if at first
                    targetIndex = (index - 1 + tabArray.length) % tabArray.length;
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    // Move to next tab, wrapping to first if at last
                    targetIndex = (index + 1) % tabArray.length;
                    break;
                case 'Home':
                    e.preventDefault();
                    targetIndex = 0;
                    break;
                case 'End':
                    e.preventDefault();
                    targetIndex = tabArray.length - 1;
                    break;
                default:
                    return; // Don't handle other keys
            }

            // Move focus to the target tab
            const targetTab = tabArray[targetIndex];
            targetTab.focus();

            // Switch to the target tab's panel
            const tabId = targetTab.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
}
