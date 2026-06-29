const API_BASE = '/api';

const api = {
    async request(method, endpoint, data = null, retry = true, isFormData = false) {
        const headers = {};
        if (!isFormData) headers['Content-Type'] = 'application/json';
        const token = localStorage.getItem('access_token');
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const options = { method, headers };
        if (data) options.body = isFormData ? data : JSON.stringify(data);

        let response = await fetch(`${API_BASE}${endpoint}`, options);

        if (response.status === 401 && retry && localStorage.getItem('refresh_token')) {
            const refreshed = await this.refreshToken();
            if (refreshed) return this.request(method, endpoint, data, false, isFormData);
        }

        const contentType = response.headers.get('content-type');
        const body = contentType && contentType.includes('application/json')
            ? await response.json()
            : await response.text();

        if (!response.ok) {
            const msg = body.detail || body.message || JSON.stringify(body) || 'Xatolik yuz berdi';
            throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
        }
        return body;
    },

    async refreshToken() {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) return false;
        try {
            const data = await fetch(`${API_BASE}/auth/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh }),
            }).then(r => r.json());
            if (data.access) {
                localStorage.setItem('access_token', data.access);
                if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
                return true;
            }
        } catch (e) { /* ignore */ }
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return false;
    },

    get(endpoint) { return this.request('GET', endpoint); },
    post(endpoint, data, retry = true) { return this.request('POST', endpoint, data, retry); },
    postForm(endpoint, formData, retry = true) { return this.request('POST', endpoint, formData, retry, true); },
    patch(endpoint, data) { return this.request('PATCH', endpoint, data); },
    delete(endpoint) { return this.request('DELETE', endpoint); },

    mediaUrl(path) {
        if (!path) return null;
        if (path.startsWith('http')) return path;
        return path.startsWith('/') ? path : `/${path}`;
    },

    productImageUrl(product) {
        if (!product) return null;
        const images = product.images || [];
        const primary = images.find(img => img.is_primary) || images[0];
        if (primary && primary.image) return this.mediaUrl(primary.image);
        if (product.primary_image) return this.mediaUrl(product.primary_image);
        return null;
    },
};
