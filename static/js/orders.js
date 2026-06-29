const ordersPage = {
    async init() {
        if (!auth.requireAuth()) return;
        const data = await api.get('/orders/');
        const container = document.getElementById('orders-list');
        (data.results || data).forEach(o => {
            container.innerHTML += `
                <div class="card">
                    <h3>${o.order_number}</h3>
                    <p>Status: ${o.status} | Jami: ${o.total_price} so'm</p>
                    <p>Sana: ${new Date(o.created_at).toLocaleDateString()}</p>
                    ${o.status === 'pending' ? `<button onclick="ordersPage.cancel(${o.id})" class="btn btn-outline btn-sm">Bekor qilish</button>` : ''}
                </div>`;
        });
    },

    async cancel(id) {
        await api.patch(`/orders/${id}/cancel/`);
        location.reload();
    },
};

document.addEventListener('DOMContentLoaded', () => ordersPage.init());
