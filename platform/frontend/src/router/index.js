import { createRouter, createWebHistory } from 'vue-router'

const ROLE_HIERARCHY = { student: 0, instructor: 1, admin: 2 }

function userHasRole(required) {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const userLevel = ROLE_HIERARCHY[user.role] ?? 0
    const requiredLevel = ROLE_HIERARCHY[required] ?? 0
    return userLevel >= requiredLevel
  } catch {
    return false
  }
}

function userHasGovernanceRole() {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return ['admin', 'institution_admin', 'privacy_officer', 'auditor'].includes(user.role)
  } catch {
    return false
  }
}

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('../views/Setup.vue'),
    meta: { guest: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/sso/callback',
    name: 'SsoCallback',
    component: () => import('../views/SsoCallback.vue'),
    meta: { guest: true, ssoCallback: true }
  },
  {
    // LTI launches run inside the LMS frame, so this alias is served with the
    // picker framing policy instead of the strict SPA policy.
    path: '/lti/callback',
    name: 'LtiCallback',
    component: () => import('../views/SsoCallback.vue'),
    meta: { guest: true, ssoCallback: true, bare: true }
  },
  {
    path: '/lti/deep-link',
    name: 'LtiDeepLink',
    component: () => import('../views/DeepLinkPicker.vue'),
    meta: { requiresAuth: true, bare: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guest: true }
  },
  {
    path: '/usage',
    name: 'Usage',
    component: () => import('../components/UsageDashboard.vue'),
    meta: { guest: true, allowAuthed: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue'),
    meta: { guest: true, allowAuthed: true }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('../views/ResetPassword.vue'),
    meta: { guest: true, allowAuthed: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardRouter.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/discover',
    name: 'Discover',
    component: () => import('../views/Discover.vue'),
    meta: { requiresAuth: true, bare: true }
  },
  {
    path: '/celebrations',
    name: 'Celebrations',
    component: () => import('../views/Celebrations.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/events',
    name: 'Events',
    component: () => import('../views/Competitions.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/events/:id',
    name: 'EventDetail',
    component: () => import('../views/CompetitionDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    // Compatibility aliases for older bookmarks. The API and internal model
    // names remain competition-based so existing data keeps working.
    path: '/competitions',
    redirect: '/events'
  },
  {
    path: '/competitions/:id',
    redirect: (to) => `/events/${to.params.id}`
  },
  {
    path: '/vpn-setup',
    name: 'VPNSetup',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/exercises',
    name: 'Exercises',
    component: () => import('../views/Curriculum.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/workbooks',
    name: 'Workbooks',
    component: () => import('../views/WorkbooksLanding.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/workbook-answers',
    name: 'WorkbookAnswers',
    component: () => import('../views/WorkbookAnswers.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/my-evidence',
    name: 'MyEvidence',
    component: () => import('../views/MyEvidence.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/journey',
    name: 'Journey',
    component: () => import('../views/Journey.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/impact',
    name: 'Impact',
    component: () => import('../views/Impact.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/practice',
    name: 'Practice',
    component: () => import('../views/Practice.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/threat-awareness',
    name: 'ThreatAwareness',
    alias: '/threat-map',
    component: () => import('../views/ThreatAwareness.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tools',
    name: 'Tools',
    component: () => import('../views/Tools.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/certificate/event/:eventId/:award',
    name: 'EventCertificate',
    component: () => import('../views/Certificate.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/certificate/:trackSlug/:levelId',
    name: 'Certificate',
    component: () => import('../views/Certificate.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/verify',
    name: 'VerifyCertificate',
    component: () => import('../views/VerifyCertificate.vue')
  },
  {
    path: '/verify/certificate/:certificateId',
    name: 'VerifyCertificateResult',
    component: () => import('../views/VerifyCertificate.vue')
  },
  {
    path: '/exercises/:trackSlug',
    name: 'TrackDetail',
    component: () => import('../views/TrackDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/exercises/:trackSlug/labs/:labSlug/quiz',
    name: 'ExerciseQuiz',
    component: () => import('../views/ExerciseQuiz.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/labs',
    name: 'Labs',
    redirect: '/exercises'  // Redirect old labs route to exercises
  },
  {
    path: '/curriculum',
    name: 'Curriculum',
    redirect: '/exercises'  // Redirect old curriculum route to exercises
  },
  {
    path: '/courses',
    name: 'Courses',
    component: () => import('../views/CourseList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/courses/:id',
    name: 'CourseDetail',
    component: () => import('../views/Course.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/instructor',
    name: 'Instructor',
    component: () => import('../views/InstructorPanel.vue'),
    meta: { requiresAuth: true, requiresInstructor: true }
  },
  {
    path: '/evidence-review',
    name: 'EvidenceReview',
    component: () => import('../views/EvidenceReview.vue'),
    meta: { requiresAuth: true, requiresInstructor: true }
  },
  {
    path: '/contract-review',
    name: 'ContractReview',
    component: () => import('../views/ContractReview.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue'),
    meta: { requiresAuth: true, requiresInstructor: true }
  },
  {
    path: '/surveys',
    name: 'Surveys',
    component: () => import('../views/Surveys.vue'),
    meta: { requiresAuth: true, requiresInstructor: true }
  },
  
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/usage',
    name: 'AdminUsage',
    component: () => import('../components/UsageDashboard.vue'),
    props: { admin: true },
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/governance',
    name: 'Governance',
    component: () => import('../views/Governance.vue'),
    meta: { requiresAuth: true, requiresGovernance: true }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('../views/ChangePassword.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/PublicAbout.vue')
  },
  {
    path: '/about/installation',
    name: 'InstallationAbout',
    component: () => import('../views/About.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/badges/:jti',
    name: 'BadgeViewer',
    component: () => import('../views/BadgeViewer.vue'),
    meta: { public: true }
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/Privacy.vue')
  },
  {
    path: '/privacy/youth',
    name: 'YouthPrivacy',
    component: () => import('../views/YouthPrivacy.vue')
  },
  {
    path: '/rangebox',
    name: 'RangeBox',
    component: () => import('../views/RangeBoxView.vue'),
    meta: { requiresAuth: true }
  },
  // Legacy competition URL and unknown paths. Unknown paths go through the
  // dashboard guard, so an unauthenticated visitor lands on the login page
  // instead of a blank screen.
  { path: '/challenges', redirect: '/events' },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard with setup check
let setupChecked = false
let setupComplete = true

router.beforeEach(async (to, from, next) => {
  // Check setup status once per session
  if (!setupChecked && to.path !== '/setup') {
    try {
      const res = await fetch('/api/setup/status')
      const data = await res.json()
      setupComplete = data.setup_complete
      setupChecked = true
    } catch {
      setupChecked = true
    }
  }

  // Redirect to setup if not complete
  if (!setupComplete && to.path !== '/setup') {
    return next('/setup')
  }

  const token = localStorage.getItem('token')
  const impersonating = sessionStorage.getItem('ocr_impersonating') === 'true'

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guest && token && !to.meta.ssoCallback && !to.meta.allowAuthed) {
    next('/dashboard')
  } else if (
    to.path === '/dashboard'
    && token
    && !impersonating
    && userHasRole('admin')
  ) {
    // Administrators work from the Admin sections; the learner/instructor
    // dashboard is not part of their interface.
    next('/admin')
  } else if (to.meta.requiresAdmin && !userHasRole('admin')) {
    next('/dashboard')
  } else if (to.meta.requiresGovernance && !userHasGovernanceRole()) {
    next('/dashboard')
  } else if (to.meta.requiresInstructor && !userHasRole('instructor')) {
    next('/dashboard')
  } else {
    // Check if user must change password (except when already on change-password page)
    // Skip during impersonation — impersonated users don't change passwords
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const imp = sessionStorage.getItem('ocr_impersonating') === 'true'
    if (
      token
      && user.must_change_password
      && !imp
      && to.path !== '/change-password'
      && !to.meta.allowAuthed
    ) {
      next('/change-password')
    } else {
      next()
    }
  }
})

export default router
