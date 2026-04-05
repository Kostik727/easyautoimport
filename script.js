// Burger menu
const burger = document.getElementById('burger');
const navLinks = document.querySelector('.nav__links');
const navBtn = document.querySelector('.nav__btn');

if (burger) {
  burger.addEventListener('click', () => {
    const isOpen = navLinks.style.display === 'flex';
    navLinks.style.display = isOpen ? 'none' : 'flex';
    navLinks.style.flexDirection = 'column';
    navLinks.style.position = 'absolute';
    navLinks.style.top = '68px';
    navLinks.style.left = '0';
    navLinks.style.right = '0';
    navLinks.style.background = 'rgba(5,7,11,0.97)';
    navLinks.style.padding = '16px 24px 20px';
    navLinks.style.borderBottom = '1px solid rgba(255,255,255,0.08)';
    burger.classList.toggle('open', !isOpen);
  });
}

// Scroll-based nav opacity
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) {
    nav.style.background = 'rgba(5,7,11,0.97)';
  } else {
    nav.style.background = 'rgba(5,7,11,0.8)';
  }
});

// Animate on scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.market-card, .adv-card, .step-card, .compare__bottom').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(28px)';
  el.style.transition = 'opacity 0.55s ease, transform 0.55s ease';
  observer.observe(el);
});

// CTA form
const form = document.getElementById('ctaForm');
if (form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const original = btn.textContent;
    btn.textContent = '✅ Заявка отправлена!';
    btn.disabled = true;
    btn.style.background = 'linear-gradient(135deg, #22c55e, #16a34a)';
    setTimeout(() => {
      btn.textContent = original;
      btn.disabled = false;
      btn.style.background = '';
      form.reset();
    }, 3500);
  });
}
