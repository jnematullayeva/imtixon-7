const auth = {
    async login(username, password) {
        const data = await api.post('/auth/login/', { username, password });
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        await this.updateUI();
        return data;
    },

    async register(userData) {
        return api.post('/auth/register/', userData);
    },

    async logout() {
        const refresh = localStorage.getItem('refresh_token');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('is_staff');
        if (refresh) {
            try { await api.post('/auth/logout/', { refresh }, false); } catch (e) { /* ignore */ }
        }
        await this.updateUI();
    },

    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    },

    isStaff() {
        return localStorage.getItem('is_staff') === 'true';
    },

    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login/';
            return false;
        }
        return true;
    },

    async updateUI() {
        const authLinks = document.getElementById('auth-links');
        const userMenu = document.getElementById('user-menu');
        const adminLink = document.getElementById('admin-link');
        const logoutBtn = document.getElementById('logout-btn');

        if (!authLinks) return;

        if (this.isAuthenticated()) {
            authLinks.classList.add('hidden');
            userMenu.classList.remove('hidden');
            try {
                const profile = await api.get('/auth/profile/');
                document.getElementById('user-name').textContent = profile.first_name || profile.username;
                localStorage.setItem('is_staff', profile.is_staff ? 'true' : 'false');
                if (profile.is_staff && adminLink) adminLink.classList.remove('hidden');
                else if (adminLink) adminLink.classList.add('hidden');
            } catch (e) {
                localStorage.removeItem('is_staff');
            }
        } else {
            authLinks.classList.remove('hidden');
            userMenu.classList.add('hidden');
            localStorage.removeItem('is_staff');
            if (adminLink) adminLink.classList.add('hidden');
        }

        if (logoutBtn) {
            logoutBtn.onclick = async () => {
                await this.logout();
                if (window.location.pathname !== '/') {
                    window.location.href = '/';
                }
            };
        }
    },
};

document.addEventListener('DOMContentLoaded', () => auth.updateUI());
