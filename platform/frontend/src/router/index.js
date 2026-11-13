import { createRouter, createWebHistory } from 'vue-router'
import { ensureModules, isModuleEnabled } from '../composables/useModules'

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
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardRouter.vue'),
    meta: { requiresAuth: true }
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
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/Privacy.vue')
  },
  {
    path: '/rangebox',
    name: 'RangeBox',
    component: () => import('../views/RangeBoxView.vue'),
    meta: { requiresAuth: true }
  },
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

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guest && token && !to.meta.ssoCallback) {
    next('/dashboard')
  } else if (to.meta.requiresAdmin && !userHasRole('admin')) {
    next('/dashboard')
  } else if (to.meta.requiresInstructor && !userHasRole('instructor')) {
    next('/dashboard')
  } else if (to.meta.module) {
    // Module route guard: fail closed. A module route is only reachable when
    // the modules API affirmatively reports the module enabled. Answers come
    // from the shared useModules cache, so this fetches once per session
    // instead of once per navigation; a failed load redirects to the dashboard.
    try {
      const loaded = await ensureModules()
      if (!loaded || !isModuleEnabled(to.meta.module)) {
        return next('/dashboard')
      }
    } catch {
      return next('/dashboard')
    }
    next()
  } else {
    // Check if user must change password (except when already on change-password page)
    // Skip during impersonation — impersonated users don't change passwords
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const imp = sessionStorage.getItem('ocr_impersonating') === 'true'
    if (token && user.must_change_password && !imp && to.path !== '/change-password') {
      next('/change-password')
    } else {
      next()
    }
  }
})

export default router
