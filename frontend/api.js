// API base URL — override via window.APP_API_URL for non-default deployments
const API_URL = (typeof window !== 'undefined' && window.APP_API_URL)
    ? window.APP_API_URL
    : 'http://localhost:8000';

export async function simulateSolar(payload) {
    const btn = document.getElementById('simulateBtn');

    try {
        // Show loading state
        btn.disabled = true;
        btn.textContent = 'Simulating…';

        // Make request
        const response = await fetch(`${API_URL}/simulate`, {
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
