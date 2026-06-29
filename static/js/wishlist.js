const wishlistPage = {
    async init() {
        if (!auth.requireAuth()) return;
        await this.load();
        document.getElementById('clear-wishlist').addEventListener('click', async () => {
            await api.delete('/wishlist/clear/');
            await this.load();
        });
    },

    async load() {
        const data = await api.get('/wishlist/');
        const container = document.getElementById('wishlist-items');
        container.innerHTML = '';
        (data.items || []).forEach(item => {
            const p = item.product;
            const badge = item.out_of_stock ? '<span class="badge">Stokda yo\'q</span>' : '';
            container.innerHTML += `
                <div class="card">
                    <h3>${p.name} ${badge}</h3>
                    <p>${p.price} so'm</p>
                    <button onclick="wishlistPage.remove(${p.id})" class="btn btn-outline btn-sm">Olib tashlash</button>
                    <button onclick="wishlistPage.moveToCart(${p.id})" class="btn btn-primary btn-sm">Buyurtmaga</button>
                </div>`;
        });
    },

    async remove(productId) {
        await api.delete(`/wishlist/remove/${productId}/`);
        await this.load();
    },

    async moveToCart(productId) {
        try {
            await api.post(`/wishlist/move-to-cart/${productId}/`);
            window.location.href = '/orders/';
        } catch (e) { alert(e.message); }
    },
};

document.addEventListener('DOMContentLoaded', () => wishlistPage.init());
