// Stripe checkout functionality for ApexLiftStudio

async function createCheckoutSession(planId, billingCycle) {
    try {
        const response = await fetch('/api/stripe/create-checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                plan_id: planId,
                billing_cycle: billingCycle
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (data.session_url) {
            // Redirect to Stripe Checkout
            window.location.href = data.session_url;
        } else if (data.error) {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error creating checkout session:', error);
        alert('An error occurred. Please try again or contact support.');
    }
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Handle checkout success/cancel from URL params
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const checkout = urlParams.get('checkout');

    if (checkout === 'success') {
        // Show success message
        showMessage('Payment successful! Your membership has been activated.', 'success');
    } else if (checkout === 'cancelled') {
        // Show cancelled message
        showMessage('Checkout was cancelled. You can try again anytime.', 'warning');
    }
});

function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-20 right-4 z-50 bg-${type === 'success' ? 'green' : type === 'warning' ? 'yellow' : 'red'}-500 text-white px-6 py-3 rounded-lg shadow-lg animate-slide-in`;
    messageDiv.textContent = message;

    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateX(100%)';
        setTimeout(() => messageDiv.remove(), 300);
    }, 5000);
}