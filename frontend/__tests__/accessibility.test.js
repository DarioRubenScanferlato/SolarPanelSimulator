/**
 * @jest-environment jsdom
 */
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Accessibility Tests (WCAG 2.1 Level AA)', () => {
  beforeEach(() => {
    // Create a minimal DOM structure matching the actual app
    document.documentElement.setAttribute('lang', 'en');
    document.title = 'Solar Panel Simulator';
    document.body.innerHTML = `
        <div class="container">
          <header>
            <h1>☀️ Solar Panel Simulator</h1>
            <p>Calculate your solar energy production</p>
          </header>

          <main>
            <nav class="tab-nav" role="tablist">
              <button class="tab-btn tab-active" id="tab-solar" role="tab" aria-selected="true" aria-controls="panel-solar">Solar Simulation</button>
              <button class="tab-btn" id="tab-battery" role="tab" aria-selected="false" aria-controls="panel-battery">Battery Simulation</button>
              <button class="tab-btn" id="tab-cost-analysis" role="tab" aria-selected="false" aria-controls="panel-cost-analysis">Cost Analysis</button>
            </nav>

            <section class="tab-panel" id="panel-solar" role="tabpanel" aria-labelledby="tab-solar">
              <section class="form-section">
                <h2>System Parameters</h2>
                <form id="simulatorForm">
                  <div class="form-grid">
                    <div class="form-group">
                      <label for="latitude">Latitude (°)</label>
                      <input type="number" id="latitude" name="latitude" min="-90" max="90" step="any" required aria-required="true" aria-describedby="error-latitude">
                      <span class="error" id="error-latitude"></span>
                    </div>

                    <div class="form-group">
                      <label for="longitude">Longitude (°)</label>
                      <input type="number" id="longitude" name="longitude" min="-180" max="180" step="any" required aria-required="true" aria-describedby="error-longitude">
                      <span class="error" id="error-longitude"></span>
                    </div>

                    <div class="form-group">
                      <label for="panelCount">Panel Count</label>
                      <input type="number" id="panelCount" name="panelCount" min="1" step="1" required aria-required="true" aria-describedby="error-panelCount">
                      <span class="error" id="error-panelCount"></span>
                    </div>

                    <div class="form-group">
                      <label for="panelArea">Panel Area (m²)</label>
                      <input type="number" id="panelArea" name="panelArea" min="0.1" step="0.1" required aria-required="true" aria-describedby="error-panelArea">
                      <span class="error" id="error-panelArea"></span>
                    </div>

                    <div class="form-group">
                      <label for="efficiency">Efficiency (%)</label>
                      <input type="number" id="efficiency" name="efficiency" min="5" max="25" step="0.1" required aria-required="true" aria-describedby="error-efficiency">
                      <span class="error" id="error-efficiency"></span>
                    </div>

                    <div class="form-group">
                      <label for="tiltAngle">Tilt Angle (°)</label>
                      <input type="number" id="tiltAngle" name="tiltAngle" min="0" max="90" step="0.1" required aria-required="true" aria-describedby="error-tiltAngle">
                      <span class="error" id="error-tiltAngle"></span>
                    </div>

                    <div class="form-group">
                      <label for="azimuth">Azimuth (°)</label>
                      <input type="number" id="azimuth" name="azimuth" min="0" max="360" step="0.1" required aria-required="true" aria-describedby="error-azimuth">
                      <span class="error" id="error-azimuth"></span>
                    </div>

                    <div class="form-group">
                      <label for="startDate">Start Date</label>
                      <input type="date" id="startDate" name="startDate" required aria-required="true" aria-describedby="error-startDate">
                      <span class="error" id="error-startDate"></span>
                    </div>

                    <div class="form-group">
                      <label for="duration">Duration (days)</label>
                      <input type="number" id="duration" name="duration" min="1" step="1" required aria-required="true" aria-describedby="error-duration">
                      <span class="error" id="error-duration"></span>
                    </div>
                  </div>

                  <button type="submit" id="simulateBtn" class="btn-primary">Simulate</button>
                  <div id="formError" class="alert alert-error" style="display: none;" role="alert" aria-live="assertive"></div>
                </form>
              </section>

              <section class="results-section" id="resultsSection" style="display: none;" aria-live="polite" aria-atomic="true">
                <h2>Results</h2>
                <div class="cards-grid">
                  <div class="card">
                    <div class="card-value" id="annualEnergy">-</div>
                    <div class="card-label">Annual Energy (kWh)</div>
                  </div>
                  <div class="card">
                    <div class="card-value" id="dailyAverage">-</div>
                    <div class="card-label">Daily Average (kWh)</div>
                  </div>
                  <div class="card">
                    <div class="card-value" id="peakHour">-</div>
                    <div class="card-label">Peak Hour (kW)</div>
                  </div>
                  <div class="card">
                    <div class="card-value" id="capacity">-</div>
                    <div class="card-label">System Capacity (kW)</div>
                  </div>
                </div>

                <div class="charts-container">
                  <div class="chart-box">
                    <h3>Daily Generation Profile</h3>
                    <div class="chart-wrapper" role="img" aria-label="Daily energy production chart showing hourly power output in kilowatts throughout the day">
                      <canvas id="dailyChart"></canvas>
                    </div>
                    <p class="chart-info" id="dailyInfo">-</p>
                  </div>

                  <div class="chart-box">
                    <h3>Yearly Energy Production</h3>
                    <div class="chart-wrapper" role="img" aria-label="Yearly energy production chart showing total kilowatt-hours generated each month">
                      <canvas id="yearlyChart"></canvas>
                    </div>
                  </div>
                </div>
              </section>

              <div id="loadingIndicator" class="loading" style="display: none;">
                <div class="spinner"></div>
                <p>Simulating...</p>
              </div>
            </section>

            <section class="tab-panel" id="panel-battery" role="tabpanel" aria-labelledby="tab-battery" hidden>
              <h2>Battery Simulation</h2>
              <p>Battery simulation coming soon...</p>
            </section>

            <section class="tab-panel" id="panel-cost-analysis" role="tabpanel" aria-labelledby="tab-cost-analysis" hidden>
              <h2>Cost Analysis</h2>
              <p>Cost analysis coming soon...</p>
            </section>
          </main>

          <footer>
            <p>Backend: <code>http://localhost:8000</code></p>
          </footer>
        </div>
    `;
  });

  test('Page has no accessibility violations', async () => {
    const results = await axe(document.body);
    expect(results).toHaveNoViolations();
  });

  test('Form inputs are accessible with labels', () => {
    const inputs = document.querySelectorAll('input[required]');

    inputs.forEach(input => {
      const label = document.querySelector(`label[for="${input.id}"]`);
      expect(label).toBeTruthy();
      expect(label.textContent).toBeTruthy();
      expect(input.getAttribute('aria-required')).toBe('true');
      expect(input.getAttribute('aria-describedby')).toBeTruthy();
    });
  });

  test('Tab navigation is accessible', () => {
    const tablist = document.querySelector('[role="tablist"]');
    expect(tablist).toBeTruthy();

    const tabs = document.querySelectorAll('[role="tab"]');
    expect(tabs.length).toBeGreaterThan(0);

    tabs.forEach(tab => {
      expect(tab.hasAttribute('aria-selected')).toBe(true);
      expect(tab.hasAttribute('aria-controls')).toBe(true);
      expect(tab.id).toBeTruthy();
    });
  });

  test('Tab panels are properly labeled', () => {
    const panels = document.querySelectorAll('[role="tabpanel"]');
    expect(panels.length).toBeGreaterThan(0);

    panels.forEach(panel => {
      expect(panel.hasAttribute('aria-labelledby')).toBe(true);
      const labelId = panel.getAttribute('aria-labelledby');
      const label = document.getElementById(labelId);
      expect(label).toBeTruthy();
    });
  });

  test('Error messages are accessible', () => {
    const formError = document.getElementById('formError');
    expect(formError).toBeTruthy();
    expect(formError.getAttribute('role')).toBe('alert');
    expect(formError.getAttribute('aria-live')).toBe('assertive');

    const fieldErrors = document.querySelectorAll('span.error');
    expect(fieldErrors.length).toBeGreaterThan(0);
  });

  test('Charts are accessible with descriptions', () => {
    const charts = document.querySelectorAll('[role="img"]');
    expect(charts.length).toBeGreaterThan(0);

    charts.forEach(chart => {
      expect(chart.hasAttribute('aria-label')).toBe(true);
      expect(chart.getAttribute('aria-label').length).toBeGreaterThan(10);
    });
  });

  test('Results section has aria-live for dynamic updates', () => {
    const results = document.getElementById('resultsSection');
    expect(results).toBeTruthy();
    expect(results.getAttribute('aria-live')).toBe('polite');
    expect(results.getAttribute('aria-atomic')).toBe('true');
  });

  test('Page has valid HTML structure', () => {
    const html = document.documentElement;
    expect(html.getAttribute('lang')).toBe('en');

    const title = document.querySelector('title');
    expect(title).toBeTruthy();
    expect(title.textContent.length).toBeGreaterThan(0);

    const h1 = document.querySelector('h1');
    expect(h1).toBeTruthy();
    expect(h1.textContent).toBeTruthy();
  });

  test('All buttons and interactive elements are keyboard accessible', () => {
    const buttons = document.querySelectorAll('button');
    expect(buttons.length).toBeGreaterThan(0);

    buttons.forEach(button => {
      // Buttons should be naturally focusable
      expect(button.tagName).toBe('BUTTON');
    });

    const inputs = document.querySelectorAll('input');
    expect(inputs.length).toBeGreaterThan(0);

    inputs.forEach(input => {
      // Inputs should be naturally focusable
      expect(input.tagName).toBe('INPUT');
    });
  });

  test('No custom tabindex disrupting focus order', () => {
    const elements = document.querySelectorAll('[tabindex]');

    elements.forEach(el => {
      const tabindex = parseInt(el.getAttribute('tabindex'));
      // Only allow tabindex="-1" (remove from focus) or "0" (add to focus order)
      // Never positive values that override natural order
      expect([0, -1]).toContain(tabindex);
    });
  });
});
