export async function simulateSolar(payload) {
    const btn = document.getElementById('simulateBtn');

    try {
        // Show loading state
        btn.disabled = true;
        btn.textContent = 'Simulating…';

        // Make request
        const response = await fetch('http://localhost:8000/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        // Handle response
        if (!response.ok) {
            const errorData = await response.json();
            return {
                error: true,
                status: response.status,
                detail: errorData.detail || [{ msg: 'Unknown error' }]
            };
        }

        return await response.json();
    } catch (error) {
        return {
            error: true,
            message: `Failed to connect to backend: ${error.message}`
        };
    } finally {
        // Restore button state
        btn.disabled = false;
        btn.textContent = 'Simulate';
    }
}
