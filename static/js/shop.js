const shop = {
    page: 1,

    productImageMarkup(product) {
        const url = api.productImageUrl(product);
        return url
            ? `<img src="${url}" alt="${product.name}" class="product-image">`
            : '<div class="product-image placeholder">Rasm yo\'q</div>';
    },

    init() {
        this.loadProducts();
        document.getElementById('filter-btn').addEventListener('click', () => {
            this.page = 1;
            this.loadProducts();
        });
    },

    buildQuery() {
        const params = new URLSearchParams();
        params.set('page', this.page);
        const search = document.getElementById('search').value;
        const priceMin = document.getElementById('price-min').value;
        const priceMax = document.getElementById('price-max').value;
        if (search) params.set('search', search);
        if (priceMin) params.set('price_min', priceMin);
        if (priceMax) params.set('price_max', priceMax);
        return params.toString();
    },

    async loadProducts() {
        const data = await api.get(`/shop/products/?${this.buildQuery()}`);
        const container = document.getElementById('products');
        container.innerHTML = '';
        (data.results || data).forEach(p => {
            container.innerHTML += `
                <div class="card">
                    ${this.productImageMarkup(p)}
                    <h3>${p.name}</h3>
                    <p>${p.brand || ''}</p>
                    <p><strong>${p.price} so'm</strong></p>
                    <a href="/product/${p.id}/" class="btn btn-sm">Ko'rish</a>
                </div>`;
        });

        const pag = document.getElementById('pagination');
        pag.innerHTML = '';
        if (data.next) {
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline';
            btn.textContent = 'Keyingi';
            btn.onclick = () => { this.page++; this.loadProducts(); };
            pag.appendChild(btn);
        }
    },
};

document.addEventListener('DOMContentLoaded', () => shop.init());
