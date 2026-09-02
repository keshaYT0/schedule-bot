document.addEventListener('DOMContentLoaded', () => {
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.ready();
    tg.expand();
    try {
      tg.setHeaderColor?.('#07080b');
      tg.setBackgroundColor?.('#07080b');
    } catch (e) {
      // Ignore
    }
  }

  function triggerHaptic(type = 'light') {
    try {
      if (tg?.HapticFeedback) {
        if (type === 'selection') tg.HapticFeedback.selectionChanged();
        else if (type === 'success') tg.HapticFeedback.notificationOccurred('success');
        else tg.HapticFeedback.impactOccurred(type);
      }
    } catch (e) {
      // Ignore
    }
  }

  // State
  let scheduleData = null;
  let bellsData = [];
  let statusData = null;
  let activeDay = 'Monday';
  let searchQuery = '';

  // Elements
  const currentDateBadge = document.getElementById('currentDateBadge');
  const liveHeroCard = document.getElementById('liveHeroCard');
  const liveStatusPill = document.getElementById('liveStatusPill');
  const liveStatusText = document.getElementById('liveStatusText');
  const liveClock = document.getElementById('liveClock');
  const liveHeroContent = document.getElementById('liveHeroContent');
  const survivalVal = document.getElementById('survivalVal');
  const survivalTrack = document.getElementById('survivalTrack');
  const daysNav = document.getElementById('daysNav');
  const selectedDayName = document.getElementById('selectedDayName');
  const lessonsCountBadge = document.getElementById('lessonsCountBadge');
  const lessonsList = document.getElementById('lessonsList');
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const burgerBtn = document.getElementById('burgerBtn');
  const closeDrawerBtn = document.getElementById('closeDrawerBtn');
  const drawerBackdrop = document.getElementById('drawerBackdrop');
  const drawerBellsList = document.getElementById('drawerBellsList');
  const quickBellsBtn = document.getElementById('quickBellsBtn');

  // Minimalist Monochrome SVG Icons
  const ICONS = {
    code: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>`,
    database: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>`,
    cpu: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>`,
    mobile: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>`,
    chart: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>`,
    activity: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>`,
    briefcase: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>`,
    user: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
    pin: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>`,
    clock: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
  };

  function getSubjectIcon(name) {
    const s = name.toLowerCase();
    if (s.includes('web-дизайн') || s.includes('программный код')) return ICONS.code;
    if (s.includes('mysql') || s.includes('база данных')) return ICONS.database;
    if (s.includes('робототехника') || s.includes('роботизированного')) return ICONS.cpu;
    if (s.includes('мобильные приложения') || s.includes('мобильных')) return ICONS.mobile;
    if (s.includes('экономики') || s.includes('экономической')) return ICONS.chart;
    if (s.includes('физическая культура') || s.includes('спорт')) return ICONS.activity;
    if (s.includes('бизнеса') || s.includes('договоров')) return ICONS.briefcase;
    return ICONS.code;
  }

  function toMinutes(timeStr) {
    const [h, m] = timeStr.split(':').map(Number);
    return h * 60 + m;
  }

  // Fetch Data
  async function loadData() {
    try {
      const [schedRes, bellsRes, statusRes] = await Promise.all([
        fetch('/api/schedule').then(r => r.json()),
        fetch('/api/bells').then(r => r.json()),
        fetch('/api/status').then(r => r.json())
      ]);

      scheduleData = schedRes;
      bellsData = bellsRes.bells || [];
      statusData = statusRes;

      if (statusData) {
        currentDateBadge.textContent = `${statusData.day_ru} // ${statusData.date_str}`;
        liveClock.textContent = statusData.time_str;

        markTodayTab(statusData.day_name);

        if (!statusData.is_weekend && scheduleData.days[statusData.day_name]) {
          activeDay = statusData.day_name;
        } else {
          activeDay = 'Monday';
        }
      }

      renderHero();
      renderDayTabs();
      renderLessons();
      renderDrawerBells();
    } catch (err) {
      console.error('Error loading schedule:', err);
      lessonsList.innerHTML = `
        <div class="empty-box">
          <div class="empty-box-title">СБОЙ СИНХРОНИЗАЦИИ</div>
          <p>Не удалось получить данные с сервера. Попробуйте обновить страницу.</p>
        </div>
      `;
    }
  }

  function markTodayTab(todayName) {
    document.querySelectorAll('.tab-pill').forEach(tab => {
      const isToday = tab.dataset.day === todayName;
      tab.classList.toggle('is-today', isToday);
    });
  }

  function renderHero() {
    if (!statusData) return;

    liveClock.textContent = statusData.time_str;
    liveHeroCard.className = 'bento-hero';

    const lessons = scheduleData?.days[statusData.day_name] || [];
    const totalPairs = lessons.length;
    let completedCount = 0;

    const cur = statusData.current_lesson;
    const nextL = statusData.next_lesson;

    if (statusData.is_weekend) {
      liveStatusText.textContent = 'ВЫХОДНОЙ';
      liveHeroContent.innerHTML = `
        <div class="hero-subject-name">Занятий нет. Полный релакс.</div>
        <div class="hero-chips-row">
          <span class="mono-chip">✦ WEEKEND VIBES</span>
        </div>
      `;
      survivalVal.textContent = '0 / 0 ПАР';
      survivalTrack.innerHTML = '';
      return;
    }

    // Determine day progress
    if (statusData.time_str) {
      const nowMin = toMinutes(statusData.time_str);
      lessons.forEach(l => {
        if (toMinutes(l.end) < nowMin) completedCount++;
      });
    }

    if (cur) {
      liveHeroCard.classList.add('is-live');
      liveStatusText.textContent = 'LIVE // ИДЕТ ПАРА';

      const totalDuration = toMinutes(cur.end) - toMinutes(cur.start);
      const elapsed = totalDuration - cur.left;
      const progressPercent = Math.min(100, Math.max(0, Math.round((elapsed / totalDuration) * 100)));

      const roomChip = (cur.room && cur.room !== '—')
        ? `<span class="mono-chip room-chip">${ICONS.pin} ${escapeHtml(cur.room)}</span>`
        : '';
      const numLabel = cur.num ? `${cur.num} ПАРА · ` : '';

      liveHeroContent.innerHTML = `
        <div class="hero-subject-name">${numLabel}${escapeHtml(cur.name)}</div>
        <div class="hero-chips-row">
          <span class="mono-chip">${ICONS.user} ${escapeHtml(cur.teacher)}</span>
          ${roomChip}
          <span class="mono-chip timer-chip">${ICONS.clock} ОСТАЛОСЬ ${cur.left} МИН</span>
        </div>
        <div class="hero-progress-line">
          <div class="hero-progress-fill" style="width: ${progressPercent}%"></div>
        </div>
      `;
    } else if (nextL) {
      liveHeroCard.classList.add('is-upcoming');
      liveStatusText.textContent = `СКОРО ПАРА // ЧЕРЕЗ ${nextL.starts_in}М`;

      const roomChip = (nextL.room && nextL.room !== '—')
        ? `<span class="mono-chip room-chip">${ICONS.pin} ${escapeHtml(nextL.room)}</span>`
        : '';
      const numLabel = nextL.num ? `${nextL.num} ПАРА · ` : '';

      liveHeroContent.innerHTML = `
        <div class="hero-subject-name">Следующая: ${numLabel}${escapeHtml(nextL.name)}</div>
        <div class="hero-chips-row">
          <span class="mono-chip">${ICONS.clock} СТАРТ В ${nextL.start}</span>
          ${roomChip}
          <span class="mono-chip">${ICONS.user} ${escapeHtml(nextL.teacher)}</span>
        </div>
      `;
    } else {
      liveStatusText.textContent = 'ФИНИШ';
      liveHeroContent.innerHTML = `
        <div class="hero-subject-name">На сегодня все пары завершены</div>
        <div class="hero-chips-row">
          <span class="mono-chip">✦ СВОБОДЕН</span>
        </div>
      `;
      completedCount = totalPairs;
    }

    // Render survival blocks
    survivalVal.textContent = `${completedCount} / ${totalPairs} ПАР`;
    survivalTrack.innerHTML = Array.from({ length: totalPairs }, (_, i) => {
      let cls = 'survival-block';
      if (cur && i === completedCount) cls += ' current';
      else if (i < completedCount) cls += ' completed';
      return `<div class="${cls}"></div>`;
    }).join('');
  }

  function renderDayTabs() {
    document.querySelectorAll('.tab-pill').forEach(tab => {
      const day = tab.dataset.day;
      const isActive = day === activeDay;
      tab.classList.toggle('active', isActive);
    });
  }

  function renderLessons() {
    if (!scheduleData) return;

    const dayRu = scheduleData.days_ru[activeDay] || activeDay;
    selectedDayName.textContent = dayRu.toUpperCase();

    const lessons = scheduleData.days[activeDay] || [];
    const filtered = lessons.filter(item => {
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      return (
        item.name.toLowerCase().includes(q) ||
        item.teacher.toLowerCase().includes(q) ||
        item.room.toLowerCase().includes(q)
      );
    });

    lessonsCountBadge.textContent = `${filtered.length} ПАР`;

    if (filtered.length === 0) {
      lessonsList.innerHTML = `
        <div class="empty-box">
          <div class="empty-box-title">${searchQuery ? 'НИЧЕГО НЕ НАЙДЕНО' : 'ВЫХОДНОЙ ДЕНЬ'}</div>
          <p>${searchQuery ? 'Попробуйте изменить поисковый запрос' : 'В этот день занятий нет в расписании'}</p>
        </div>
      `;
      return;
    }

    const isToday = statusData && statusData.day_name === activeDay;
    const currentLesson = isToday ? statusData.current_lesson : null;

    lessonsList.innerHTML = filtered.map((lesson, idx) => {
      const pairNumber = lesson.num || (idx + 1);
      const isCurrent = currentLesson && currentLesson.name === lesson.name && currentLesson.start === lesson.start;
      const roomBadge = (lesson.room && lesson.room !== '—')
        ? `<span class="room-tag">${ICONS.pin} ${escapeHtml(lesson.room)}</span>`
        : '';
      const subjectIcon = getSubjectIcon(lesson.name);

      return `
        <article class="timeline-card ${isCurrent ? 'is-current' : ''}">
          <div class="card-meta-line">
            <span class="time-badge">
              ${ICONS.clock} ${lesson.start} – ${lesson.end}
            </span>
            ${isCurrent ? '<span class="current-live-tag">LIVE // СЕЙЧАС</span>' : `<span class="pair-index-badge">ПАРА ${pairNumber < 10 ? '0' + pairNumber : pairNumber}</span>`}
          </div>
          <div class="card-subject-row">
            <div class="category-icon-box">
              ${subjectIcon}
            </div>
            <div class="card-subject-title">${escapeHtml(lesson.name)}</div>
          </div>
          <div class="card-bottom-chips">
            <span class="teacher-chip">
              ${ICONS.user} ${escapeHtml(lesson.teacher)}
            </span>
            ${roomBadge}
          </div>
        </article>
      `;
    }).join('');
  }

  function renderDrawerBells() {
    if (!bellsData.length) return;
    drawerBellsList.innerHTML = bellsData.map(b => `
      <div class="bell-row-chip">
        <span class="b-name">${escapeHtml(b.name)}</span>
        <span class="b-time">${b.start} – ${b.end}</span>
      </div>
    `).join('');
  }

  function openDrawer() {
    drawerBackdrop.classList.remove('hidden');
    triggerHaptic('light');
    if (tg?.BackButton) {
      tg.BackButton.show();
      tg.BackButton.onClick(closeDrawer);
    }
  }

  function closeDrawer() {
    drawerBackdrop.classList.add('hidden');
    triggerHaptic('light');
    if (tg?.BackButton) {
      tg.BackButton.hide();
      tg.BackButton.offClick(closeDrawer);
    }
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Listeners
  daysNav.addEventListener('click', (e) => {
    const tab = e.target.closest('.tab-pill');
    if (!tab) return;
    const day = tab.dataset.day;
    if (day && day !== activeDay) {
      activeDay = day;
      triggerHaptic('selection');
      renderDayTabs();
      renderLessons();
    }
  });

  searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value.trim();
    clearSearchBtn.classList.toggle('hidden', searchQuery.length === 0);
    renderLessons();
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchQuery = '';
    clearSearchBtn.classList.add('hidden');
    triggerHaptic('light');
    renderLessons();
    searchInput.focus();
  });

  burgerBtn.addEventListener('click', openDrawer);
  quickBellsBtn.addEventListener('click', openDrawer);
  closeDrawerBtn.addEventListener('click', closeDrawer);
  drawerBackdrop.addEventListener('click', (e) => {
    if (e.target === drawerBackdrop) closeDrawer();
  });

  // Auto-refresh clock & status
  setInterval(async () => {
    try {
      const statusRes = await fetch('/api/status').then(r => r.json());
      statusData = statusRes;
      renderHero();
      if (statusData.day_name === activeDay) {
        renderLessons();
      }
    } catch (e) {
      // Background silent
    }
  }, 25000);

  // Initial load
  loadData();
});
