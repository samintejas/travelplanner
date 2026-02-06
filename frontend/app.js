// Travel Concierge - Customer App

const API_URL = 'http://localhost:8000/api';

let sessionId = null;
let bookingId = null;
let itinerary = {
    flights: [],
    hotels: [],
    activities: [],
    totalCost: 0,
    confirmed: false
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Add welcome message
    addMessage('assistant',
        "Welcome to Travel Concierge! I'm here to help you plan your perfect trip to **anywhere in the world**.\n\n" +
        "Tell me where you'd like to go, your budget, and travel dates, and I'll help you find flights, hotels, and activities.\n\n" +
        "Try asking: \"I want to plan a trip to India\" or \"Help me visit Japan\""
    );

    // Handle enter key
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Setup modal close
    document.getElementById('confirm-modal').addEventListener('click', (e) => {
        if (e.target.id === 'confirm-modal') {
            closeConfirmModal();
        }
    });
});

// Send message to backend
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to UI
    addMessage('user', message);
    input.value = '';

    // Disable input while processing
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span class="loading"></span>';

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });

        const data = await response.json();

        // Store session ID
        sessionId = data.session_id;

        // Add assistant response
        addMessage('assistant', data.response);

        // Update preferences sidebar
        updatePreferences(data.preferences);

        // Check for booking IDs in response and add booking buttons
        checkForBookingOptions(data.response);

        // Update confirmed status
        if (data.confirmed && data.booking_id) {
            bookingId = data.booking_id;
            itinerary.confirmed = true;
            showBookingConfirmation(data.booking_id);
            updateItineraryUI();
        }

    } catch (error) {
        console.error('Error:', error);
        addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    }

    sendBtn.disabled = false;
    sendBtn.textContent = 'Send';
}

// Add message to chat
function addMessage(role, content) {
    const messagesContainer = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    // Simple markdown-like parsing
    let html = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n- /g, '</p><li>')
        .replace(/\n/g, '<br>');

    // Wrap in paragraph
    html = '<p>' + html + '</p>';

    messageDiv.innerHTML = html;
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Update preferences sidebar
function updatePreferences(prefs) {
    document.getElementById('pref-destination').textContent = prefs.destination || '-';
    document.getElementById('pref-origin').textContent = prefs.origin || '-';
    document.getElementById('pref-dates').textContent =
        prefs.start_date && prefs.end_date ? `${prefs.start_date} - ${prefs.end_date}` : '-';
    document.getElementById('pref-budget').textContent = prefs.budget ? `$${prefs.budget}` : '-';
    document.getElementById('pref-style').textContent = prefs.travel_style || '-';
}

// Check response for booking options
function checkForBookingOptions(response) {
    const patterns = {
        flight: /\(FL\d+\)/g,
        hotel: /\(HT\d+\)/g,
        activity: /\(AC\d+\)/g
    };

    const messagesContainer = document.getElementById('messages');
    const lastMessage = messagesContainer.lastElementChild;

    let buttonsHtml = '';

    for (const [type, pattern] of Object.entries(patterns)) {
        const matches = response.match(pattern);
        if (matches) {
            matches.forEach(match => {
                const id = match.replace(/[()]/g, '');
                buttonsHtml += `
                    <button class="quick-action" onclick="addToItinerary('${type}', '${id}')">
                        Add ${id}
                    </button>
                `;
            });
        }
    }

    if (buttonsHtml) {
        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'quick-actions';
        buttonsDiv.style.marginTop = '12px';
        buttonsDiv.innerHTML = buttonsHtml;
        lastMessage.appendChild(buttonsDiv);
    }
}

// Add item to itinerary
async function addToItinerary(type, itemId) {
    if (!sessionId) {
        alert('Please start a conversation first');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/book`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                item_type: type,
                item_id: itemId
            })
        });

        const data = await response.json();

        if (data.success) {
            // Refresh itinerary from server
            await loadItinerary();
            addMessage('assistant', data.message);
        }
    } catch (error) {
        console.error('Error adding to itinerary:', error);
    }
}

// Load itinerary from server
async function loadItinerary() {
    if (!sessionId) return;

    try {
        const response = await fetch(`${API_URL}/itinerary/${sessionId}`);
        const data = await response.json();

        itinerary = {
            flights: data.flights,
            hotels: data.hotels,
            activities: data.activities,
            totalCost: data.total_cost,
            confirmed: data.confirmed
        };

        updateItineraryUI();
    } catch (error) {
        console.error('Error loading itinerary:', error);
    }
}

// Update itinerary UI
function updateItineraryUI() {
    const container = document.getElementById('itinerary-items');
    const items = [];

    itinerary.flights.forEach(f => {
        items.push(`
            <div class="itinerary-item">
                <div class="type">Flight</div>
                <div class="name">${f.airline}: ${f.from} → ${f.to}</div>
                <div class="price">$${f.price}</div>
            </div>
        `);
    });

    itinerary.hotels.forEach(h => {
        items.push(`
            <div class="itinerary-item">
                <div class="type">Hotel</div>
                <div class="name">${h.name}</div>
                <div class="price">$${h.price_per_night}/night</div>
            </div>
        `);
    });

    itinerary.activities.forEach(a => {
        items.push(`
            <div class="itinerary-item">
                <div class="type">Activity</div>
                <div class="name">${a.name}</div>
                <div class="price">$${a.price}</div>
            </div>
        `);
    });

    if (items.length === 0) {
        container.innerHTML = '<div class="empty-state">No items yet</div>';
        document.getElementById('total-cost').style.display = 'none';
        document.getElementById('confirm-btn').style.display = 'none';
        document.getElementById('confirmed-badge').style.display = 'none';
        document.getElementById('booking-ref').style.display = 'none';
    } else {
        container.innerHTML = items.join('');
        document.getElementById('total-cost').style.display = 'block';
        document.getElementById('cost-value').textContent = itinerary.totalCost.toFixed(2);

        if (itinerary.confirmed) {
            document.getElementById('confirm-btn').style.display = 'none';
            document.getElementById('confirmed-badge').style.display = 'block';
            if (bookingId) {
                document.getElementById('booking-ref').style.display = 'block';
                document.getElementById('booking-ref-id').textContent = bookingId;
            }
        } else {
            document.getElementById('confirm-btn').style.display = 'block';
            document.getElementById('confirmed-badge').style.display = 'none';
            document.getElementById('booking-ref').style.display = 'none';
        }
    }
}

// Show confirmation modal
function showConfirmModal() {
    if (!sessionId || itinerary.totalCost === 0) {
        alert('Please add items to your itinerary first');
        return;
    }

    // Populate modal with itinerary summary
    let summary = '<h4 style="margin-bottom: 12px;">Your Booking Summary</h4>';

    if (itinerary.flights.length > 0) {
        summary += '<div style="margin-bottom: 8px;"><strong>Flights:</strong></div>';
        itinerary.flights.forEach(f => {
            summary += `<div style="padding: 8px; background: var(--bg-tertiary); border-radius: 4px; margin-bottom: 4px;">
                ${f.airline}: ${f.from} → ${f.to} - $${f.price}
            </div>`;
        });
    }

    if (itinerary.hotels.length > 0) {
        summary += '<div style="margin-bottom: 8px; margin-top: 12px;"><strong>Hotels:</strong></div>';
        itinerary.hotels.forEach(h => {
            summary += `<div style="padding: 8px; background: var(--bg-tertiary); border-radius: 4px; margin-bottom: 4px;">
                ${h.name} - $${h.price_per_night}/night
            </div>`;
        });
    }

    if (itinerary.activities.length > 0) {
        summary += '<div style="margin-bottom: 8px; margin-top: 12px;"><strong>Activities:</strong></div>';
        itinerary.activities.forEach(a => {
            summary += `<div style="padding: 8px; background: var(--bg-tertiary); border-radius: 4px; margin-bottom: 4px;">
                ${a.name} - $${a.price}
            </div>`;
        });
    }

    summary += `<div style="margin-top: 16px; font-size: 18px; font-weight: 600;">Total: $${itinerary.totalCost.toFixed(2)}</div>`;

    document.getElementById('booking-summary').innerHTML = summary;
    document.getElementById('confirm-modal').style.display = 'flex';
}

// Close confirmation modal
function closeConfirmModal() {
    document.getElementById('confirm-modal').style.display = 'none';
}

// Submit booking with customer info
async function submitBooking() {
    const email = document.getElementById('customer-email').value.trim();
    const name = document.getElementById('customer-name').value.trim();
    const phone = document.getElementById('customer-phone').value.trim();

    if (!email) {
        alert('Please enter your email address');
        return;
    }

    // Save customer info
    try {
        await fetch(`${API_URL}/customer-info`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                email: email,
                name: name || null,
                phone: phone || null
            })
        });
    } catch (error) {
        console.error('Error saving customer info:', error);
    }

    // Close modal
    closeConfirmModal();

    // Send confirmation message through chat
    document.getElementById('messageInput').value = 'Please confirm my booking';
    await sendMessage();
}

// Show booking confirmation
function showBookingConfirmation(bookingId) {
    addMessage('assistant',
        `**Booking Confirmed!**\n\n` +
        `Your booking reference number is: **${bookingId}**\n\n` +
        `Please save this reference number for your records. Our travel team has been notified and will process your booking shortly.\n\n` +
        `Thank you for using Travel Concierge!`
    );
}

// Confirm booking (legacy, now shows modal)
function confirmBooking() {
    showConfirmModal();
}

// Quick action helper
function quickAction(text) {
    document.getElementById('messageInput').value = text;
    sendMessage();
}
