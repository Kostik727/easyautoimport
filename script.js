// ===== CALCULATOR =====
const Y = (base, start = 2017, end = 2023) => {
  const obj = {};
  for (let y = start; y <= end; y++) {
    const factor = Math.pow(1.1, y - start);
    obj[y] = Math.round(base * factor / 500000) * 500000;
  }
  return obj;
};

const CAR_DATA = {
  Acura: {
    'MDX':          Y(25000000, 2020),
    'RDX':          Y(19000000, 2020),
    'TLX':          Y(17000000, 2020),
  },
  Audi: {
    'A4':           Y(22000000, 2020),
    'A6':           Y(30000000, 2020),
    'A7':           Y(38000000, 2020),
    'Q3':           Y(20000000, 2020),
    'Q5':           Y(28000000, 2020),
    'Q7':           Y(40000000, 2020),
    'Q8':           Y(50000000, 2020),
    'e-tron':       Y(32000000, 2020),
    'e-tron GT':    Y(60000000, 2022),
  },
  BMW: {
    '3 Series':     {2020:18000000, 2021:20000000, 2022:22000000, 2023:25000000, 2024:28000000, 2025:31000000},
    '5 Series':     {2020:25000000, 2021:28000000, 2022:30000000, 2023:35000000, 2024:40000000, 2025:45000000},
    '7 Series':     {2020:40000000, 2021:45000000, 2022:50000000, 2023:60000000, 2024:70000000, 2025:78000000},
    'X1':           {2020:16000000, 2021:18000000, 2022:20000000, 2023:22000000, 2024:25000000, 2025:28000000},
    'X3':           {2020:22000000, 2021:25000000, 2022:28000000, 2023:32000000, 2024:35000000, 2025:38000000},
    'X5':           {2020:36000000, 2021:38600000, 2022:40000000, 2023:54000000, 2024:58000000, 2025:69200000},
    'X6':           {2020:38000000, 2021:42000000, 2022:45000000, 2023:50000000, 2024:55000000, 2025:62000000},
    'X7':           {2020:48000000, 2021:52000000, 2022:55000000, 2023:62000000, 2024:68000000, 2025:75000000},
    'i4':           {2022:28000000, 2023:32000000, 2024:35000000, 2025:38000000},
    'iX':           {2022:45000000, 2023:50000000, 2024:55000000, 2025:60000000},
  },
  Cadillac: {
    'CT5':          Y(22000000, 2020),
    'XT4':          Y(20000000, 2020),
    'XT5':          Y(27000000, 2020),
    'XT6':          Y(30000000, 2020),
    'Escalade':     Y(55000000, 2020),
    'Escalade ESV': Y(60000000, 2020),
  },
  Chevrolet: {
    'Malibu':       Y(11000000, 2020),
    'Camaro':       Y(17000000, 2020),
    'Equinox':      Y(13000000, 2020),
    'Blazer':       Y(18000000, 2020),
    'Traverse':     Y(20000000, 2020),
    'Tahoe':        Y(38000000, 2020),
    'Suburban':     Y(42000000, 2020),
    'Silverado 1500': Y(22000000, 2020),
  },
  Dodge: {
    'Charger':      Y(16000000, 2020),
    'Challenger':   Y(16000000, 2020),
    'Durango':      Y(25000000, 2020),
  },
  Ford: {
    'Mustang':      Y(17000000, 2020),
    'Escape':       Y(13000000, 2020),
    'Explorer':     Y(24000000, 2020),
    'Expedition':   Y(35000000, 2020),
    'F-150':        Y(25000000, 2020),
    'Ranger':       Y(18000000, 2020),
    'Bronco':       Y(20000000, 2021),
    'Bronco Sport': Y(15000000, 2021),
    'Maverick':     Y(14000000, 2022),
    'Mustang Mach-E': Y(26000000, 2021),
  },
  Genesis: {
    'G70':          Y(20000000, 2020),
    'G80':          Y(30000000, 2020),
    'G90':          Y(45000000, 2020),
    'GV70':         Y(24000000, 2022),
    'GV80':         Y(32000000, 2021),
  },
  GMC: {
    'Sierra 1500':  Y(24000000, 2020),
    'Yukon':        Y(38000000, 2020),
    'Yukon XL':     Y(42000000, 2020),
  },
  Honda: {
    'Civic':        Y(10000000, 2020),
    'Accord':       Y(12000000, 2020),
    'HR-V':         Y(11000000, 2020),
    'CR-V':         Y(14000000, 2020),
    'Passport':     Y(18000000, 2020),
    'Pilot':        Y(20000000, 2020),
  },
  Hyundai: {
    'Elantra':      {2020:8500000, 2021:9500000, 2022:10500000, 2023:12000000, 2024:13500000, 2025:15000000},
    'Sonata':       {2020:11000000, 2021:12500000, 2022:13500000, 2023:15000000, 2024:17000000, 2025:19000000},
    'Tucson':       {2020:10600000, 2021:11900000, 2022:12600000, 2023:13100000, 2024:13500000, 2025:18100000},
    'Santa Fe':     {2020:15500000, 2021:17000000, 2022:19000000, 2023:21000000, 2024:24000000, 2025:27000000},
    'Palisade':     {2020:22000000, 2021:24000000, 2022:26000000, 2023:28000000, 2024:31000000, 2025:34000000},
    'Kona':         {2020:9500000, 2021:10500000, 2022:11500000, 2023:13000000, 2024:14500000, 2025:16000000},
    'IONIQ 5':      {2022:19000000, 2023:21000000, 2024:23000000, 2025:25000000},
    'IONIQ 6':      {2023:20000000, 2024:22000000, 2025:24000000},
  },
  Infiniti: {
    'QX50':         Y(20000000, 2020),
    'QX55':         Y(22000000, 2022),
    'QX60':         Y(25000000, 2020),
    'QX80':         Y(42000000, 2020),
  },
  Jeep: {
    'Grand Cherokee': Y(25000000, 2020),
    'Grand Cherokee L': Y(28000000, 2022),
    'Wrangler':     Y(22000000, 2020),
    'Gladiator':    Y(21000000, 2020),
    'Wagoneer':     Y(42000000, 2022),
    'Grand Wagoneer': Y(58000000, 2022),
  },
  Kia: {
    'K5':           {2021:12000000, 2022:13500000, 2023:15000000, 2024:17000000, 2025:19000000},
    'Sportage':     {2020:10500000, 2021:10400000, 2022:13100000, 2023:13400000, 2024:14800000, 2025:13900000},
    'Sorento':      {2020:16000000, 2021:17500000, 2022:19000000, 2023:21000000, 2024:24000000, 2025:27000000},
    'Seltos':       {2021:11000000, 2022:12000000, 2023:13500000, 2024:15000000, 2025:16500000},
    'Telluride':    {2020:21000000, 2021:23000000, 2022:25000000, 2023:27000000, 2024:30000000, 2025:33000000},
    'Carnival':     {2021:17000000, 2022:19000000, 2023:21000000, 2024:24000000, 2025:27000000},
    'EV6':          {2022:19000000, 2023:21000000, 2024:23000000, 2025:25000000},
    'EV9':          {2024:36000000, 2025:40000000},
  },
  'Land Rover': {
    'Discovery':    Y(32000000, 2020),
    'Range Rover Evoque': Y(24000000, 2020),
    'Range Rover Velar':  Y(32000000, 2020),
    'Range Rover Sport':  Y(50000000, 2020),
    'Range Rover':        Y(65000000, 2020),
    'Defender':           Y(36000000, 2021),
  },
  Lexus: {
    'ES':           {2020:20000000, 2021:22000000, 2022:24000000, 2023:27000000, 2024:30000000, 2025:33000000},
    'IS':           {2020:18000000, 2021:20000000, 2022:22000000, 2023:25000000, 2024:28000000, 2025:31000000},
    'NX':           {2020:22000000, 2021:24000000, 2022:27000000, 2023:30000000, 2024:34000000, 2025:37000000},
    'RX':           {2020:33700000, 2021:28900000, 2022:27000000, 2023:38000000, 2024:62100000, 2025:60000000},
    'GX':           {2020:32000000, 2021:35000000, 2022:38000000, 2023:42000000, 2024:55000000, 2025:60000000},
    'LX':           {2020:55000000, 2021:58000000, 2022:65000000, 2023:70000000, 2024:78000000, 2025:85000000},
  },
  Lincoln: {
    'Corsair':      Y(19000000, 2020),
    'Nautilus':     Y(26000000, 2020),
    'Aviator':      Y(32000000, 2020),
    'Navigator':    Y(48000000, 2020),
  },
  Mazda: {
    'Mazda3':       Y(11000000, 2020),
    'CX-30':        Y(12000000, 2020),
    'CX-5':         Y(14000000, 2020),
    'CX-50':        Y(17000000, 2023),
    'CX-9':         Y(21000000, 2020),
    'CX-90':        Y(30000000, 2024),
  },
  'Mercedes-Benz': {
    'C-Class':      {2020:20000000, 2021:23000000, 2022:26000000, 2023:30000000, 2024:34000000, 2025:38000000},
    'E-Class':      {2020:28000000, 2021:32000000, 2022:36000000, 2023:42000000, 2024:48000000, 2025:55000000},
    'S-Class':      {2020:55000000, 2021:60000000, 2022:70000000, 2023:80000000, 2024:90000000, 2025:100000000},
    'CLA':          {2020:18000000, 2021:20000000, 2022:22000000, 2023:25000000, 2024:28000000, 2025:31000000},
    'GLA':          {2020:18000000, 2021:20000000, 2022:22000000, 2023:25000000, 2024:28000000, 2025:31000000},
    'GLB':          {2020:20000000, 2021:22000000, 2022:25000000, 2023:28000000, 2024:31000000, 2025:34000000},
    'GLC':          {2020:27000000, 2021:30000000, 2022:34000000, 2023:38000000, 2024:43000000, 2025:48000000},
    'GLE':          {2020:55500000, 2021:74700000, 2022:65500000, 2023:60500000, 2024:94100000, 2025:103100000},
    'GLS':          {2020:52000000, 2021:58000000, 2022:65000000, 2023:72000000, 2024:80000000, 2025:90000000},
    'G-Class':      {2020:85000000, 2021:90000000, 2022:95000000, 2023:100000000, 2024:110000000, 2025:120000000},
  },
  Mitsubishi: {
    'Eclipse Cross': Y(11000000, 2020),
    'Outlander':    Y(13000000, 2020),
    'Pajero Sport': Y(16000000, 2020),
  },
  Nissan: {
    'Sentra':       Y(9000000, 2020),
    'Altima':       Y(10000000, 2020),
    'Kicks':        Y(9000000, 2020),
    'Rogue':        Y(13000000, 2020),
    'Murano':       Y(17000000, 2020),
    'Pathfinder':   Y(20000000, 2020),
    'Armada':       Y(33000000, 2020),
    'Ariya':        Y(26000000, 2023),
  },
  Porsche: {
    'Macan':        Y(35000000, 2020),
    'Cayenne':      Y(55000000, 2020),
    'Cayenne Coupe':Y(60000000, 2020),
    'Panamera':     Y(58000000, 2020),
    'Taycan':       Y(58000000, 2020),
    '911':          Y(65000000, 2020),
  },
  RAM: {
    '1500':         Y(22000000, 2020),
    '1500 TRX':     Y(40000000, 2021),
    '2500':         Y(28000000, 2020),
  },
  Subaru: {
    'Outback':      Y(15000000, 2020),
    'Forester':     Y(14000000, 2020),
    'Crosstrek':    Y(12000000, 2020),
    'Ascent':       Y(19000000, 2020),
    'WRX':          Y(16000000, 2020),
  },
  Tesla: {
    'Model 3':      Y(20000000, 2020),
    'Model S':      Y(45000000, 2020),
    'Model X':      Y(50000000, 2020),
    'Model Y':      Y(24000000, 2020),
    'Cybertruck':   Y(45000000, 2024),
  },
  Toyota: {
    'Camry':        {2020:13700000, 2021:15400000, 2022:14100000, 2023:17000000, 2024:19900000, 2025:22200000},
    'Corolla':      {2020:9100000, 2021:9400000, 2022:9600000, 2023:11100000, 2024:13700000, 2025:15500000},
    'Corolla Cross': {2022:12500000, 2023:14000000, 2024:16000000, 2025:18000000},
    'RAV4':         {2020:14200000, 2021:14500000, 2022:15800000, 2023:17500000, 2024:17900000, 2025:21900000},
    'Highlander':   {2020:22300000, 2021:23800000, 2022:33000000, 2023:27700000, 2024:33500000, 2025:29200000},
    '4Runner':      {2020:24000000, 2021:25000000, 2022:27000000, 2023:29000000, 2024:32000000, 2025:35000000},
    'Prius':        {2020:11000000, 2021:12000000, 2022:13000000, 2023:14500000, 2024:16000000, 2025:17500000},
    'C-HR':         {2020:10500000, 2021:11000000, 2022:12000000, 2023:13000000, 2024:14500000, 2025:15500000},
    'Venza':        {2021:18000000, 2022:19500000, 2023:21000000, 2024:23000000, 2025:25000000},
    'Sienna':       {2020:18000000, 2021:19500000, 2022:21000000, 2023:23000000, 2024:25000000, 2025:27000000},
    'Sequoia':      {2020:35000000, 2021:37000000, 2022:40000000, 2023:45000000, 2024:50000000, 2025:55000000},
    'Tundra':       {2020:22000000, 2021:23000000, 2022:28000000, 2023:30000000, 2024:33000000, 2025:36000000},
    'Tacoma':       {2020:17000000, 2021:18000000, 2022:19500000, 2023:21000000, 2024:23000000, 2025:25000000},
    'Land Cruiser Prado': {2020:30000000, 2021:32000000, 2022:35000000, 2023:38000000, 2024:42000000, 2025:45000000},
    'Land Cruiser 300':   {2022:55000000, 2023:58000000, 2024:62000000, 2025:65000000},
    'Crown':        {2023:22000000, 2024:25000000, 2025:28000000},
    'bZ4X':         {2023:21000000, 2024:23000000, 2025:25000000},
    'Supra':        {2020:25000000, 2021:27000000, 2022:29000000, 2023:31000000, 2024:34000000, 2025:37000000},
  },
  Volkswagen: {
    'Jetta':        Y(10000000, 2020),
    'Passat':       Y(13000000, 2020),
    'Tiguan':       Y(15000000, 2020),
    'Atlas':        Y(21000000, 2020),
    'Atlas Cross Sport': Y(22000000, 2020),
    'Touareg':      Y(30000000, 2020),
    'ID.4':         Y(19000000, 2021),
    'Taos':         Y(13000000, 2022),
  },
  Volvo: {
    'S60':          Y(20000000, 2020),
    'S90':          Y(32000000, 2020),
    'XC40':         Y(22000000, 2020),
    'XC60':         Y(28000000, 2020),
    'XC90':         Y(40000000, 2020),
    'C40 Recharge': Y(28000000, 2022),
  },
};

const DISCOUNT = 0.35; // ~35% дешевле

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
    `💵 Рыночная цена в Казахстане: ${fmt(dealerPrice)}`,
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
