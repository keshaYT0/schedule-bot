document.addEventListener('DOMContentLoaded', () => {
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.ready();
    tg.expand();
  }

  function triggerHaptic(type = 'light') {
    try {
      if (tg?.HapticFeedback) {
        if (type === 'selection') tg.HapticFeedback.selectionChanged();
        else if (type === 'success') tg.HapticFeedback.notificationOccurred('success');
        else tg.HapticFeedback.impactOccurred(type);
      }
    } catch (e) {
      // Ignore if not supported
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
  const liveStatusCard = document.getElementById('liveStatusCard');
  const liveStatusLabel = document.getElementById('liveStatusLabel');
  const liveClock = document.getElementById('liveClock');
  const liveStatusBody = document.getElementById('liveStatusBody');
  const daysNav = document.getElementById('daysNav');
  const selectedDayName = document.getElementById('selectedDayName');
  const lessonsCountBadge = document.getElementById('lessonsCountBadge');
  const lessonsList = document.getElementById('lessonsList');
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const openBellsBtn = document.getElementById('openBellsBtn');
  const closeBellsBtn = document.getElementById('closeBellsBtn');
  const bellsModal = document.getElementById('bellsModal');
  const bellsList = document.getElementById('bellsList');
  const refreshBtn = document.getElementById('refreshBtn');

  // Convert "HH:MM" to minutes from start of day
  function toMinutes(timeStr) {
    const [h, m] = timeStr.split(':').map(Number);
    return h * 60 + m;
  }

  // Fetch all initial data
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

      // Set date & clock
      if (statusData) {
        currentDateBadge.textContent = `${statusData.day_ru}, ${statusData.date_str}`;
        liveClock.textContent = statusData.time_str;

        // Mark today tab
        markTodayTab(statusData.day_name);

        // Set default active tab
        if (!statusData.is_weekend && scheduleData.days[statusData.day_name]) {
          activeDay = statusData.day_name;
        } else {
          activeDay = 'Monday';
        }
      }

      renderStatusWidget();
      renderDayTabs();
      renderLessons();
      renderBellsModal();
    } catch (err) {
      console.error('Error loading schedule:', err);
      lessonsList.innerHTML = `
        <div class="empty-state">
          <h3>Ошибка загрузки</h3>
          <p>Не удалось получить данные расписания. Проверьте соединение.</p>
        </div>
      `;
    }
  }

  function markTodayTab(todayName) {
    document.querySelectorAll('.day-tab').forEach(tab => {
      const isToday = tab.dataset.day === todayName;
      tab.classList.toggle('is-today', isToday);
    });
  }

  function renderStatusWidget() {
    if (!statusData) return;

    liveClock.textContent = statusData.time_str;
    liveStatusCard.className = 'live-status-card';

    if (statusData.is_weekend) {
      liveStatusLabel.textContent = 'Выходной';
      liveStatusBody.innerHTML = `
        <div class="live-lesson-title">Сегодня пар нет 🎉</div>
        <div class="live-lesson-meta">Хороших выходных!</div>
      `;
      return;
    }

    const current = statusData.current_lesson;
    const nextL = statusData.next_lesson;

    if (current) {
      liveStatusCard.classList.add('active-lesson');
      liveStatusLabel.textContent = 'Идет пара';

      const totalDuration = toMinutes(current.end) - toMinutes(current.start);
      const elapsed = totalDuration - current.left;
      const progressPercent = Math.min(100, Math.max(0, Math.round((elapsed / totalDuration) * 100)));

      const roomHtml = (current.room && current.room !== '—') ? `<span>📍 ${escapeHtml(current.room)}</span>` : '';
      const numPrefix = current.num ? `${current.num} пара: ` : '';

      liveStatusBody.innerHTML = `
        <div class="live-lesson-title">${numPrefix}${escapeHtml(current.name)}</div>
        <div class="live-lesson-meta">
          <span>👨‍🏫 ${escapeHtml(current.teacher)}</span>
          ${roomHtml}
          <span>⏰ Осталось ${current.left} мин.</span>
        </div>
        <div class="progress-container">
          <div class="progress-bar" style="width: ${progressPercent}%"></div>
        </div>
      `;
    } else if (nextL) {
      liveStatusCard.classList.add('upcoming-lesson');
      liveStatusLabel.textContent = 'Скоро пара';
      const roomHtml = (nextL.room && nextL.room !== '—') ? `<span>📍 ${escapeHtml(nextL.room)}</span>` : '';
      const numPrefix = nextL.num ? `${nextL.num} пара: ` : '';

      liveStatusBody.innerHTML = `
        <div class="live-lesson-title">Следующая: ${numPrefix}${escapeHtml(nextL.name)}</div>
        <div class="live-lesson-meta">
          <span>⏰ Начало в ${nextL.start} (через ${nextL.starts_in} мин.)</span>
          ${roomHtml}
          <span>👨‍🏫 ${escapeHtml(nextL.teacher)}</span>
        </div>
      `;
    } else {
      liveStatusLabel.textContent = 'Пар нет';
      liveStatusBody.innerHTML = `
        <div class="live-lesson-title">На сегодня занятия окончены</div>
        <div class="live-lesson-meta">Отличная работа! Отдыхайте.</div>
      `;
    }
  }

  function renderDayTabs() {
    document.querySelectorAll('.day-tab').forEach(tab => {
      const day = tab.dataset.day;
      const isActive = day === activeDay;
      tab.classList.toggle('active', isActive);
    });
  }

  function renderLessons() {
    if (!scheduleData) return;

    const dayRu = scheduleData.days_ru[activeDay] || activeDay;
    selectedDayName.textContent = dayRu;

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

    lessonsCountBadge.textContent = `${filtered.length} ${getNounPlural(filtered.length, 'пара', 'пары', 'пар')}`;

    if (filtered.length === 0) {
      lessonsList.innerHTML = `
        <div class="empty-state">
          <h3>${searchQuery ? 'Ничего не найдено' : 'Выходной день'}</h3>
          <p>${searchQuery ? 'Попробуйте изменить поисковый запрос' : 'В этот день занятий нет'}</p>
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
        ? `<span class="info-chip room-chip">📍 ${escapeHtml(lesson.room)}</span>`
        : '';

      return `
        <article class="lesson-card ${isCurrent ? 'now-active' : ''}">
          <div class="card-top">
            <span class="lesson-time-pill">
              🕒 ${lesson.start} – ${lesson.end}
            </span>
            <span class="lesson-index">
              ${isCurrent ? '<span class="now-tag">Сейчас</span>' : `${pairNumber} пара`}
            </span>
          </div>
          <h3 class="lesson-name">${escapeHtml(lesson.name)}</h3>
          <div class="card-details">
            <span class="info-chip">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              ${escapeHtml(lesson.teacher)}
            </span>
            ${roomBadge}
          </div>
        </article>
      `;
    }).join('');

  }

  function renderBellsModal() {
    if (!bellsData.length) return;
    bellsList.innerHTML = `
      <div class="bells-table">
        ${bellsData.map(b => `
          <div class="bells-row">
            <span class="bells-name">${escapeHtml(b.name)}</span>
            <span class="bells-time">${b.start} – ${b.end}</span>
          </div>
        `).join('')}
      </div>
    `;
  }

  function openModal() {
    bellsModal.classList.remove('hidden');
    triggerHaptic('light');
    if (tg?.BackButton) {
      tg.BackButton.show();
      tg.BackButton.onClick(closeModal);
    }
  }

  function closeModal() {
    bellsModal.classList.add('hidden');
    triggerHaptic('light');
    if (tg?.BackButton) {
      tg.BackButton.hide();
      tg.BackButton.offClick(closeModal);
    }
  }

  function getNounPlural(number, one, two, five) {
    let n = Math.abs(number);
    n %= 100;
    if (n >= 5 && n <= 20) return five;
    n %= 10;
    if (n === 1) return one;
    if (n >= 2 && n <= 4) return two;
    return five;
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Event Listeners
  daysNav.addEventListener('click', (e) => {
    const tab = e.target.closest('.day-tab');
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

  openBellsBtn.addEventListener('click', openModal);
  closeBellsBtn.addEventListener('click', closeModal);
  bellsModal.addEventListener('click', (e) => {
    if (e.target === bellsModal) closeModal();
  });

  refreshBtn.addEventListener('click', async () => {
    triggerHaptic('medium');
    refreshBtn.style.transform = 'rotate(180deg)';
    setTimeout(() => { refreshBtn.style.transform = ''; }, 300);
    try {
      const statusRes = await fetch('/api/status').then(r => r.json());
      statusData = statusRes;
      renderStatusWidget();
      renderLessons();
      triggerHaptic('success');
    } catch (e) {
      console.error('Refresh error:', e);
    }
  });

  // Auto-refresh status every 30 seconds
  setInterval(async () => {
    try {
      const statusRes = await fetch('/api/status').then(r => r.json());
      statusData = statusRes;
      renderStatusWidget();
      if (statusData.day_name === activeDay) {
        renderLessons();
      }
    } catch (e) {
      // Silent error in background
    }
  }, 30000);

  // Initial load
  loadData();
});
