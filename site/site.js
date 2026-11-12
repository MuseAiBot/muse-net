(() => {
  const config = window.FEDNET_SITE || {title:'MuseAi-FED-NET', url:'https://museai-fed-net.pages.dev'};
  document.querySelectorAll('[data-site-title]').forEach(el => el.textContent = config.title);
  document.querySelectorAll('[data-site-url]').forEach(el => { el.textContent = config.url; el.href = config.url; });
  const cursor = document.querySelector('.cursor-glow');
  window.addEventListener('pointermove', e => { if (cursor) { cursor.style.left = e.clientX + 'px'; cursor.style.top = e.clientY + 'px'; }});
  const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); }), {threshold:.12});
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();


(() => {
  const gate = document.getElementById('nsfwGate');
  const trigger = document.getElementById('nsfwDiscordBtn');
  const check = document.getElementById('nsfwAgeCheck');
  const confirm = document.getElementById('nsfwConfirm');
  const cancel = document.getElementById('nsfwCancel');
  const request = document.getElementById('nsfwEmailRequest');
  if (!gate || !trigger || !check || !confirm || !cancel || !request) return;

  trigger.addEventListener('click', event => {
    event.preventDefault();
    check.checked = false;
    confirm.disabled = true;
    request.hidden = true;
    gate.showModal();
  });
  check.addEventListener('change', () => { confirm.disabled = !check.checked; });
  confirm.addEventListener('click', () => {
    if (!check.checked) return;
    request.hidden = false;
    confirm.hidden = true;
    cancel.textContent = 'Close';
  });
  cancel.addEventListener('click', () => { gate.close(); trigger.focus(); });
  gate.addEventListener('click', event => { if (event.target === gate) gate.close(); });
})();

(() => {
  const current = (window.location.pathname.split('/').pop() || 'index.html').toLowerCase();
  document.querySelectorAll('.nav a').forEach(link => {
    const target = (link.getAttribute('href') || '').split('/').pop().toLowerCase();
    if (target === current) link.setAttribute('aria-current', 'page');
  });
})();
