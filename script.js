// ===== CALCULATOR =====
const CAR_DATA = {
  Toyota: {
    Camry:          { 2019: 13500000, 2020: 15200000, 2021: 16800000, 2022: 18500000, 2023: 21000000 },
    RAV4:           { 2019: 16000000, 2020: 18000000, 2021: 20000000, 2022: 22500000, 2023: 25000000 },
    Highlander:     { 2020: 24000000, 2021: 26500000, 2022: 29000000, 2023: 32000000 },
    'Land Cruiser Prado': { 2020: 36000000, 2021: 39000000, 2022: 43000000, 2023: 48000000 },
    'Land Cruiser 300':   { 2021: 68000000, 2022: 74000000, 2023: 82000000 },
    Fortuner:       { 2020: 22000000, 2021: 24000000, 2022: 26500000, 2023: 29000000 },
  },
  Hyundai: {
    Tucson:         { 2020: 14500000, 2021: 16000000, 2022: 17500000, 2023: 19500000 },
    'Santa Fe':     { 2020: 20000000, 2021: 22000000, 2022: 24500000, 2023: 27000000 },
    Palisade:       { 2020: 26000000, 2021: 28500000, 2022: 31000000, 2023: 34000000 },
    Sonata:         { 2020: 12500000, 2021: 14000000, 2022: 15500000, 2023: 17000000 },
  },
  Kia: {
    Sportage:       { 2020: 13500000, 2021: 15000000, 2022: 16500000, 2023: 18500000 },
    Sorento:        { 2020: 19500000, 2021: 21500000, 2022: 23500000, 2023: 26000000 },
    Telluride:      { 2020: 24000000, 2021: 26000000, 2022: 28500000, 2023: 31000000 },
    K5:             { 2020: 13000000, 2021: 14500000, 2022: 16000000, 2023: 17500000 },
  },
  BMW: {
    'X5':           { 2019: 42000000, 2020: 47000000, 2021: 52000000, 2022: 57000000, 2023: 63000000 },
    'X3':           { 2020: 32000000, 2021: 36000000, 2022: 40000000, 2023: 44000000 },
    '5 Series':     { 2020: 34000000, 2021: 38000000, 2022: 42000000, 2023: 46000000 },
    '7 Series':     { 2020: 58000000, 2021: 64000000, 2022: 70000000, 2023: 78000000 },
  },
  'Mercedes-Benz': {
    'GLE':          { 2020: 52000000, 2021: 57000000, 2022: 63000000, 2023: 70000000 },
    'GLC':          { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'E-Class':      { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'S-Class':      { 2021: 82000000, 2022: 90000000, 2023: 99000000 },
  },
  Audi: {
    'Q5':           { 2020: 33000000, 2021: 37000000, 2022: 41000000, 2023: 45000000 },
    'Q7':           { 2020: 48000000, 2021: 53000000, 2022: 58000000, 2023: 64000000 },
    'A6':           { 2020: 32000000, 2021: 36000000, 2022: 40000000, 2023: 44000000 },
  },
  Lexus: {
    'RX':           { 2020: 34000000, 2021: 38000000, 2022: 42000000, 2023: 47000000 },
    'LX':           { 2021: 68000000, 2022: 75000000, 2023: 84000000 },
    'NX':           { 2021: 28000000, 2022: 32000000, 2023: 36000000 },
    'GX':           { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
  },
  Ford: {
    'F-150':        { 2020: 28000000, 2021: 31000000, 2022: 34000000, 2023: 38000000 },
    'Explorer':     { 2020: 28000000, 2021: 31000000, 2022: 34000000, 2023: 37000000 },
    'Expedition':   { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
  },
  Chevrolet: {
    'Tahoe':        { 2020: 40000000, 2021: 44000000, 2022: 48000000, 2023: 53000000 },
    'Suburban':     { 2020: 45000000, 2021: 50000000, 2022: 55000000, 2023: 61000000 },
    'Traverse':     { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
  },
  Volkswagen: {
    'Tiguan':       { 2020: 17000000, 2021: 19000000, 2022: 21000000, 2023: 23000000 },
    'Atlas':        { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
    'Touareg':      { 2020: 34000000, 2021: 38000000, 2022: 42000000, 2023: 46000000 },
  },
};

const DISCOUNT = 0.28; // ~28% дешевле

function fmt(n) {
  return n.toLocaleString('ru-RU') + ' ₸';
}

function animateValue(el, from, to, duration) {
  const start = performance.now();
  const update = (now) => {
    const p = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    const val = Math.round(from + (to - from) * eased);
    el.textContent = fmt(val);
    if (p < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

function showCalcResult(dealerPrice, carName) {
  const ourPrice = Math.round(dealerPrice * (1 - DISCOUNT));
  const saving = dealerPrice - ourPrice;
  const deposit = Math.round(ourPrice * 0.4);

  const placeholder = document.querySelector('.calc__result-placeholder');
  const data = document.getElementById('calcData');
  if (placeholder) placeholder.style.display = 'none';
  if (data) data.style.display = 'flex';

  document.getElementById('calcCarName').textContent = carName || 'Ваш автомобиль';
  document.getElementById('calcDealerPrice').textContent = fmt(dealerPrice);

  const ourPriceEl = document.getElementById('calcOurPrice');
  const savingEl = document.getElementById('calcSaving');
  const depositEl = document.getElementById('calcDeposit');

  animateValue(ourPriceEl, dealerPrice, ourPrice, 800);
  animateValue(savingEl, 0, saving, 900);
  animateValue(depositEl, 0, deposit, 700);

  const text = [
    '🚗 *Запрос из калькулятора — Easy Auto Import*',
    '',
    carName ? `🚘 Авто: ${carName}` : '',
    `💵 Цена дилера: ${fmt(dealerPrice)}`,
    `✅ Наша цена: ${fmt(ourPrice)}`,
    `💰 Экономия: ${fmt(saving)}`,
  ].filter(Boolean).join('\n');

  document.getElementById('calcWhatsapp').href =
    `https://wa.me/77476899519?text=${encodeURIComponent(text)}`;
}

function resetCalcResult() {
  const placeholder = document.querySelector('.calc__result-placeholder');
  const data = document.getElementById('calcData');
  if (placeholder) placeholder.style.display = '';
  if (data) data.style.display = 'none';
}

// Tabs
document.querySelectorAll('.calc__tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.calc__tab').forEach(t => t.classList.remove('calc__tab--active'));
    tab.classList.add('calc__tab--active');
    const target = tab.dataset.tab;
    document.getElementById('tabModel').classList.toggle('calc__panel--hidden', target !== 'model');
    document.getElementById('tabManual').classList.toggle('calc__panel--hidden', target !== 'manual');
    resetCalcResult();
  });
});

// Brand → Model
const brandSel = document.getElementById('calcBrand');
const modelSel = document.getElementById('calcModel');
const yearSel = document.getElementById('calcYear');

if (brandSel) {
  brandSel.addEventListener('change', () => {
    const brand = brandSel.value;
    modelSel.innerHTML = '<option value="">— Выберите модель —</option>';
    yearSel.innerHTML = '<option value="">— Выберите год —</option>';
    modelSel.disabled = !brand;
    yearSel.disabled = true;
    if (brand && CAR_DATA[brand]) {
      Object.keys(CAR_DATA[brand]).forEach(m => {
        modelSel.innerHTML += `<option value="${m}">${m}</option>`;
      });
    }
    resetCalcResult();
  });

  modelSel.addEventListener('change', () => {
    const brand = brandSel.value;
    const model = modelSel.value;
    yearSel.innerHTML = '<option value="">— Выберите год —</option>';
    yearSel.disabled = !model;
    if (brand && model && CAR_DATA[brand]?.[model]) {
      Object.keys(CAR_DATA[brand][model]).sort((a,b) => b-a).forEach(y => {
        yearSel.innerHTML += `<option value="${y}">${y}</option>`;
      });
    }
    resetCalcResult();
  });

  yearSel.addEventListener('change', () => {
    const brand = brandSel.value;
    const model = modelSel.value;
    const year = yearSel.value;
    if (!brand || !model || !year) return;
    const price = CAR_DATA[brand]?.[model]?.[year];
    if (price) showCalcResult(price, `${brand} ${model} ${year}`);
  });
}

// Manual price
const manualInput = document.getElementById('calcManualPrice');
let manualTimer;
if (manualInput) {
  manualInput.addEventListener('input', () => {
    clearTimeout(manualTimer);
    manualTimer = setTimeout(() => {
      const val = parseInt(manualInput.value);
      if (val >= 1000000) {
        showCalcResult(val, '');
      } else {
        resetCalcResult();
      }
    }, 500);
  });
}

// Nav burger
const burger = document.getElementById('burger');
const navLinks = document.querySelector('.nav__links');
if (burger && navLinks) {
  burger.addEventListener('click', () => {
    const isOpen = navLinks.classList.contains('nav__links--open');
    navLinks.classList.toggle('nav__links--open', !isOpen);
    if (!isOpen) {
      navLinks.style.cssText = 'display:flex;flex-direction:column;position:absolute;top:64px;left:0;right:0;background:rgba(8,10,15,0.98);padding:16px 24px 20px;border-bottom:1px solid rgba(255,255,255,0.07);gap:4px;';
    } else {
      navLinks.style.display = '';
    }
  });
}

// Nav scroll opacity
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
  nav.style.background = window.scrollY > 40
    ? 'rgba(8,10,15,0.98)'
    : 'rgba(8,10,15,0.85)';
});

// Animated counters
const counters = document.querySelectorAll('.pain-stat__num');
const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const el = entry.target;
    const target = parseInt(el.dataset.target);
    const duration = 1500;
    const start = performance.now();
    const update = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
    counterObserver.unobserve(el);
  });
}, { threshold: 0.5 });
counters.forEach(el => counterObserver.observe(el));

// Scroll animations
const animObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      animObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.market-card, .ins-card, .step-item, .pay-step, .shield-item, .pain-stat').forEach((el, i) => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = `opacity 0.5s ${i * 0.06}s ease, transform 0.5s ${i * 0.06}s ease`;
  animObserver.observe(el);
});

// CTA form — WhatsApp
const form = document.getElementById('ctaForm');
if (form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const inputs = form.querySelectorAll('input');
    const name = inputs[0].value.trim();
    const phone = inputs[1].value.trim();
    const car = inputs[2].value.trim();

    const text = [
      '🚗 *Новая заявка — Easy Auto Import*',
      '',
      `👤 Имя: ${name}`,
      `📞 Телефон: ${phone}`,
      car ? `🔍 Авто: ${car}` : '',
    ].filter(Boolean).join('\n');

    window.open(`https://wa.me/77476899519?text=${encodeURIComponent(text)}`, '_blank');

    const btn = form.querySelector('button[type="submit"]');
    const orig = btn.innerHTML;
    btn.innerHTML = '✅ Заявка отправлена!';
    btn.disabled = true;
    btn.style.background = '#22C55E';
    setTimeout(() => {
      btn.innerHTML = orig;
      btn.disabled = false;
      btn.style.background = '';
      form.reset();
    }, 3500);
  });
}
