const API_BASE_URL = 'http://localhost:5000/api';

class API {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    async request(endpoint, method = 'GET', data = null) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const options = {
            method,
            headers,
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        try {
            console.log(`Making ${method} request to: ${url}`);
            console.log('Headers:', headers);
            if (data) console.log('Data:', data);

            const response = await fetch(url, options);
            console.log('Response status:', response.status);

            // Handle 401 Unauthorized
            if (response.status === 401) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/auth/login.html';
                throw new Error('Session expired. Please login again.');
            }

            let responseData;
            try {
                responseData = await response.json();
            } catch (e) {
                console.error('Failed to parse JSON response:', e);
                throw new Error('Invalid server response');
            }

            if (!response.ok) {
                throw new Error(responseData.error || responseData.details || `Request failed with status ${response.status}`);
            }

            console.log('Response data:', responseData);
            return responseData;
        } catch (error) {
            console.error('API Error:', error.message);
            throw error;
        }
    }

    // Auth endpoints
    async register(email, password, name) {
        try {
            const data = await this.request('/auth/register', 'POST', { email, password, name });
            if (data.token) {
                this.token = data.token;
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
            }
            return data;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }

    async login(email, password) {
        try {
            const data = await this.request('/auth/login', 'POST', { email, password });
            if (data.token) {
                this.token = data.token;
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
            }
            return data;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    async getCurrentUser() {
        return this.request('/auth/me');
    }

    // Event endpoints
    async createEvent(eventData) {
        return this.request('/events/create', 'POST', eventData);
    }

    async getMyEvents() {
        return this.request('/events/my-events');
    }

    // Voice endpoints
    async initiateCall(callData) {
        return this.request('/voice/call', 'POST', callData);
    }

    // Design endpoints
    async generatePoster(posterData) {
        return this.request('/design/poster', 'POST', posterData);
    }

    async generateCertificate(certificateData) {
        return this.request('/design/certificate', 'POST', certificateData);
    }
}

// Create global API instance
window.API = new API();