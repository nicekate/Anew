// Global variables
let scheduleData = null;
let currentDay = 'friday';
let currentSession = null;
let filteredSessions = [];
let useBeijingTime = true; // 默认使用北京时间

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadScheduleData();
    setupEventListeners();
    setupTimezoneToggle();
});

// Load schedule data from embedded data
async function loadScheduleData() {
    try {
        // Use embedded data instead of fetching
        scheduleData = scheduleDataEmbedded;

        // Hide loading and show content
        document.getElementById('loading').style.display = 'none';
        document.getElementById('scheduleContent').style.display = 'block';

        // Render the initial day
        renderDay(currentDay);

    } catch (error) {
        console.error('Error loading schedule data:', error);
        document.getElementById('loading').innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>加载议程数据时出错，请稍后重试。</p>
            </div>
        `;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Day tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const day = this.dataset.day;
            switchDay(day);
        });
    });
    
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        filterSessions(query);
    });
    
    // Modal close on background click
    document.getElementById('sessionModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

// Switch between days
function switchDay(day) {
    currentDay = day;
    
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-day="${day}"]`).classList.add('active');
    
    // Clear search
    document.getElementById('searchInput').value = '';
    
    // Render the day
    renderDay(day);
}

// Render a specific day
function renderDay(day) {
    if (!scheduleData || !scheduleData.days[day]) {
        return;
    }
    
    const dayData = scheduleData.days[day];
    const scheduleContent = document.getElementById('scheduleContent');
    
    // Create day header
    const dayHeader = `
        <div class="day-header">
            <h2>${dayData.day_name} - ${dayData.theme}</h2>
            <p>${dayData.date}</p>
        </div>
    `;
    
    // Create sessions grid
    const sessionsHtml = dayData.sessions.map((session, index) => 
        createSessionCard(session, day, index)
    ).join('');
    
    scheduleContent.innerHTML = `
        ${dayHeader}
        <div class="sessions-grid">
            ${sessionsHtml}
        </div>
    `;
    
    // Store current sessions for filtering
    filteredSessions = dayData.sessions;
    
    // Hide no results message
    document.getElementById('noResults').style.display = 'none';
}

// Create a session card HTML
function createSessionCard(session, day, index) {
    const speakers = session.speakers && session.speakers.length > 0 
        ? session.speakers.map(speaker => `<span class="speaker-tag">${speaker}</span>`).join('')
        : '<span class="speaker-tag">TBA</span>';
    
    return `
        <div class="session-card" onclick="openSessionModal('${day}', ${index})">
            <div class="session-header">
                <div class="session-time">
                    <i class="fas fa-clock"></i>
                    ${getDisplayTime(session)}
                </div>
                <div class="session-venue">${session.venue}</div>
            </div>
            <h3 class="session-title">${session.title}</h3>
            <p class="session-description">${truncateText(session.description, 150)}</p>
            <div class="session-speakers">
                ${speakers}
            </div>
            <div class="session-duration">
                <i class="fas fa-hourglass-half"></i>
                时长: ${session.duration}
            </div>
        </div>
    `;
}

// Filter sessions based on search query
function filterSessions(query) {
    if (!scheduleData || !scheduleData.days[currentDay]) {
        return;
    }
    
    const dayData = scheduleData.days[currentDay];
    
    if (!query) {
        // Show all sessions
        filteredSessions = dayData.sessions;
        renderFilteredSessions();
        return;
    }
    
    // Filter sessions
    filteredSessions = dayData.sessions.filter(session => {
        return session.title.toLowerCase().includes(query) ||
               session.description.toLowerCase().includes(query) ||
               session.venue.toLowerCase().includes(query) ||
               (session.speakers && session.speakers.some(speaker => 
                   speaker.toLowerCase().includes(query)
               ));
    });
    
    renderFilteredSessions();
}

// Render filtered sessions
function renderFilteredSessions() {
    const sessionsGrid = document.querySelector('.sessions-grid');
    const noResults = document.getElementById('noResults');
    
    if (filteredSessions.length === 0) {
        sessionsGrid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    sessionsGrid.style.display = 'block';
    noResults.style.display = 'none';
    
    const sessionsHtml = filteredSessions.map((session, index) => {
        // Find original index
        const originalIndex = scheduleData.days[currentDay].sessions.indexOf(session);
        return createSessionCard(session, currentDay, originalIndex);
    }).join('');
    
    sessionsGrid.innerHTML = sessionsHtml;
}

// Open session modal
function openSessionModal(day, sessionIndex) {
    if (!scheduleData || !scheduleData.days[day] || !scheduleData.days[day].sessions[sessionIndex]) {
        return;
    }
    
    const session = scheduleData.days[day].sessions[sessionIndex];
    currentSession = { day, sessionIndex, session };
    
    // Populate modal content
    document.getElementById('modalTitle').textContent = session.title;
    document.getElementById('modalTime').textContent = getDisplayTime(session);
    document.getElementById('modalVenue').textContent = session.venue;
    document.getElementById('modalDuration').textContent = session.duration;
    document.getElementById('modalDescription').textContent = session.description;
    
    // Populate speakers
    const speakersList = document.getElementById('speakersList');
    if (session.speakers && session.speakers.length > 0) {
        speakersList.innerHTML = session.speakers
            .map(speaker => `<span class="speaker-tag">${speaker}</span>`)
            .join('');
        document.getElementById('modalSpeakers').style.display = 'block';
    } else {
        document.getElementById('modalSpeakers').style.display = 'none';
    }
    
    // Show modal
    document.getElementById('sessionModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close session modal
function closeModal() {
    document.getElementById('sessionModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    currentSession = null;
}

// Export single session to ICS
function exportSessionToICS() {
    if (!currentSession) return;
    
    const { day, session } = currentSession;
    const dayData = scheduleData.days[day];
    
    const icsContent = generateICSContent([{
        ...session,
        date: dayData.date,
        dayName: dayData.day_name
    }], `OpenSauce 2025 - ${session.title}`);
    
    downloadICS(icsContent, `opensauce-${session.title.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase()}.ics`);
}

// Export all sessions to ICS
function exportAllToICS() {
    if (!scheduleData) return;
    
    const allSessions = [];
    
    Object.keys(scheduleData.days).forEach(dayKey => {
        const dayData = scheduleData.days[dayKey];
        dayData.sessions.forEach(session => {
            allSessions.push({
                ...session,
                date: dayData.date,
                dayName: dayData.day_name
            });
        });
    });
    
    const icsContent = generateICSContent(allSessions, 'OpenSauce 2025 - Complete Schedule');
    downloadICS(icsContent, 'opensauce-2025-complete-schedule.ics');
}

// Generate ICS content
function generateICSContent(sessions, calendarName) {
    const now = new Date();
    const timestamp = now.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    
    let icsContent = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//OpenSauce 2025//Schedule//EN',
        `X-WR-CALNAME:${calendarName}`,
        'X-WR-CALDESC:OpenSauce 2025 Conference Schedule',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH'
    ];
    
    sessions.forEach((session, index) => {
        // 使用北京时间或PDT时间
        const dateStr = useBeijingTime ? (session.date_beijing || session.date) : (session.date_pdt || session.date);
        const timeStr = useBeijingTime ? (session.time_beijing || session.time) : (session.time_pdt || session.time);
        const eventDate = parseSessionDateTime(dateStr, timeStr);
        const endDate = new Date(eventDate.getTime() + parseDuration(session.duration) * 60000);
        
        const uid = `opensauce-2025-${index}-${timestamp}@opensauce.com`;
        const dtstart = formatICSDateTime(eventDate);
        const dtend = formatICSDateTime(endDate);
        
        icsContent.push(
            'BEGIN:VEVENT',
            `UID:${uid}`,
            `DTSTAMP:${timestamp}`,
            `DTSTART:${dtstart}`,
            `DTEND:${dtend}`,
            `SUMMARY:${escapeICSText(session.title)}`,
            `DESCRIPTION:${escapeICSText(session.description)}`,
            `LOCATION:${escapeICSText(session.venue + ', San Francisco, CA')}`,
            session.speakers && session.speakers.length > 0 
                ? `ORGANIZER:CN=${escapeICSText(session.speakers.join(', '))}` 
                : '',
            'STATUS:CONFIRMED',
            'TRANSP:OPAQUE',
            'END:VEVENT'
        );
    });
    
    icsContent.push('END:VCALENDAR');
    
    return icsContent.filter(line => line !== '').join('\r\n');
}

// Parse session date and time
function parseSessionDateTime(dateStr, timeStr) {
    // Parse date like "July 18, 2025"
    const date = new Date(dateStr);
    
    // Parse time like "09:30 AM"
    const [time, period] = timeStr.split(' ');
    const [hours, minutes] = time.split(':').map(Number);
    
    let hour24 = hours;
    if (period === 'PM' && hours !== 12) {
        hour24 += 12;
    } else if (period === 'AM' && hours === 12) {
        hour24 = 0;
    }
    
    date.setHours(hour24, minutes, 0, 0);
    return date;
}

// Parse duration string to minutes
function parseDuration(durationStr) {
    const match = durationStr.match(/(\d+)\s*mins?/i);
    return match ? parseInt(match[1]) : 30; // Default to 30 minutes
}

// Format date for ICS
function formatICSDateTime(date) {
    return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
}

// Escape text for ICS format
function escapeICSText(text) {
    return text.replace(/\\/g, '\\\\')
               .replace(/;/g, '\\;')
               .replace(/,/g, '\\,')
               .replace(/\n/g, '\\n')
               .replace(/\r/g, '');
}

// Download ICS file
function downloadICS(content, filename) {
    const blob = new Blob([content], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

// Utility function to truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

// 时区相关函数
function setupTimezoneToggle() {
    // 在导航栏添加时区切换按钮
    const navActions = document.querySelector('.nav-actions');
    if (navActions) {
        const timezoneToggle = document.createElement('button');
        timezoneToggle.id = 'timezone-toggle';
        timezoneToggle.className = 'export-btn';
        timezoneToggle.innerHTML = '<i class="fas fa-clock"></i> 切换到PDT时间';
        timezoneToggle.addEventListener('click', toggleTimezone);

        // 插入到导出按钮后面
        const exportBtn = navActions.querySelector('.export-btn');
        navActions.insertBefore(timezoneToggle, exportBtn.nextSibling);
    }
}

function toggleTimezone() {
    useBeijingTime = !useBeijingTime;
    updateDisplayedTimes();

    // 更新按钮文本
    const toggleButton = document.getElementById('timezone-toggle');
    if (toggleButton) {
        toggleButton.innerHTML = useBeijingTime ?
            '<i class="fas fa-clock"></i> 切换到PDT时间' :
            '<i class="fas fa-clock"></i> 切换到北京时间';
    }

    // 重新渲染当前页面
    renderDay(currentDay);
}

function updateDisplayedTimes() {
    // 更新页面上显示的时间
    document.querySelectorAll('.session-time').forEach(timeElement => {
        const sessionCard = timeElement.closest('.session-card');
        if (sessionCard && sessionCard.sessionData) {
            const session = sessionCard.sessionData;
            if (useBeijingTime && session.time_beijing) {
                timeElement.textContent = session.time_beijing;
                // 添加跨天提示
                if (session.beijing_next_day) {
                    timeElement.title = `北京时间：${session.time_beijing} (次日)`;
                }
            } else {
                timeElement.textContent = session.time_pdt || session.time;
                timeElement.title = `PDT时间：${session.time}`;
            }
        }
    });
}

function getDisplayTime(session) {
    if (useBeijingTime && session.time_beijing) {
        return session.time_beijing + (session.beijing_next_day ? ' (次日)' : '');
    }
    return session.time;
}

function getDisplayDate(session) {
    if (useBeijingTime && session.date_beijing) {
        return session.date_beijing;
    }
    return session.date_pdt || session.date;
}
