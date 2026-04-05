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
    'MDX':          Y(21000000, 2017),
    'RDX':          Y(16000000, 2017),
    'TLX':          Y(14500000, 2017),
    'ILX':          Y(10000000, 2017),
    'MDX Sport Hybrid': Y(24000000, 2017),
  },
  'Alfa Romeo': {
    'Stelvio':      Y(24000000, 2017),
    'Giulia':       Y(21000000, 2017),
    'Stelvio Quadrifoglio': Y(40000000, 2017),
    'Giulia Quadrifoglio':  Y(38000000, 2017),
  },
  Audi: {
    'A3':           Y(16000000, 2017),
    'A4':           Y(20000000, 2017),
    'A5':           Y(22000000, 2017),
    'A6':           Y(25000000, 2017),
    'A7':           Y(30000000, 2017),
    'A8':           Y(45000000, 2017),
    'Q3':           Y(18000000, 2017),
    'Q5':           Y(25000000, 2017),
    'Q7':           Y(37000000, 2017),
    'Q8':           Y(45000000, 2017),
    'SQ5':          Y(30000000, 2017),
    'SQ7':          Y(50000000, 2017),
    'RS6':          Y(55000000, 2020),
    'RS7':          Y(56000000, 2020),
    'e-tron':       Y(36000000, 2019),
    'e-tron GT':    Y(60000000, 2022),
    'Q4 e-tron':    Y(28000000, 2022),
  },
  BMW: {
    '1 Series':     Y(14000000, 2017),
    '2 Series':     Y(16000000, 2017),
    '3 Series':     Y(20000000, 2017),
    '4 Series':     Y(22000000, 2017),
    '5 Series':     Y(26000000, 2017),
    '6 Series':     Y(38000000, 2017),
    '7 Series':     Y(45000000, 2017),
    '8 Series':     Y(60000000, 2019),
    'X1':           Y(18000000, 2017),
    'X2':           Y(19000000, 2018),
    'X3':           Y(25000000, 2017),
    'X4':           Y(27000000, 2017),
    'X5':           Y(32000000, 2017),
    'X6':           Y(38000000, 2017),
    'X7':           Y(48000000, 2019),
    'M3':           Y(42000000, 2017),
    'M4':           Y(44000000, 2017),
    'M5':           Y(56000000, 2017),
    'M8':           Y(70000000, 2019),
    'i4':           Y(32000000, 2022),
    'iX':           Y(50000000, 2022),
    'i7':           Y(78000000, 2023),
  },
  Buick: {
    'Encore':       Y(10000000, 2017),
    'Encore GX':    Y(14000000, 2020),
    'Envision':     Y(17000000, 2017),
    'Enclave':      Y(22000000, 2017),
    'LaCrosse':     Y(18000000, 2017),
  },
  Cadillac: {
    'CT4':          Y(18000000, 2020),
    'CT5':          Y(22000000, 2020),
    'CT6':          Y(32000000, 2017),
    'XT4':          Y(20000000, 2019),
    'XT5':          Y(25000000, 2017),
    'XT6':          Y(30000000, 2020),
    'Escalade':     Y(46000000, 2017),
    'Escalade ESV': Y(50000000, 2017),
    'LYRIQ':        Y(42000000, 2023),
  },
  Chevrolet: {
    'Spark':        Y(6000000, 2017),
    'Sonic':        Y(7500000, 2017),
    'Cruze':        Y(8000000, 2017),
    'Malibu':       Y(11000000, 2017),
    'Impala':       Y(14000000, 2017),
    'Camaro':       Y(14000000, 2017),
    'Corvette':     Y(35000000, 2017),
    'Trax':         Y(9000000, 2017),
    'Equinox':      Y(12000000, 2017),
    'Blazer':       Y(16000000, 2019),
    'Traverse':     Y(18000000, 2017),
    'Tahoe':        Y(31000000, 2017),
    'Suburban':     Y(35000000, 2017),
    'Colorado':     Y(13000000, 2017),
    'Silverado 1500': Y(19000000, 2017),
    'Silverado 2500': Y(25000000, 2017),
    'Bolt EV':      Y(18000000, 2017),
    'Bolt EUV':     Y(20000000, 2022),
  },
  Chrysler: {
    'Pacifica':     Y(15000000, 2017),
    'Pacifica Hybrid': Y(17000000, 2017),
    '300':          Y(14000000, 2017),
  },
  Dodge: {
    'Charger':      Y(14000000, 2017),
    'Challenger':   Y(14000000, 2017),
    'Durango':      Y(22000000, 2017),
    'Journey':      Y(10000000, 2017),
    'Grand Caravan':Y(12000000, 2017),
  },
  Ford: {
    'Fiesta':       Y(6500000, 2017),
    'Focus':        Y(8000000, 2017),
    'Fusion':       Y(10000000, 2017),
    'Mustang':      Y(14000000, 2017),
    'Escape':       Y(11000000, 2017),
    'Edge':         Y(16000000, 2017),
    'Explorer':     Y(21000000, 2017),
    'Expedition':   Y(29000000, 2017),
    'F-150':        Y(21000000, 2017),
    'F-250':        Y(27000000, 2017),
    'F-350':        Y(30000000, 2017),
    'Ranger':       Y(16000000, 2019),
    'Bronco':       Y(18000000, 2021),
    'Bronco Sport': Y(14000000, 2021),
    'Maverick':     Y(12000000, 2022),
    'Mustang Mach-E': Y(26000000, 2021),
    'F-150 Lightning': Y(32000000, 2022),
  },
  Genesis: {
    'G70':          Y(18000000, 2019),
    'G80':          Y(26000000, 2017),
    'G90':          Y(40000000, 2017),
    'GV70':         Y(22000000, 2022),
    'GV80':         Y(30000000, 2021),
    'GV80 Coupe':   Y(34000000, 2023),
  },
  GMC: {
    'Canyon':       Y(13000000, 2017),
    'Sierra 1500':  Y(20000000, 2017),
    'Sierra 2500':  Y(27000000, 2017),
    'Terrain':      Y(12000000, 2017),
    'Acadia':       Y(19000000, 2017),
    'Yukon':        Y(32000000, 2017),
    'Yukon XL':     Y(36000000, 2017),
    'Envoy':        Y(16000000, 2017),
    'Hummer EV':    Y(65000000, 2022),
  },
  Honda: {
    'Fit':          Y(7000000, 2017),
    'Civic':        Y(9000000, 2017),
    'Accord':       Y(10000000, 2017),
    'Insight':      Y(11000000, 2019),
    'HR-V':         Y(10000000, 2017),
    'CR-V':         Y(12000000, 2017),
    'Passport':     Y(16000000, 2019),
    'Pilot':        Y(17000000, 2017),
    'Ridgeline':    Y(16000000, 2017),
    'Odyssey':      Y(15000000, 2017),
    'CR-V Hybrid':  Y(14000000, 2020),
    'Prologue':     Y(28000000, 2024),
  },
  Hyundai: {
    'Accent':       Y(6500000, 2017),
    'Elantra':      Y(7500000, 2017),
    'Sonata':       Y(9500000, 2017),
    'Azera':        Y(13000000, 2017),
    'Kona':         Y(9000000, 2018),
    'Tucson':       Y(11000000, 2017),
    'Santa Fe':     Y(15000000, 2017),
    'Santa Fe XL':  Y(18000000, 2017),
    'Palisade':     Y(20000000, 2020),
    'Venue':        Y(8500000, 2020),
    'IONIQ':        Y(12000000, 2017),
    'IONIQ 5':      Y(19000000, 2022),
    'IONIQ 6':      Y(18000000, 2023),
    'IONIQ 7':      Y(40000000, 2024),
    'Nexo':         Y(30000000, 2019),
  },
  Infiniti: {
    'Q50':          Y(15000000, 2017),
    'Q60':          Y(18000000, 2017),
    'Q70':          Y(22000000, 2017),
    'QX30':         Y(14000000, 2017),
    'QX50':         Y(18000000, 2017),
    'QX55':         Y(22000000, 2022),
    'QX60':         Y(23000000, 2017),
    'QX70':         Y(24000000, 2017),
    'QX80':         Y(37000000, 2017),
  },
  Jaguar: {
    'XE':           Y(18000000, 2017),
    'XF':           Y(25000000, 2017),
    'XJ':           Y(40000000, 2017),
    'E-Pace':       Y(20000000, 2018),
    'F-Pace':       Y(30000000, 2017),
    'F-Type':       Y(35000000, 2017),
    'I-Pace':       Y(36000000, 2019),
  },
  Jeep: {
    'Renegade':     Y(9000000, 2017),
    'Compass':      Y(11000000, 2017),
    'Cherokee':     Y(14000000, 2017),
    'Grand Cherokee': Y(20000000, 2017),
    'Grand Cherokee L': Y(26000000, 2022),
    'Grand Cherokee 4xe': Y(28000000, 2022),
    'Wrangler':     Y(17000000, 2017),
    'Wrangler 4xe': Y(22000000, 2021),
    'Gladiator':    Y(19000000, 2020),
    'Commander':    Y(24000000, 2022),
    'Wagoneer':     Y(40000000, 2022),
    'Grand Wagoneer': Y(55000000, 2022),
  },
  Kia: {
    'Rio':          Y(6000000, 2017),
    'Forte':        Y(8000000, 2017),
    'K5':           Y(10000000, 2021),
    'Stinger':      Y(16000000, 2018),
    'Soul':         Y(9000000, 2017),
    'Seltos':       Y(11000000, 2021),
    'Sportage':     Y(10500000, 2017),
    'Sorento':      Y(15000000, 2017),
    'Telluride':    Y(19000000, 2020),
    'Niro':         Y(11000000, 2017),
    'EV6':          Y(19000000, 2022),
    'EV9':          Y(36000000, 2024),
    'Carnival':     Y(15000000, 2021),
  },
  'Land Rover': {
    'Discovery Sport': Y(22000000, 2017),
    'Discovery':    Y(30000000, 2017),
    'Range Rover Evoque': Y(22000000, 2017),
    'Range Rover Velar':  Y(30000000, 2018),
    'Range Rover Sport':  Y(40000000, 2017),
    'Range Rover':        Y(55000000, 2017),
    'Defender 90':        Y(34000000, 2021),
    'Defender 110':       Y(36000000, 2021),
  },
  Lexus: {
    'CT':           Y(14000000, 2017),
    'IS':           Y(18000000, 2017),
    'ES':           Y(20000000, 2017),
    'GS':           Y(26000000, 2017),
    'LS':           Y(43000000, 2017),
    'LC':           Y(48000000, 2017),
    'UX':           Y(17000000, 2019),
    'NX':           Y(22000000, 2017),
    'RX':           Y(26000000, 2017),
    'RX L':         Y(29000000, 2018),
    'GX':           Y(29000000, 2017),
    'LX':           Y(52000000, 2017),
    'RZ':           Y(38000000, 2023),
  },
  Lincoln: {
    'MKZ':          Y(16000000, 2017),
    'MKC':          Y(18000000, 2017),
    'MKX':          Y(22000000, 2017),
    'MKT':          Y(22000000, 2017),
    'Corsair':      Y(19000000, 2020),
    'Nautilus':     Y(24000000, 2019),
    'Aviator':      Y(30000000, 2020),
    'Navigator':    Y(40000000, 2017),
    'Navigator L':  Y(44000000, 2017),
  },
  Mazda: {
    'Mazda2':       Y(7000000, 2017),
    'Mazda3':       Y(10000000, 2017),
    'Mazda6':       Y(11000000, 2017),
    'MX-5 Miata':   Y(10000000, 2017),
    'CX-3':         Y(9000000, 2017),
    'CX-30':        Y(12000000, 2020),
    'CX-5':         Y(13000000, 2017),
    'CX-50':        Y(15000000, 2023),
    'CX-9':         Y(19000000, 2017),
    'MX-30':        Y(18000000, 2022),
    'CX-90':        Y(28000000, 2024),
  },
  'Mercedes-Benz': {
    'A-Class':      Y(18000000, 2019),
    'C-Class':      Y(23000000, 2017),
    'E-Class':      Y(30000000, 2017),
    'S-Class':      Y(63000000, 2017),
    'CLA':          Y(20000000, 2017),
    'CLS':          Y(38000000, 2019),
    'GLA':          Y(20000000, 2017),
    'GLB':          Y(23000000, 2020),
    'GLC':          Y(30000000, 2017),
    'GLE':          Y(40000000, 2017),
    'GLS':          Y(52000000, 2017),
    'G-Class':      Y(92000000, 2017),
    'AMG GT':       Y(62000000, 2017),
    'C 63 AMG':     Y(45000000, 2017),
    'E 63 AMG':     Y(60000000, 2017),
    'EQS':          Y(70000000, 2022),
    'EQE':          Y(50000000, 2023),
    'EQB':          Y(32000000, 2022),
    'Maybach GLS':  Y(120000000, 2021),
  },
  Mitsubishi: {
    'Mirage':       Y(5500000, 2017),
    'Eclipse Cross': Y(9500000, 2018),
    'Outlander Sport': Y(10000000, 2017),
    'Outlander':    Y(11000000, 2017),
    'Outlander PHEV': Y(13000000, 2017),
    'Pajero Sport': Y(14000000, 2017),
    'Galant':       Y(10000000, 2017),
  },
  Nissan: {
    'Versa':        Y(6500000, 2017),
    'Sentra':       Y(8000000, 2017),
    'Altima':       Y(8500000, 2017),
    'Maxima':       Y(14000000, 2017),
    'GT-R':         Y(55000000, 2017),
    'Kicks':        Y(8000000, 2018),
    'Juke':         Y(9000000, 2017),
    'Rogue Sport':  Y(11000000, 2017),
    'Rogue':        Y(11500000, 2017),
    'Murano':       Y(15000000, 2017),
    'Pathfinder':   Y(17000000, 2017),
    'Armada':       Y(29000000, 2017),
    'Titan':        Y(17000000, 2017),
    'Titan XD':     Y(21000000, 2017),
    'LEAF':         Y(13000000, 2017),
    'Ariya':        Y(26000000, 2023),
    'Frontier':     Y(14000000, 2017),
    'Xterra':       Y(13000000, 2017),
  },
  Porsche: {
    'Macan':        Y(29000000, 2017),
    'Cayenne':      Y(45000000, 2017),
    'Cayenne Coupe':Y(50000000, 2020),
    'Panamera':     Y(50000000, 2017),
    'Taycan':       Y(58000000, 2020),
    'Taycan Sport Turismo': Y(60000000, 2021),
    '911':          Y(55000000, 2017),
    '718 Boxster':  Y(35000000, 2017),
    '718 Cayman':   Y(35000000, 2017),
  },
  RAM: {
    '1500':         Y(18000000, 2017),
    '1500 TRX':     Y(38000000, 2021),
    '2500':         Y(23000000, 2017),
    '3500':         Y(27000000, 2017),
    'ProMaster':    Y(13000000, 2017),
    'ProMaster City': Y(11000000, 2017),
  },
  Subaru: {
    'Impreza':      Y(9000000, 2017),
    'Legacy':       Y(12000000, 2017),
    'Outback':      Y(13000000, 2017),
    'Forester':     Y(12000000, 2017),
    'Crosstrek':    Y(10000000, 2017),
    'Ascent':       Y(17000000, 2019),
    'WRX':          Y(14000000, 2017),
    'BRZ':          Y(13000000, 2017),
    'Solterra':     Y(24000000, 2023),
  },
  Tesla: {
    'Model 3':      Y(17000000, 2018),
    'Model S':      Y(40000000, 2017),
    'Model X':      Y(46000000, 2017),
    'Model Y':      Y(22000000, 2020),
    'Cybertruck':   Y(38000000, 2024),
  },
  Toyota: {
    'Yaris':        Y(7000000, 2017),
    'Corolla':      Y(8000000, 2017),
    'Corolla Cross': Y(11000000, 2022),
    'Camry':        Y(10500000, 2017),
    'Avalon':       Y(16000000, 2017),
    'Prius':        Y(11000000, 2017),
    'Prius Prime':  Y(12000000, 2017),
    'C-HR':         Y(10000000, 2018),
    'RAV4':         Y(12500000, 2017),
    'RAV4 Prime':   Y(16000000, 2021),
    'Venza':        Y(16000000, 2021),
    'Highlander':   Y(18500000, 2017),
    'Highlander Hybrid': Y(21000000, 2017),
    '4Runner':      Y(20000000, 2017),
    'Fortuner':     Y(17000000, 2017),
    'Sequoia':      Y(31000000, 2017),
    'Tundra':       Y(20000000, 2017),
    'Tacoma':       Y(15000000, 2017),
    'Sienna':       Y(17000000, 2017),
    'Land Cruiser Prado': Y(28000000, 2017),
    'Land Cruiser 200':   Y(52000000, 2017),
    'Land Cruiser 300':   Y(55000000, 2022),
    'bZ4X':         Y(21000000, 2022),
    'GR86':         Y(14000000, 2022),
  },
  Volkswagen: {
    'Polo':         Y(7000000, 2017),
    'Jetta':        Y(9000000, 2017),
    'Passat':       Y(11000000, 2017),
    'Arteon':       Y(16000000, 2019),
    'Taos':         Y(13000000, 2022),
    'Tiguan':       Y(13000000, 2017),
    'Atlas':        Y(18500000, 2017),
    'Atlas Cross Sport': Y(20000000, 2020),
    'Touareg':      Y(26000000, 2017),
    'ID.4':         Y(19000000, 2021),
    'ID.6':         Y(24000000, 2022),
    'Golf GTI':     Y(13000000, 2017),
    'Golf R':       Y(18000000, 2017),
  },
  Volvo: {
    'S60':          Y(18000000, 2017),
    'S90':          Y(30000000, 2017),
    'V60':          Y(18000000, 2017),
    'V90':          Y(30000000, 2017),
    'XC40':         Y(20000000, 2018),
    'XC60':         Y(26000000, 2017),
    'XC90':         Y(36000000, 2017),
    'C40 Recharge': Y(28000000, 2022),
    'XC40 Recharge': Y(27000000, 2022),
    'EX90':         Y(50000000, 2024),
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
