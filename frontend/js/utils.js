// Utility functions
class Utils {
    static showLoading() {
        let overlay = document.getElementById('loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner"></div>
            `;
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    }

    static hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    static showSuccessModal(message, onClose = null) {
        const modalId = 'success-modal';
        let modal = document.getElementById(modalId);
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = modalId;
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-icon">
                        <i class="fas fa-check"></i>
                    </div>
                    <h3>Success!</h3>
                    <p>${message}</p>
                    <button onclick="Utils.hideSuccessModal()" class="btn btn-primary">Close</button>
                </div>
            `;
            document.body.appendChild(modal);
        } else {
            modal.querySelector('p').textContent = message;
        }
        
        modal.style.display = 'flex';
        
        if (onClose) {
            modal.querySelector('button').onclick = () => {
                Utils.hideSuccessModal();
                onClose();
            };
        }
    }

    static hideSuccessModal() {
        const modal = document.getElementById('success-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    static showError(message) {
        alert(`Error: ${message}`);
    }

    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    static validateEmail(email) {
        const pattern = /^[a-zA-Z0-9._%+-]+@skasc\.ac\.in$/;
        return pattern.test(email);
    }

    static logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/auth/login.html';
    }

    static isAuthenticated() {
        return !!localStorage.getItem('token');
    }

    static requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/auth/login.html';
            return false;
        }
        return true;
    }

    static getUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }
}
// Event Storage Functions - Add this after your Utils class
const EventManager = {
    // Save event to storage
    saveEvent: function(eventData) {
        try {
            // Get existing events from storage
            let events = JSON.parse(localStorage.getItem('skasc_events')) || [];
            
            // Add unique ID if not present
            if (!eventData.id) {
                eventData.id = 'event_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            }
            
            // Add creation timestamp if not present
            if (!eventData.created_at) {
                eventData.created_at = new Date().toISOString();
            }
            
            // Add default status if not present
            if (!eventData.status) {
                eventData.status = 'active';
            }
            
            // Get event type from session or default
            if (!eventData.event_type) {
                eventData.event_type = sessionStorage.getItem('eventType') || 'custom';
            }
            
            // Add to events array
            events.push(eventData);
            
            // Save back to localStorage
            localStorage.setItem('skasc_events', JSON.stringify(events));
            
            // Also save to sessionStorage for immediate use
            sessionStorage.setItem('selectedEvent', JSON.stringify(eventData));
            sessionStorage.setItem('selectedEventId', eventData.id);
            
            console.log('Event saved:', eventData);
            return eventData.id;
        } catch (error) {
            console.error('Error saving event:', error);
            return null;
        }
    },

    // Get all events
    getAllEvents: function() {
        try {
            const events = JSON.parse(localStorage.getItem('skasc_events')) || [];
            console.log('Retrieved events:', events);
            return events;
        } catch (error) {
            console.error('Error getting events:', error);
            return [];
        }
    },

    // Get event by ID
    getEventById: function(eventId) {
        try {
            const events = this.getAllEvents();
            return events.find(event => event.id === eventId);
        } catch (error) {
            console.error('Error getting event:', error);
            return null;
        }
    },

    // Update event
    updateEvent: function(eventId, updatedData) {
        try {
            let events = this.getAllEvents();
            const eventIndex = events.findIndex(event => event.id === eventId);
            
            if (eventIndex !== -1) {
                // Merge updated data with existing event data
                events[eventIndex] = { ...events[eventIndex], ...updatedData };
                localStorage.setItem('skasc_events', JSON.stringify(events));
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error updating event:', error);
            return false;
        }
    },

    // Delete event
    deleteEvent: function(eventId) {
        try {
            let events = this.getAllEvents();
            const filteredEvents = events.filter(event => event.id !== eventId);
            localStorage.setItem('skasc_events', JSON.stringify(filteredEvents));
            return true;
        } catch (error) {
            console.error('Error deleting event:', error);
            return false;
        }
    },

    // Clear all events
    clearAllEvents: function() {
        try {
            localStorage.removeItem('skasc_events');
            return true;
        } catch (error) {
            console.error('Error clearing events:', error);
            return false;
        }
    }
};

// Make EventManager globally available
window.EventManager = EventManager;
// Make Utils globally available
window.Utils = Utils;