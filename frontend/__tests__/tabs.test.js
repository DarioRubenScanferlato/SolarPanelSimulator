const { switchTab } = require('../tabs.js');

describe('tabs.js', () => {
  beforeEach(() => {
    // Setup HTML structure matching index.html
    document.body.innerHTML = `
      <nav class="tab-nav">
        <button class="tab-btn tab-active" data-tab="solar">Solar Simulation</button>
        <button class="tab-btn" data-tab="battery">Battery Simulation</button>
        <button class="tab-btn" data-tab="cost">Cost Analysis</button>
      </nav>
      <section id="panel-solar" class="tab-panel">Solar Panel Content</section>
      <section id="panel-battery" class="tab-panel" hidden>Battery Content</section>
      <section id="panel-cost" class="tab-panel" hidden>Cost Analysis Content</section>
    `;
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('switchTab', () => {
    test('shows solar panel when switching to solar', () => {
      const solarPanel = document.getElementById('panel-solar');
      solarPanel.setAttribute('hidden', '');

      switchTab('solar');

      expect(solarPanel.hasAttribute('hidden')).toBe(false);
    });

    test('shows battery panel when switching to battery', () => {
      const batteryPanel = document.getElementById('panel-battery');

      switchTab('battery');

      expect(batteryPanel.hasAttribute('hidden')).toBe(false);
    });

    test('shows cost panel when switching to cost', () => {
      const costPanel = document.getElementById('panel-cost');

      switchTab('cost');

      expect(costPanel.hasAttribute('hidden')).toBe(false);
    });

    test('hides other panels when switching to solar', () => {
      switchTab('solar');

      const batteryPanel = document.getElementById('panel-battery');
      const costPanel = document.getElementById('panel-cost');

      expect(batteryPanel.hasAttribute('hidden')).toBe(true);
      expect(costPanel.hasAttribute('hidden')).toBe(true);
    });

    test('hides other panels when switching to battery', () => {
      switchTab('battery');

      const solarPanel = document.getElementById('panel-solar');
      const costPanel = document.getElementById('panel-cost');

      expect(solarPanel.hasAttribute('hidden')).toBe(true);
      expect(costPanel.hasAttribute('hidden')).toBe(true);
    });

    test('hides other panels when switching to cost', () => {
      switchTab('cost');

      const solarPanel = document.getElementById('panel-solar');
      const batteryPanel = document.getElementById('panel-battery');

      expect(solarPanel.hasAttribute('hidden')).toBe(true);
      expect(batteryPanel.hasAttribute('hidden')).toBe(true);
    });
  });

  describe('Tab button active state', () => {
    test('applies tab-active class to solar button', () => {
      const solarBtn = document.querySelector('[data-tab="solar"]');
      solarBtn.classList.remove('tab-active');

      switchTab('solar');

      expect(solarBtn.classList.contains('tab-active')).toBe(true);
    });

    test('applies tab-active class to battery button', () => {
      const batteryBtn = document.querySelector('[data-tab="battery"]');

      switchTab('battery');

      expect(batteryBtn.classList.contains('tab-active')).toBe(true);
    });

    test('applies tab-active class to cost button', () => {
      const costBtn = document.querySelector('[data-tab="cost"]');

      switchTab('cost');

      expect(costBtn.classList.contains('tab-active')).toBe(true);
    });

    test('removes tab-active class from other buttons when switching to solar', () => {
      switchTab('battery');
      switchTab('solar');

      const batteryBtn = document.querySelector('[data-tab="battery"]');
      const costBtn = document.querySelector('[data-tab="cost"]');

      expect(batteryBtn.classList.contains('tab-active')).toBe(false);
      expect(costBtn.classList.contains('tab-active')).toBe(false);
    });

    test('removes tab-active class from other buttons when switching to battery', () => {
      switchTab('battery');

      const solarBtn = document.querySelector('[data-tab="solar"]');
      const costBtn = document.querySelector('[data-tab="cost"]');

      expect(solarBtn.classList.contains('tab-active')).toBe(false);
      expect(costBtn.classList.contains('tab-active')).toBe(false);
    });
  });

  describe('Multiple tab switches', () => {
    test('maintains correct state when switching between all tabs', () => {
      // Start at solar (initial state)
      expect(document.getElementById('panel-solar').hasAttribute('hidden')).toBe(false);
      expect(document.querySelector('[data-tab="solar"]').classList.contains('tab-active')).toBe(true);

      // Switch to battery
      switchTab('battery');
      expect(document.getElementById('panel-battery').hasAttribute('hidden')).toBe(false);
      expect(document.querySelector('[data-tab="battery"]').classList.contains('tab-active')).toBe(true);
      expect(document.getElementById('panel-solar').hasAttribute('hidden')).toBe(true);

      // Switch to cost
      switchTab('cost');
      expect(document.getElementById('panel-cost').hasAttribute('hidden')).toBe(false);
      expect(document.querySelector('[data-tab="cost"]').classList.contains('tab-active')).toBe(true);
      expect(document.getElementById('panel-battery').hasAttribute('hidden')).toBe(true);

      // Switch back to solar
      switchTab('solar');
      expect(document.getElementById('panel-solar').hasAttribute('hidden')).toBe(false);
      expect(document.querySelector('[data-tab="solar"]').classList.contains('tab-active')).toBe(true);
      expect(document.getElementById('panel-cost').hasAttribute('hidden')).toBe(true);
    });

    test('switching to same tab twice maintains correct state', () => {
      switchTab('battery');
      switchTab('battery');

      expect(document.getElementById('panel-battery').hasAttribute('hidden')).toBe(false);
      expect(document.querySelector('[data-tab="battery"]').classList.contains('tab-active')).toBe(true);
      expect(document.getElementById('panel-solar').hasAttribute('hidden')).toBe(true);
    });
  });
});
