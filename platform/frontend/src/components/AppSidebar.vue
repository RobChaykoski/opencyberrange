<template>
  <aside
    id="primary-sidebar"
    class="sidebar"
    :class="{
      'sidebar--collapsed': collapsed && !isMobile,
      'sidebar--mobile-open': mobileOpen,
    }"
    :inert="isMobile && !mobileOpen"
    :aria-hidden="isMobile && !mobileOpen ? 'true' : undefined"
    :role="isMobile && mobileOpen ? 'dialog' : undefined"
    :aria-modal="isMobile && mobileOpen ? 'true' : undefined"
    :aria-label="isMobile && mobileOpen ? 'Navigation' : undefined"
  >
    <!-- Brand -->
    <div class="sidebar__brand">
      <button
      v-if="!isMobile"
      @click="$emit('toggle')"
      class="collapse-btn"
      :title="collapsed ? 'Expand' : 'Collapse'"
      :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      :aria-expanded="!collapsed"
    >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline v-if="collapsed" points="9 18 15 12 9 6"/>
          <polyline v-else points="15 18 9 12 15 6"/>
        </svg>
      </button>
      <button
        v-if="isMobile"
        type="button"
        class="mobile-close-btn"
        aria-label="Close navigation"
        @click="$emit('close')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
      <router-link to="/dashboard" class="brand-link">
        <img :src="brandIcon" alt="" class="brand-icon" />
        <span v-show="!collapsed" class="brand-text">
          <span class="brand-text__name">SWOCTS</span>
          <span class="brand-text__sub">Cyber Range</span>
        </span>
      </router-link>
    </div>

    <!-- Navigation Sections -->
    <nav class="sidebar__nav">
      <!-- Student-facing workspace. Administrators work from the Admin
           sections instead of a second copy of the learner menu. Instructors
           keep this menu so they can see and use what students see. -->
      <template v-if="showUserNav">
      <!-- WORKSPACE -->
      <div class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Workspace</span>
        <router-link to="/dashboard" aria-label="Dashboard" title="Dashboard: your current objective and range status" data-tour="nav-dashboard" class="nav-item" :class="{ 'nav-item--active': isActive('/dashboard') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <rect x="3" y="3" width="7" height="7"/>
            <rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Dashboard</span>
        </router-link>
        <router-link to="/rangebox" aria-label="RangeBox" title="RangeBox: open a browser desktop for your labs" data-tour="nav-rangebox" class="nav-item" :class="{ 'nav-item--active': isActive('/rangebox') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">RangeBox</span>
        </router-link>
      </div>

      <!-- INSTRUCTOR (instructor only; administrators use the Admin sections) -->
      <div v-if="showInstructorTools" class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Teaching</span>
        <router-link to="/instructor?tab=courses" aria-label="Course workspace" title="Course workspace: rosters, assignments, and course health" class="nav-item" :class="{ 'nav-item--active': isInstructorTab('courses') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Course workspace</span>
        </router-link>
        <router-link to="/instructor?tab=labs" aria-label="Exercise authoring" title="Exercise authoring: create and review exercises" class="nav-item" :class="{ 'nav-item--active': isInstructorTab('labs') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Exercise authoring</span>
        </router-link>
        <router-link to="/evidence-review" aria-label="Evidence review" title="Evidence review: decide pending learner evidence" class="nav-item" :class="{ 'nav-item--active': isActive('/evidence-review') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <path d="m9 14 2 2 4-4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Evidence review</span>
        </router-link>
        <router-link to="/contract-review" aria-label="Contract review" title="Contract review: competency contract drafts and sign-off" class="nav-item" :class="{ 'nav-item--active': isActive('/contract-review') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <path d="m9 14 2 2 4-4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Contract review</span>
        </router-link>
        <router-link to="/capstone-builder" aria-label="Capstone Builder" title="Capstone Builder: turn a role profile into an approved capstone plan" class="nav-item" :class="{ 'nav-item--active': isActive('/capstone-builder') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M12 3 2 8l10 5 10-5-10-5z"/>
            <path d="M4 10v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Capstone Builder</span>
        </router-link>
        <router-link v-if="!showAdmin" to="/reports" aria-label="Reports and analytics" title="Reports &amp; analytics: programme trends and exports" class="nav-item" :class="{ 'nav-item--active': isActive('/reports') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M3 3v18h18"/>
            <path d="M7 15l4-4 3 3 5-6"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Reports &amp; analytics</span>
        </router-link>
        <router-link to="/surveys" aria-label="Surveys" title="Surveys: learner feedback and pulse checks" class="nav-item" :class="{ 'nav-item--active': isActive('/surveys') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <path d="M9 12h6M9 16h4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Surveys</span>
        </router-link>
      </div>

      <!-- LEARN -->
      <div class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Learn</span>
        <router-link to="/courses" aria-label="Courses" title="Courses: work assigned by an instructor" class="nav-item" :class="{ 'nav-item--active': isActive('/courses') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Courses</span>
        </router-link>
        <router-link to="/exercises" aria-label="Exercises" title="Exercises: browse labs by track" data-tour="nav-exercises" class="nav-item" :class="{ 'nav-item--active': isActive('/exercises') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20V22H6.5A2.5 2.5 0 0 1 4 19.5V4.5A2.5 2.5 0 0 1 6.5 2Z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Exercises</span>
        </router-link>
        <router-link to="/workbooks" aria-label="Workbooks" title="Workbooks: step-by-step guides for each track" class="nav-item" :class="{ 'nav-item--active': isActive('/workbooks') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Workbooks</span>
        </router-link>
        <router-link to="/workbook-answers" aria-label="Analyst answers" title="Analyst answers: write an answer and send it for instructor review" class="nav-item" :class="{ 'nav-item--active': isActive('/workbook-answers') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M12 20h9"/>
            <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Analyst answers</span>
        </router-link>
        <router-link to="/practice" aria-label="Practice exams" title="Practice exams: certification-style questions, not a scoreboard" class="nav-item" :class="{ 'nav-item--active': isActive('/practice') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <circle cx="12" cy="12" r="9"/>
            <circle cx="12" cy="12" r="5"/>
            <circle cx="12" cy="12" r="1.5"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Practice exams</span>
        </router-link>
      </div>

      </template>

      <!-- TOOLS (every role; the same allow-listed tools in one place) -->
      <div class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Tools</span>
        <router-link to="/toolbox" aria-label="All tools" title="All tools: the full tool catalogue and how each one runs" class="nav-item" :class="{ 'nav-item--active': isActive('/toolbox') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">All tools</span>
        </router-link>
        <button
          type="button"
          aria-label="CyberChef (opens in a panel)"
          title="CyberChef — decode and inspect data"
          class="nav-item nav-item--button"
          @click="toggleTool('cyberchef')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M4 7h16"/>
            <path d="M4 12h10"/>
            <path d="M4 17h7"/>
            <circle cx="18" cy="12" r="2"/>
            <path d="m18 14v3"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">CyberChef</span>
        </button>
        <button
          type="button"
          aria-label="OT scan assistant (opens in a panel)"
          title="OT scan assistant - safe nmap for Modbus, S7, EtherNet/IP, DNP3"
          class="nav-item nav-item--button"
          @click="toggleTool('otscan')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <circle cx="12" cy="12" r="9"/>
            <circle cx="12" cy="12" r="4"/>
            <line x1="12" y1="3" x2="12" y2="7"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
            <line x1="3" y1="12" x2="7" y2="12"/>
            <line x1="17" y1="12" x2="21" y2="12"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">OT scan</span>
        </button>
        <button
          type="button"
          aria-label="MITRE ATT&CK Navigator (opens in a panel)"
          title="MITRE ATT&CK Navigator — technique coverage and layers"
          class="nav-item nav-item--button"
          @click="toggleTool('attacknavigator')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">ATT&amp;CK</span>
        </button>
        <button
          type="button"
          aria-label="OWASP ZAP scan planner (opens in a panel)"
          title="OWASP ZAP scan planner - build an authorised baseline or full scan"
          class="nav-item nav-item--button"
          @click="toggleTool('zap')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M13 2 4 14h7l-1 8 9-12h-7z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">ZAP scan</span>
        </button>
      </div>

      <template v-if="showUserNav">
      <!-- PROGRESS -->
      <div class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Your progress</span>
        <router-link to="/journey" aria-label="Journey and mission" title="Journey and mission: choose the direction you are working toward" class="nav-item" :class="{ 'nav-item--active': isActive('/journey') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <circle cx="6" cy="19" r="2"/>
            <circle cx="18" cy="5" r="2"/>
            <path d="M8 19h3a4 4 0 0 0 4-4V9a4 4 0 0 1 4-4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Journey &amp; mission</span>
        </router-link>
        <router-link to="/impact" aria-label="Impact and recognition" title="Impact and recognition: what your verified work reached" class="nav-item" :class="{ 'nav-item--active': isActive('/impact') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Impact &amp; recognition</span>
        </router-link>
        <router-link to="/profile?tab=skill-tree" aria-label="Cyber DNA skills profile" title="Cyber DNA: your evidence-backed skills profile" class="nav-item" :class="{ 'nav-item--active': isActive('/profile') && route.query.tab === 'skill-tree' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M7 3c0 6 10 6 10 12M17 3c0 6-10 6-10 12M7 21c0-1 10-1 10-6M17 21c0-1-10-1-10-6"/>
            <path d="M8.5 6h7M8.5 18h7M9.5 9h5M9.5 15h5"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Cyber DNA</span>
        </router-link>
        <router-link to="/profile?tab=careers" aria-label="Career paths" title="Career GPS: explore target roles and the path to them" class="nav-item" :class="{ 'nav-item--active': isActive('/profile') && route.query.tab === 'careers' }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M12 21s-6-5.33-6-11a6 6 0 1 1 12 0c0 5.67-6 11-6 11z"/>
            <circle cx="12" cy="10" r="2"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Career GPS</span>
        </router-link>
        <router-link to="/my-evidence" aria-label="Evidence portfolio" title="Evidence portfolio: verified work and instructor decisions" class="nav-item" :class="{ 'nav-item--active': isActive('/my-evidence') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <path d="m9 14 2 2 4-4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Evidence portfolio</span>
        </router-link>
      </div>

      <!-- EXPLORE -->
      <div class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Explore</span>
        <router-link to="/threat-awareness" aria-label="Threat map" title="Threat map: explore aggregated hostile infrastructure by country" class="nav-item" :class="{ 'nav-item--active': isActive('/threat-awareness') || isActive('/threat-map') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <circle cx="12" cy="12" r="9"/>
            <path d="M3 12h18"/>
            <path d="M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Threat map</span>
        </router-link>
        <router-link to="/events" aria-label="Events and competitions" title="Events and competitions" class="nav-item" :class="{ 'nav-item--active': isActive('/events') || isActive('/competitions') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M8 21h8"/>
            <path d="M12 17v4"/>
            <path d="M7 4h10v5a5 5 0 0 1-10 0V4z"/>
            <path d="M7 6H4a1 1 0 0 0-1 1v1a3 3 0 0 0 3 3h1"/>
            <path d="M17 6h3a1 1 0 0 1 1 1v1a3 3 0 0 1-3 3h-1"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Events</span>
        </router-link>
        <router-link to="/celebrations" aria-label="Celebration wall" title="Celebration wall: recent badges and wins from across the range" class="nav-item" :class="{ 'nav-item--active': isActive('/celebrations') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="m12 3 2.5 5.6 6.1.6-4.6 4 1.4 6-5.4-3.2-5.4 3.2 1.4-6-4.6-4 6.1-.6z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Celebration wall</span>
        </router-link>
      </div>

      </template>

      <!-- GOVERNANCE (privacy, audit, institution admin) -->
      <div v-if="showGovernance" class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Governance</span>
        <router-link to="/governance" aria-label="Privacy and audit evidence" title="Privacy and audit evidence" class="nav-item" :class="{ 'nav-item--active': isActive('/governance') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="M9 12l2 2 4-4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Privacy &amp; audit</span>
        </router-link>
        <router-link to="/contract-review" aria-label="Contract review" title="Contract review: competency contract drafts and sign-off" class="nav-item" :class="{ 'nav-item--active': isActive('/contract-review') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <path d="m9 14 2 2 4-4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Contract review</span>
        </router-link>
      </div>

      <!-- ADMIN (admin only) -->
      <div v-if="showAdmin" class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Administration</span>
        <router-link to="/admin?tab=users" aria-label="Users" title="Users: accounts, roles, and approvals" class="nav-item" :class="{ 'nav-item--active': isAdminTab('users') || isAdminTab('pending') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon">
            <path d="M17 21V19C17 17.9 16.1 17 15 17H9C7.9 17 7 17.9 7 19V21"/>
            <circle cx="12" cy="11" r="4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Users</span>
        </router-link>
        <router-link to="/admin?tab=courses" aria-label="Course catalogue" title="Course catalogue: all courses on the platform" class="nav-item" :class="{ 'nav-item--active': isAdminTab('courses') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Course catalogue</span>
        </router-link>
        <router-link to="/admin?tab=exercises" aria-label="Exercise library" title="Exercise library: all labs and tracks" class="nav-item" :class="{ 'nav-item--active': isAdminTab('exercises') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Exercise library</span>
        </router-link>
        <router-link to="/evidence-review" aria-label="Evidence review" title="Evidence review: decide pending learner evidence" class="nav-item" :class="{ 'nav-item--active': isActive('/evidence-review') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <path d="m9 14 2 2 4-4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Evidence review</span>
        </router-link>
      </div>

      <div v-if="showAdmin" class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Operations</span>
        <router-link to="/admin?tab=monitoring" aria-label="Sessions and activity" title="Sessions and activity: running labs, VPN sessions, and recent events" class="nav-item" :class="{ 'nav-item--active': isAdminTab('monitoring') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Sessions &amp; activity</span>
        </router-link>
        <router-link to="/reports" aria-label="Reports and analytics" title="Reports &amp; analytics: programme trends and exports" class="nav-item" :class="{ 'nav-item--active': isActive('/reports') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M3 3v18h18"/>
            <path d="M7 15l4-4 3 3 5-6"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Reports &amp; analytics</span>
        </router-link>
        <router-link to="/surveys" aria-label="Surveys" title="Surveys: learner feedback and pulse checks" class="nav-item" :class="{ 'nav-item--active': isActive('/surveys') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <path d="M9 12h6M9 16h4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Surveys</span>
        </router-link>
        <router-link to="/admin?tab=system" aria-label="System health" title="System health: services, backups, integrity, and metrics" class="nav-item" :class="{ 'nav-item--active': isAdminTab('system') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <rect x="2" y="3" width="20" height="14" rx="2"/>
            <path d="M8 21h8M12 17v4"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">System health</span>
        </router-link>
        <router-link to="/admin?tab=settings" aria-label="Platform settings" title="Platform settings: identity, modules, lab defaults, and data labels" class="nav-item" :class="{ 'nav-item--active': isAdminTab('settings') }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">Platform settings</span>
        </router-link>
      </div>

      <div class="nav-section">
        <span v-show="!collapsed" class="nav-section__label">Resources</span>
        <a :href="manualUrl" aria-label="User manual" title="User manual: how to use the range" target="_blank" rel="noopener" class="nav-item" @click="setWikiAuthCookie">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="nav-item__icon" aria-hidden="true">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          <span v-show="!collapsed" class="nav-item__label">User manual</span>
        </a>
      </div>

    </nav>

    <!-- User Section -->
    <div class="sidebar__footer">
      <div v-if="showPrivileged" class="privacy-row" :class="{ 'privacy-row--collapsed': collapsed }">
        <button @click="togglePrivacy" class="privacy-btn" :title="privacyMode ? 'Show names (Privacy OFF)' : 'Mask names (Privacy ON)'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="privacy-btn__icon">
            <template v-if="privacyMode">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
              <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
              <line x1="1" y1="1" x2="23" y2="23"/>
            </template>
            <template v-else>
              <path d="M1 12S5 4 12 4S23 12 23 12S19 20 12 20S1 12 1 12Z"/>
              <circle cx="12" cy="12" r="3"/>
            </template>
          </svg>
          <span v-show="!collapsed" class="privacy-btn__label">Privacy Mode</span>
          <span v-show="!collapsed" class="privacy-btn__track" :class="{ 'privacy-btn__track--on': privacyMode }">
            <span class="privacy-btn__thumb"></span>
          </span>
        </button>
      </div>
      <button v-if="!showAdmin" v-show="!collapsed && startTour" @click="replayTour" class="tour-btn" title="Replay the orientation tour">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="tour-btn__icon">
          <circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <span class="tour-btn__label">Take the tour</span>
      </button>
      <router-link to="/profile" aria-label="Profile" title="Profile" class="nav-item nav-item--user" :class="{ 'nav-item--active': isActive('/profile') }">
        <div class="user-avatar">{{ userInitial }}</div>
        <span v-show="!collapsed" class="nav-item__label nav-item__identity">
          <span class="nav-item__name">{{ formattedUsername }}</span>
          <span class="nav-item__role">{{ roleLabel }}</span>
        </span>
      </router-link>
      <button v-show="!collapsed" @click="$emit('logout')" class="logout-btn">Logout</button>
      <div v-show="!collapsed" class="powered-footer">
        <span>Powered by</span>
        <a
          href="https://github.com/RobChaykoski/opencyberrange"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="OpenCyberRange on GitHub"
        >
          <img :src="poweredLogo" alt="" class="powered-footer__logo" />
          <span>OpenCyberRange</span>
        </a>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useRoute } from 'vue-router'
import { usePrivacy } from '../composables/usePrivacy'
import { useToolPanel } from '../composables/useToolPanel'
import { setWikiAuthCookie } from '../utils/wikiAuth'
import { wikiUrl } from '../utils/wikiUrl'

const props = defineProps({
  collapsed: Boolean,
  mobileOpen: Boolean,
  isMobile: Boolean,
  userRole: {
    type: String,
    default: 'student'
  },
  username: String,
})

defineEmits(['toggle', 'logout', 'close'])

const route = useRoute()
const { privacyMode, togglePrivacy } = usePrivacy()
const { toggleTool } = useToolPanel()
const brandIcon = '/swocts-cyber-range-mark.png'
const poweredLogo = '/ocr-logo-dark.png'
const manualUrl = computed(() => wikiUrl('/wiki/reference/manual/'))
const startTour = inject('startTour', null)
const replayTour = () => { if (startTour) startTour() }

const showUserNav = computed(() => props.userRole !== 'admin')
const showInstructorTools = computed(() => props.userRole === 'instructor')
const showAdmin = computed(() => props.userRole === 'admin')
const showGovernance = computed(() => (
  ['admin', 'institution_admin', 'privacy_officer', 'auditor'].includes(props.userRole)
))
const showPrivileged = computed(() => ['instructor', 'admin'].includes(props.userRole))
const roleLabel = computed(() => ({
  admin: 'Administrator',
  institution_admin: 'Institution admin',
  privacy_officer: 'Privacy officer',
  auditor: 'Auditor',
  mentor: 'Mentor',
  teaching_assistant: 'Teaching assistant',
  instructor: 'Instructor',
  student: 'Student',
}[props.userRole] || 'User'))

const isActive = (path) => {
  if (path === '/dashboard') return route.path === '/dashboard'
  if (path === '/admin') return route.path === '/admin'
  if (path === '/instructor') return route.path === '/instructor'
  if (path === '/exercises') return route.path.startsWith('/exercises')
  return route.path.startsWith(path)
}

const isAdminTab = (tab) => {
  if (route.path !== '/admin') return false
  const currentTab = route.query.tab || 'users'
  if (tab === 'monitoring') return ['monitoring', 'sessions', 'vpn', 'activity'].includes(currentTab)
  if (tab === 'exercises') return ['exercises', 'labs', 'curriculum'].includes(currentTab)
  if (tab === 'system') return ['system', 'tester'].includes(currentTab)
  return currentTab === tab
}

const isInstructorTab = (tab) => {
  if (route.path !== '/instructor') return false
  const currentTab = route.query.tab || 'courses'
  return currentTab === tab
}

const formattedUsername = computed(() => {
  if (!props.username) return 'User'
  return props.username.charAt(0).toUpperCase() + props.username.slice(1).toLowerCase()
})

const userInitial = computed(() => {
  return (props.username || 'U').charAt(0).toUpperCase()
})
</script>

<style scoped>
.sidebar {
  width: 250px;
  min-width: 250px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  transition: width 0.2s ease, min-width 0.2s ease;
  z-index: 50;
  overflow: hidden;
}

.sidebar--collapsed {
  width: 64px;
  min-width: 64px;
}

/* Brand */
.sidebar__brand {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.25rem 1rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.brand-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--text-primary);
}

.brand-icon {
  width: 84px;
  height: 84px;
  flex-shrink: 0;
  border-radius: 4px;
  object-fit: contain;
}

.brand-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.1rem;
  line-height: 1.05;
  white-space: nowrap;
  color: var(--text-primary);
}

.brand-text__name {
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: 0.13em;
}

.brand-text__sub {
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.collapse-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.collapse-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.collapse-btn svg {
  width: 18px;
  height: 18px;
}

.mobile-close-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
}

.mobile-close-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.mobile-close-btn svg {
  width: 20px;
  height: 20px;
}

.sidebar--collapsed .sidebar__brand {
  padding: 0.75rem 0.5rem;
}

.sidebar--collapsed .brand-link {
  display: none;
}

/* Navigation */
.sidebar__nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
}

.nav-section {
  margin-bottom: 0.25rem;
  padding-top: 0.5rem;
}

.nav-section + .nav-section {
  border-top: 1px solid var(--border-color);
  margin-top: 0.25rem;
}

.nav-section__label {
  display: block;
  font-size: 0.625rem;
  font-weight: 700;
  color: var(--nav-label);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0.5rem 1.25rem 0.375rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1.25rem;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.8125rem;
  font-weight: 500;
  border-radius: 0;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
  white-space: nowrap;
}

.sidebar--collapsed .nav-item {
  justify-content: center;
  padding: 0.625rem;
  border-left: none;
}

.nav-item:hover {
  color: var(--hover-text);
  background: var(--hover-bg);
}

.nav-item--button {
  width: 100%;
  background: transparent;
  font: inherit;
  text-align: left;
  cursor: pointer;
  border-top: 0;
  border-right: 0;
  border-bottom: 0;
}

.nav-item--button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.nav-item--active {
  color: var(--accent-text);
  background: var(--accent-bg);
  border-left-color: var(--accent);
}

.sidebar--collapsed .nav-item--active {
  border-left-color: transparent;
}

.nav-item__icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-item__label {
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item__identity {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
  min-width: 0;
}

.nav-item__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-item__role {
  margin-top: 0.1rem;
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
}

/* Footer */
.sidebar__footer {
  border-top: 1px solid var(--border-color);
  padding: 0.75rem;
}

/* Privacy toggle */
.privacy-row {
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.privacy-row--collapsed {
  padding-bottom: 0.5rem;
}

.privacy-btn {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.15s;
}

.privacy-row--collapsed .privacy-btn {
  justify-content: center;
  padding: 0.4rem;
}

.privacy-btn:hover {
  color: var(--text-primary);
  background: var(--hover-bg);
}

.privacy-btn__icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.privacy-btn__label {
  flex: 1;
  text-align: left;
  white-space: nowrap;
}

.privacy-btn__track {
  width: 30px;
  height: 16px;
  background: var(--border-color);
  border-radius: 8px;
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}

.privacy-btn__track--on {
  background: var(--accent);
}

.privacy-btn__thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
}

.privacy-btn__track--on .privacy-btn__thumb {
  transform: translateX(14px);
}

.nav-item--user {
  margin-bottom: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-left: none;
  border-radius: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.tour-btn {
  display: flex; align-items: center; gap: 0.6rem; width: 100%;
  padding: 0.5rem 0.75rem; margin-bottom: 0.25rem;
  background: none; border: none; cursor: pointer;
  color: var(--text-secondary); font-size: 0.82rem; border-radius: 8px;
}
.tour-btn:hover { background: var(--sidebar-hover, rgba(255,255,255,0.06)); color: var(--sidebar-fg, #e2e8f0); }
.tour-btn__icon { width: 18px; height: 18px; flex-shrink: 0; }

.logout-btn {
  width: 100%;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: var(--danger-bg);
  border-color: var(--danger);
  color: var(--danger);
}

/* Shorter laptop windows: tighten the brand and nav rhythm so Teaching and
   Operations links are not pushed below the fold. */
@media (max-height: 900px) and (min-width: 769px) {
  .sidebar__brand {
    padding: 0.75rem 1rem 0.6rem;
  }
  .brand-icon {
    width: 64px;
    height: 64px;
  }
  .nav-section {
    padding-top: 0.35rem;
  }
  .nav-item {
    padding-top: 0.38rem;
    padding-bottom: 0.38rem;
  }
  .nav-section__label {
    padding-top: 0.35rem;
    padding-bottom: 0.25rem;
  }
}

/* Responsive - off-canvas drawer on phones */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: min(86vw, 320px);
    min-width: min(86vw, 320px);
    height: 100vh;
  height: 100dvh;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    z-index: 300;
    box-shadow: 18px 0 40px rgba(2, 6, 23, 0.35);
  }

  .sidebar--mobile-open {
    transform: translateX(0);
  }

  .sidebar--collapsed {
    width: min(86vw, 320px);
    min-width: min(86vw, 320px);
  }

  .sidebar__brand {
    padding-top: 1rem;
  }

  .sidebar__nav {
    padding-bottom: 1rem;
  }

  .sidebar .nav-item {
    min-height: 44px;
    padding-top: 0.6rem;
    padding-bottom: 0.6rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sidebar {
    transition: none;
  }
}
.powered-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  font-size: 0.7rem;
  color: var(--text-muted);
  padding: 0.5rem 0.25rem;
  border-top: 1px solid var(--border-color);
  margin-top: 0.5rem;
}
.powered-footer a {
  color: var(--accent-text);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-weight: 600;
}
.powered-footer a:hover {
  opacity: 0.8;
}
.powered-footer__logo {
  height: 16px;
  width: auto;
  display: block;
  border-radius: 3px;
}

</style>
