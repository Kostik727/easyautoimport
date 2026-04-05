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
