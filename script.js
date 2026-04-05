// ===== CALCULATOR =====
const CAR_DATA = {
  Acura: {
    'MDX':          { 2020: 28000000, 2021: 31000000, 2022: 34000000, 2023: 38000000 },
    'RDX':          { 2020: 22000000, 2021: 24000000, 2022: 27000000, 2023: 30000000 },
    'TLX':          { 2021: 20000000, 2022: 22000000, 2023: 25000000 },
  },
  'Alfa Romeo': {
    'Stelvio':      { 2020: 32000000, 2021: 35000000, 2022: 38000000, 2023: 42000000 },
    'Giulia':       { 2020: 28000000, 2021: 31000000, 2022: 34000000, 2023: 37000000 },
  },
  Audi: {
    'Q3':           { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
    'Q5':           { 2020: 33000000, 2021: 37000000, 2022: 41000000, 2023: 45000000 },
    'Q7':           { 2020: 48000000, 2021: 53000000, 2022: 58000000, 2023: 64000000 },
    'Q8':           { 2020: 58000000, 2021: 64000000, 2022: 70000000, 2023: 78000000 },
    'A4':           { 2020: 26000000, 2021: 29000000, 2022: 32000000, 2023: 35000000 },
    'A6':           { 2020: 32000000, 2021: 36000000, 2022: 40000000, 2023: 44000000 },
    'A8':           { 2020: 58000000, 2021: 64000000, 2022: 70000000, 2023: 78000000 },
    'e-tron':       { 2020: 46000000, 2021: 50000000, 2022: 55000000, 2023: 61000000 },
  },
  BMW: {
    'X1':           { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
    'X3':           { 2020: 32000000, 2021: 36000000, 2022: 40000000, 2023: 44000000 },
    'X5':           { 2019: 42000000, 2020: 47000000, 2021: 52000000, 2022: 57000000, 2023: 63000000 },
    'X6':           { 2020: 50000000, 2021: 55000000, 2022: 61000000, 2023: 67000000 },
    'X7':           { 2020: 62000000, 2021: 68000000, 2022: 75000000, 2023: 83000000 },
    '3 Series':     { 2020: 26000000, 2021: 29000000, 2022: 32000000, 2023: 35000000 },
    '5 Series':     { 2020: 34000000, 2021: 38000000, 2022: 42000000, 2023: 46000000 },
    '7 Series':     { 2020: 58000000, 2021: 64000000, 2022: 70000000, 2023: 78000000 },
    'i4':           { 2022: 40000000, 2023: 44000000 },
    'iX':           { 2022: 62000000, 2023: 68000000 },
  },
  Buick: {
    'Enclave':      { 2020: 28000000, 2021: 31000000, 2022: 34000000, 2023: 37000000 },
    'Envision':     { 2021: 22000000, 2022: 24000000, 2023: 27000000 },
  },
  Cadillac: {
    'Escalade':     { 2020: 60000000, 2021: 66000000, 2022: 73000000, 2023: 80000000 },
    'XT5':          { 2020: 32000000, 2021: 35000000, 2022: 38000000, 2023: 42000000 },
    'XT6':          { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'CT5':          { 2020: 28000000, 2021: 31000000, 2022: 34000000, 2023: 37000000 },
  },
  Chevrolet: {
    'Equinox':      { 2020: 16000000, 2021: 18000000, 2022: 20000000, 2023: 22000000 },
    'Traverse':     { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
    'Tahoe':        { 2020: 40000000, 2021: 44000000, 2022: 48000000, 2023: 53000000 },
    'Suburban':     { 2020: 45000000, 2021: 50000000, 2022: 55000000, 2023: 61000000 },
    'Silverado':    { 2020: 25000000, 2021: 28000000, 2022: 31000000, 2023: 34000000 },
    'Blazer':       { 2020: 20000000, 2021: 22000000, 2022: 24000000, 2023: 27000000 },
  },
  Chrysler: {
    'Pacifica':     { 2020: 19000000, 2021: 21000000, 2022: 23000000, 2023: 25000000 },
  },
  Dodge: {
    'Durango':      { 2020: 28000000, 2021: 31000000, 2022: 34000000, 2023: 37000000 },
    'Challenger':   { 2020: 18000000, 2021: 20000000, 2022: 22000000, 2023: 24000000 },
    'Charger':      { 2020: 18000000, 2021: 20000000, 2022: 22000000, 2023: 24000000 },
  },
  Ford: {
    'Explorer':     { 2020: 28000000, 2021: 31000000, 2022: 34000000, 2023: 37000000 },
    'Expedition':   { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'F-150':        { 2020: 28000000, 2021: 31000000, 2022: 34000000, 2023: 38000000 },
    'Edge':         { 2020: 20000000, 2021: 22000000, 2022: 24000000, 2023: 27000000 },
    'Escape':       { 2020: 15000000, 2021: 17000000, 2022: 19000000, 2023: 21000000 },
    'Mustang':      { 2020: 18000000, 2021: 20000000, 2022: 22000000, 2023: 24000000 },
    'Bronco':       { 2021: 22000000, 2022: 25000000, 2023: 28000000 },
  },
  Genesis: {
    'GV80':         { 2021: 38000000, 2022: 42000000, 2023: 46000000 },
    'GV70':         { 2022: 28000000, 2023: 31000000 },
    'G80':          { 2021: 34000000, 2022: 38000000, 2023: 42000000 },
  },
  GMC: {
    'Yukon':        { 2020: 42000000, 2021: 46000000, 2022: 51000000, 2023: 56000000 },
    'Acadia':       { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
    'Sierra':       { 2020: 26000000, 2021: 29000000, 2022: 32000000, 2023: 35000000 },
    'Terrain':      { 2020: 16000000, 2021: 18000000, 2022: 20000000, 2023: 22000000 },
  },
  Honda: {
    'CR-V':         { 2020: 15000000, 2021: 17000000, 2022: 19000000, 2023: 21000000 },
    'Pilot':        { 2020: 22000000, 2021: 24000000, 2022: 27000000, 2023: 30000000 },
    'Passport':     { 2020: 20000000, 2021: 22000000, 2022: 24000000, 2023: 27000000 },
    'Accord':       { 2020: 13000000, 2021: 14500000, 2022: 16000000, 2023: 17500000 },
    'Odyssey':      { 2020: 19000000, 2021: 21000000, 2022: 23000000, 2023: 25000000 },
    'Ridgeline':    { 2020: 21000000, 2021: 23000000, 2022: 25000000, 2023: 28000000 },
  },
  Hyundai: {
    'Elantra':      { 2020: 10000000, 2021: 11500000, 2022: 13000000, 2023: 14500000 },
    'Sonata':       { 2020: 12500000, 2021: 14000000, 2022: 15500000, 2023: 17000000 },
    'Tucson':       { 2020: 14500000, 2021: 16000000, 2022: 17500000, 2023: 19500000 },
    'Santa Fe':     { 2020: 20000000, 2021: 22000000, 2022: 24500000, 2023: 27000000 },
    'Palisade':     { 2020: 26000000, 2021: 28500000, 2022: 31000000, 2023: 34000000 },
    'IONIQ 5':      { 2022: 24000000, 2023: 27000000 },
    'IONIQ 6':      { 2023: 22000000 },
  },
  Infiniti: {
    'QX60':         { 2020: 30000000, 2021: 33000000, 2022: 36000000, 2023: 40000000 },
    'QX80':         { 2020: 48000000, 2021: 53000000, 2022: 58000000, 2023: 64000000 },
    'Q50':          { 2020: 20000000, 2021: 22000000, 2022: 24000000, 2023: 26000000 },
  },
  Jaguar: {
    'F-Pace':       { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'XF':           { 2020: 32000000, 2021: 36000000, 2022: 40000000, 2023: 44000000 },
    'I-Pace':       { 2020: 46000000, 2021: 50000000, 2022: 55000000, 2023: 60000000 },
  },
  Jeep: {
    'Grand Cherokee': { 2020: 26000000, 2021: 28000000, 2022: 31000000, 2023: 34000000 },
    'Wrangler':     { 2020: 22000000, 2021: 24000000, 2022: 27000000, 2023: 30000000 },
    'Gladiator':    { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
    'Commander':    { 2022: 30000000, 2023: 33000000 },
  },
  Kia: {
    'Sportage':     { 2020: 13500000, 2021: 15000000, 2022: 16500000, 2023: 18500000 },
    'Sorento':      { 2020: 19500000, 2021: 21500000, 2022: 23500000, 2023: 26000000 },
    'Telluride':    { 2020: 24000000, 2021: 26000000, 2022: 28500000, 2023: 31000000 },
    'K5':           { 2021: 13000000, 2022: 14500000, 2023: 16000000 },
    'EV6':          { 2022: 24000000, 2023: 27000000 },
    'Carnival':     { 2021: 19000000, 2022: 21000000, 2023: 23000000 },
  },
  'Land Rover': {
    'Range Rover':        { 2020: 70000000, 2021: 77000000, 2022: 85000000, 2023: 94000000 },
    'Range Rover Sport':  { 2020: 52000000, 2021: 57000000, 2022: 63000000, 2023: 70000000 },
    'Defender':           { 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'Discovery':          { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
  },
  Lexus: {
    'NX':           { 2021: 28000000, 2022: 32000000, 2023: 36000000 },
    'RX':           { 2020: 34000000, 2021: 38000000, 2022: 42000000, 2023: 47000000 },
    'GX':           { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'LX':           { 2021: 68000000, 2022: 75000000, 2023: 84000000 },
    'ES':           { 2020: 26000000, 2021: 29000000, 2022: 32000000, 2023: 35000000 },
    'LS':           { 2020: 56000000, 2021: 62000000, 2022: 68000000, 2023: 75000000 },
  },
  Lincoln: {
    'Navigator':    { 2020: 52000000, 2021: 57000000, 2022: 63000000, 2023: 70000000 },
    'Aviator':      { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'Corsair':      { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
  },
  Mazda: {
    'CX-5':         { 2020: 16000000, 2021: 18000000, 2022: 20000000, 2023: 22000000 },
    'CX-9':         { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
    'CX-50':        { 2022: 19000000, 2023: 21000000 },
    'Mazda6':       { 2020: 14000000, 2021: 15500000, 2022: 17000000, 2023: 18500000 },
  },
  'Mercedes-Benz': {
    'GLA':          { 2021: 30000000, 2022: 33000000, 2023: 37000000 },
    'GLC':          { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'GLE':          { 2020: 52000000, 2021: 57000000, 2022: 63000000, 2023: 70000000 },
    'GLS':          { 2020: 68000000, 2021: 75000000, 2022: 83000000, 2023: 91000000 },
    'G-Class':      { 2020: 120000000, 2021: 130000000, 2022: 143000000, 2023: 157000000 },
    'C-Class':      { 2020: 30000000, 2021: 33000000, 2022: 36000000, 2023: 40000000 },
    'E-Class':      { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'S-Class':      { 2021: 82000000, 2022: 90000000, 2023: 99000000 },
    'EQS':          { 2022: 90000000, 2023: 99000000 },
  },
  Mitsubishi: {
    'Outlander':    { 2020: 14000000, 2021: 16000000, 2022: 18000000, 2023: 20000000 },
    'Eclipse Cross': { 2020: 12000000, 2021: 13500000, 2022: 15000000, 2023: 16500000 },
    'Pajero Sport': { 2020: 18000000, 2021: 20000000, 2022: 22000000, 2023: 24000000 },
  },
  Nissan: {
    'Pathfinder':   { 2020: 22000000, 2021: 24000000, 2022: 27000000, 2023: 30000000 },
    'Armada':       { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'Murano':       { 2020: 20000000, 2021: 22000000, 2022: 24000000, 2023: 27000000 },
    'Rogue':        { 2020: 15000000, 2021: 17000000, 2022: 19000000, 2023: 21000000 },
    'Altima':       { 2020: 11000000, 2021: 12500000, 2022: 14000000, 2023: 15500000 },
    'Titan':        { 2020: 22000000, 2021: 25000000, 2022: 28000000, 2023: 31000000 },
  },
  Porsche: {
    'Cayenne':      { 2020: 58000000, 2021: 64000000, 2022: 70000000, 2023: 77000000 },
    'Macan':        { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
    'Panamera':     { 2020: 64000000, 2021: 70000000, 2022: 77000000, 2023: 85000000 },
    'Taycan':       { 2021: 75000000, 2022: 83000000, 2023: 91000000 },
  },
  RAM: {
    '1500':         { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
    '2500':         { 2020: 30000000, 2021: 33000000, 2022: 37000000, 2023: 41000000 },
    'ProMaster':    { 2020: 16000000, 2021: 18000000, 2022: 20000000, 2023: 22000000 },
  },
  Subaru: {
    'Outback':      { 2020: 16000000, 2021: 18000000, 2022: 20000000, 2023: 22000000 },
    'Forester':     { 2020: 15000000, 2021: 17000000, 2022: 19000000, 2023: 21000000 },
    'Ascent':       { 2020: 22000000, 2021: 24000000, 2022: 27000000, 2023: 30000000 },
  },
  Tesla: {
    'Model 3':      { 2020: 22000000, 2021: 24000000, 2022: 27000000, 2023: 30000000 },
    'Model Y':      { 2021: 28000000, 2022: 31000000, 2023: 34000000 },
    'Model S':      { 2020: 52000000, 2021: 57000000, 2022: 63000000, 2023: 70000000 },
    'Model X':      { 2020: 60000000, 2021: 66000000, 2022: 73000000, 2023: 80000000 },
  },
  Toyota: {
    'Corolla':      { 2020: 10500000, 2021: 12000000, 2022: 13500000, 2023: 15000000 },
    'Camry':        { 2019: 13500000, 2020: 15200000, 2021: 16800000, 2022: 18500000, 2023: 21000000 },
    'RAV4':         { 2019: 16000000, 2020: 18000000, 2021: 20000000, 2022: 22500000, 2023: 25000000 },
    'Highlander':   { 2020: 24000000, 2021: 26500000, 2022: 29000000, 2023: 32000000 },
    'Sequoia':      { 2020: 40000000, 2021: 44000000, 2022: 52000000, 2023: 57000000 },
    'Tundra':       { 2020: 26000000, 2021: 29000000, 2022: 35000000, 2023: 39000000 },
    'Fortuner':     { 2020: 22000000, 2021: 24000000, 2022: 26500000, 2023: 29000000 },
    'Land Cruiser Prado': { 2020: 36000000, 2021: 39000000, 2022: 43000000, 2023: 48000000 },
    'Land Cruiser 300':   { 2021: 68000000, 2022: 74000000, 2023: 82000000 },
    'Sienna':       { 2021: 22000000, 2022: 24000000, 2023: 27000000 },
    'bZ4X':         { 2022: 26000000, 2023: 29000000 },
  },
  Volkswagen: {
    'Tiguan':       { 2020: 17000000, 2021: 19000000, 2022: 21000000, 2023: 23000000 },
    'Atlas':        { 2020: 24000000, 2021: 27000000, 2022: 30000000, 2023: 33000000 },
    'ID.4':         { 2021: 24000000, 2022: 27000000, 2023: 30000000 },
    'Touareg':      { 2020: 34000000, 2021: 38000000, 2022: 42000000, 2023: 46000000 },
    'Passat':       { 2020: 14000000, 2021: 15500000, 2022: 17000000, 2023: 18500000 },
  },
  Volvo: {
    'XC60':         { 2020: 34000000, 2021: 38000000, 2022: 42000000, 2023: 46000000 },
    'XC90':         { 2020: 46000000, 2021: 51000000, 2022: 56000000, 2023: 62000000 },
    'XC40':         { 2020: 26000000, 2021: 29000000, 2022: 32000000, 2023: 35000000 },
    'S90':          { 2020: 38000000, 2021: 42000000, 2022: 46000000, 2023: 51000000 },
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
