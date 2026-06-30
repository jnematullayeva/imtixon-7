const booking = {
    state: { step: 1, category: null, service: null, master: null, date: null, slot: null },

    init() {
        if (!auth.requireAuth()) return;
        this.loadCategories();
        document.getElementById('prev-btn').addEventListener('click', () => this.prevStep());
        document.getElementById('next-btn').addEventListener('click', () => this.nextStep());
        document.getElementById('booking-date').addEventListener('change', (e) => {
            this.state.date = e.target.value;
            this.loadSlots();
            this.updateNextBtn();
        });
        document.getElementById('confirm-booking').addEventListener('click', () => this.confirm());
    },

    async loadCategories() {
        const data = await api.get('/booking/categories/');
        const container = document.getElementById('categories');
        (data.results || data).forEach(c => {
            const el = document.createElement('div');
            el.className = 'card';
            el.innerHTML = `<h3>${c.icon || ''} ${c.name}</h3><p>${c.description || ''}</p>`;
            el.onclick = () => {
                document.querySelectorAll('#categories .card').forEach(x => x.classList.remove('selected'));
                el.classList.add('selected');
                this.state.category = c;
                this.updateNextBtn();
            };
            container.appendChild(el);
        });
    },

    async loadServices() {
        const data = await api.get(`/booking/categories/${this.state.category.id}/services/`);
        const container = document.getElementById('services');
        container.innerHTML = '';
        (data.results || data).forEach(s => {
            const el = document.createElement('div');
            el.className = 'card';
            el.innerHTML = `<h3>${s.name}</h3><p>${s.duration_minutes} daq | ${s.price} so'm</p>`;
            el.onclick = () => {
                document.querySelectorAll('#services .card').forEach(x => x.classList.remove('selected'));
                el.classList.add('selected');
                this.state.service = s;
                this.updateNextBtn();
            };
            container.appendChild(el);
        });
    },

    async loadMasters() {
        const data = await api.get(`/booking/masters/?service=${this.state.service.id}`);
        const container = document.getElementById('masters');
        container.innerHTML = '';
        (data.results || data).forEach(m => {
            const el = document.createElement('div');
            el.className = 'card';
            el.innerHTML = `<h3>${m.user_name}</h3><p>Tajriba: ${m.experience_years} yil</p>`;
            el.onclick = () => {
                document.querySelectorAll('#masters .card').forEach(x => x.classList.remove('selected'));
                el.classList.add('selected');
                this.state.master = m;
                this.loadSlots();
                this.updateNextBtn();
            };
            container.appendChild(el);
        });
    },

    async loadSlots() {
        if (!this.state.master || !this.state.date || !this.state.service) return;
        const slots = await api.get(
            `/booking/masters/${this.state.master.id}/availability/?date=${this.state.date}&service_id=${this.state.service.id}`
        );
        const container = document.getElementById('time-slots');
        container.innerHTML = '';
        slots.forEach(s => {
            const btn = document.createElement('button');
            btn.className = 'slot-btn';
            btn.textContent = `${s.start} - ${s.end}`;
            btn.onclick = () => {
                document.querySelectorAll('.slot-btn').forEach(x => x.classList.remove('selected'));
                btn.classList.add('selected');
                this.state.slot = s;
                this.updateNextBtn();
            };
            container.appendChild(btn);
        });
    },

    updateNextBtn() {
        const btn = document.getElementById('next-btn');
        const s = this.state;
        let enabled = false;
        if (s.step === 1) enabled = !!s.category;
        if (s.step === 2) enabled = !!s.service;
        if (s.step === 3) enabled = !!s.master && !!s.date && !!s.slot;
        btn.disabled = !enabled;
    },

    showStep(n) {
        this.state.step = n;
        document.querySelectorAll('.wizard-panel').forEach(p => p.classList.add('hidden'));
        document.getElementById(`step-${n}`).classList.remove('hidden');
        document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
        document.querySelector(`.step[data-step="${n}"]`).classList.add('active');
        document.getElementById('prev-btn').disabled = n === 1;
        document.getElementById('next-btn').classList.toggle('hidden', n === 4);
        this.updateNextBtn();
    },

    async nextStep() {
        if (this.state.step === 1) { await this.loadServices(); this.showStep(2); }
        else if (this.state.step === 2) { await this.loadMasters(); this.showStep(3); }
        else if (this.state.step === 3) {
            document.getElementById('confirm-summary').innerHTML = `
                <p><strong>Kategoriya:</strong> ${this.state.category.name}</p>
                <p><strong>Xizmat:</strong> ${this.state.service.name}</p>
                <p><strong>Master:</strong> ${this.state.master.user_name}</p>
                <p><strong>Sana:</strong> ${this.state.date}</p>
                <p><strong>Vaqt:</strong> ${this.state.slot.start} - ${this.state.slot.end}</p>`;
            this.showStep(4);
        }
    },

    prevStep() {
        if (this.state.step > 1) this.showStep(this.state.step - 1);
    },

    async confirm() {
        try {
            await api.post('/booking/appointments/', {
                master: this.state.master.id,
                service: this.state.service.id,
                date: this.state.date,
                start_time: this.state.slot.start,
            });
            alert('Bron muvaffaqiyatli yaratildi!');
            window.location.href = '/profile/';
        } catch (e) {
            alert(e.message || 'Bron yaratib bo\'lmadi.');
        }
    },
};

document.addEventListener('DOMContentLoaded', () => booking.init());
