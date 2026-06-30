const admin = {
    revenueChart: null,

    requireAdmin() {
        if (!auth.requireAuth()) return false;
        if (!auth.isStaff()) {
            alert('Admin huquqi talab qilinadi');
            window.location.href = '/';
            return false;
        }
        return true;
    },

    reportUrl(path, params) {
        const qs = params.toString();
        return qs ? `${path}?${qs}` : path;
    },

    async loadDashboard() {
        if (!this.requireAdmin()) return;
        const data = await api.get('/reports/dashboard/');
        const stats = document.getElementById('dashboard-stats');
        stats.innerHTML = `
            <div class="stat-card"><h3>${data.today.appointments}</h3><p>Bugungi bronlar</p></div>
            <div class="stat-card"><h3>${data.today.confirmed}</h3><p>Tasdiqlangan</p></div>
            <div class="stat-card"><h3>${data.this_month.total_orders}</h3><p>Oylik buyurtmalar</p></div>
            <div class="stat-card"><h3>${data.this_month.booking_revenue}</h3><p>Bron daromadi</p></div>`;

        const upcoming = document.getElementById('upcoming-appointments');
        upcoming.innerHTML = (data.upcoming_appointments || []).map(a =>
            `<div class="card"><p>${a.client} — ${a.service} | ${a.date} ${a.start_time}</p></div>`
        ).join('');

        const lowStock = document.getElementById('low-stock');
        lowStock.innerHTML = (data.low_stock_products || []).map(p =>
            `<div class="card"><p>${p.name} — Stok: ${p.stock_quantity}</p></div>`
        ).join('');
    },

    async loadAppointments() {
        if (!this.requireAdmin()) return;
        const data = await api.get('/admin/appointments/');
        const container = document.getElementById('appointments-table');
        const rows = (data.results || data).map(a => {
            const clientName = a.client_name || 'Noma\'lum mijoz';
            const clientPhone = a.client_phone || 'Kiritilmagan';
            const clientEmail = a.client_email || 'Kiritilmagan';
            const serviceName = a.service_name || 'Noma\'lum xizmat';
            const servicePrice = a.service_price ? parseFloat(a.service_price).toLocaleString() + ' so\'m' : '0 so\'m';
            const masterName = a.master_name || 'Noma\'lum master';
            
            return `<tr>
                <td>${a.id}</td>
                <td>
                    <div class="client-info">
                        <strong class="client-name">${clientName}</strong>
                        <span class="client-phone">📞 ${clientPhone}</span>
                        <span class="client-email">✉️ ${clientEmail}</span>
                    </div>
                </td>
                <td>
                    <div class="service-info">
                        <strong>${serviceName}</strong>
                        <span class="service-price">${servicePrice}</span>
                    </div>
                </td>
                <td><strong>${masterName}</strong></td>
                <td>
                    <div class="date-time-info">
                        <span class="date">${a.date}</span>
                        <span class="time">${a.start_time.substring(0, 5)} - ${a.end_time.substring(0, 5)}</span>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${a.status}">${a.status}</span>
                </td>
                <td>
                    <select class="status-select" onchange="admin.updateAppointmentStatus(${a.id}, this.value)">
                        <option value="pending" ${a.status==='pending'?'selected':''}>pending</option>
                        <option value="confirmed" ${a.status==='confirmed'?'selected':''}>confirmed</option>
                        <option value="cancelled" ${a.status==='cancelled'?'selected':''}>cancelled</option>
                        <option value="completed" ${a.status==='completed'?'selected':''}>completed</option>
                        <option value="no_show" ${a.status==='no_show'?'selected':''}>no_show</option>
                    </select>
                </td>
            </tr>`;
        }).join('');
        
        container.innerHTML = `
            <div class="table-responsive">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Mijoz ma'lumotlari</th>
                            <th>Xizmat</th>
                            <th>Master (Usta)</th>
                            <th>Sana va Vaqt</th>
                            <th>Status</th>
                            <th>O'zgartirish</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>`;
    },

    async updateAppointmentStatus(id, status) {
        try {
            await api.patch(`/admin/appointments/${id}/`, { status });
            await this.loadAppointments();
        } catch (e) {
            alert('Statusni yangilashda xatolik yuz berdi: ' + e.message);
        }
    },

    async loadProductCategories() {
        if (!this.requireAdmin()) return;
        const data = await api.get('/shop/categories/');
        const select = document.getElementById('product-category');
        if (!select) return;
        select.innerHTML = (data.results || data).map(c =>
            `<option value="${c.id}">${c.name}</option>`
        ).join('');
    },

    async createProduct() {
        if (!this.requireAdmin()) return;
        const errorEl = document.getElementById('product-form-error');
        errorEl.classList.add('hidden');
        try {
            const payload = {
                category: parseInt(document.getElementById('product-category').value, 10),
                name: document.getElementById('product-name').value.trim(),
                brand: document.getElementById('product-brand').value.trim(),
                price: document.getElementById('product-price').value,
                stock_quantity: parseInt(document.getElementById('product-stock').value, 10) || 0,
                unit: document.getElementById('product-unit').value.trim() || 'dona',
                description: document.getElementById('product-description').value.trim(),
                is_featured: document.getElementById('product-featured').checked,
                is_active: true,
            };
            const product = await api.post('/admin/shop/products/', payload);
            const imageInput = document.getElementById('product-image');
            if (imageInput && imageInput.files.length) {
                const formData = new FormData();
                formData.append('image', imageInput.files[0]);
                formData.append('is_primary', 'true');
                await api.postForm(`/admin/shop/products/${product.id}/images/`, formData);
            }
            document.getElementById('product-form').reset();
            document.getElementById('product-unit').value = 'dona';
            await this.loadProducts();
        } catch (e) {
            errorEl.textContent = e.message;
            errorEl.classList.remove('hidden');
        }
    },

    productImageMarkup(product) {
        const url = api.productImageUrl(product);
        return url
            ? `<img src="${url}" alt="${product.name}" class="product-thumb">`
            : '<div class="product-thumb"></div>';
    },

    async loadProducts() {
        if (!this.requireAdmin()) return;
        const data = await api.get('/shop/products/');
        const container = document.getElementById('products-table');
        const rows = (data.results || data).map(p =>
            `<tr>
                <td>${p.id}</td>
                <td>${this.productImageMarkup(p)}</td>
                <td>${p.name}</td>
                <td>${p.price}</td>
                <td>${p.stock_quantity}</td>
            </tr>`
        ).join('');
        container.innerHTML = `<table><thead><tr><th>ID</th><th>Rasm</th><th>Nom</th><th>Narx</th><th>Stok</th></tr></thead><tbody>${rows}</tbody></table>`;
    },

    async loadOrders() {
        if (!this.requireAdmin()) return;
        const data = await api.get('/admin/orders/');
        const container = document.getElementById('orders-table');
        const rows = (data.results || data).map(o =>
            `<tr><td>${o.order_number}</td><td>${o.status}</td><td>${o.total_price}</td>
            <td><select onchange="admin.updateOrderStatus(${o.id}, this.value)">
                <option value="pending" ${o.status==='pending'?'selected':''}>pending</option>
                <option value="confirmed" ${o.status==='confirmed'?'selected':''}>confirmed</option>
                <option value="processing" ${o.status==='processing'?'selected':''}>processing</option>
                <option value="completed" ${o.status==='completed'?'selected':''}>completed</option>
                <option value="cancelled" ${o.status==='cancelled'?'selected':''}>cancelled</option>
            </select></td></tr>`
        ).join('');
        container.innerHTML = `<table><thead><tr><th>Raqam</th><th>Status</th><th>Summa</th><th>O'zgartirish</th></tr></thead><tbody>${rows}</tbody></table>`;
    },

    async updateOrderStatus(id, status) {
        await api.patch(`/admin/orders/${id}/status/`, { status });
    },

    async loadReports() {
        if (!this.requireAdmin()) return;
        const from = document.getElementById('date-from').value;
        const to = document.getElementById('date-to').value;
        const params = new URLSearchParams();
        if (from) params.set('date_from', from);
        if (to) params.set('date_to', to);

        const [booking, orders, revenue] = await Promise.all([
            api.get(this.reportUrl('/reports/bookings/summary/', params)),
            api.get(this.reportUrl('/reports/orders/summary/', params)),
            api.get(this.reportUrl('/reports/revenue/', params)),
        ]);

        document.getElementById('reports-content').innerHTML = `
            <div class="stats-grid">
                <div class="stat-card"><h3>${booking.total}</h3><p>Jami bronlar</p></div>
                <div class="stat-card"><h3>${orders.total_orders}</h3><p>Jami buyurtmalar</p></div>
                <div class="stat-card"><h3>${revenue.total_revenue}</h3><p>Umumiy daromad</p></div>
            </div>`;

        const canvas = document.getElementById('revenue-chart');
        if (this.revenueChart) {
            this.revenueChart.destroy();
        }
        this.revenueChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: ['Bron', 'Do\'kon'],
                datasets: [{ label: 'Daromad', data: [revenue.booking_revenue, revenue.shop_revenue] }],
            },
        });
    },
};
