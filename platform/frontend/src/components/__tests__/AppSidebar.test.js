import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { describe, expect, it } from 'vitest'

import AppSidebar from '../AppSidebar.vue'

async function mountSidebar(userRole) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
  })
  await router.push('/dashboard')
  await router.isReady()
  return mount(AppSidebar, {
    props: {
      collapsed: false,
      mobileOpen: false,
      isMobile: false,
      userRole,
      username: 'student',
    },
    global: { plugins: [router] },
  })
}

function labels(wrapper) {
  return wrapper.findAll('.nav-item__label').map((label) => label.text())
}

describe('AppSidebar navigation', () => {
  it('groups student work under Learn, Progress, Explore, and Tools', async () => {
    const wrapper = await mountSidebar('student')
    const text = labels(wrapper)
    expect(text).toEqual(expect.arrayContaining([
      'Dashboard',
      'RangeBox',
      'Courses',
      'Exercises',
      'Workbooks',
      'Analyst answers',
      'Practice exams',
      'Journey & mission',
      'Impact & recognition',
      'Cyber DNA',
      'Career GPS',
      'Evidence portfolio',
      'Threat map',
      'Events',
      'Celebration wall',
      'All tools',
      'CyberChef',
      'OT scan',
      'ATT&CK',
      'ZAP scan',
    ]))
    expect(text).not.toContain('Workbook answers')
    expect(text).not.toContain('Your journey')
    expect(text).not.toContain('Your impact')
    expect(wrapper.text()).toContain('Learn')
    expect(wrapper.text()).toContain('Your progress')
    expect(wrapper.text()).toContain('Explore')
  })

  it('links the Tools heading to the shared tool catalogue', async () => {
    const wrapper = await mountSidebar('student')
    const allTools = wrapper.findAll('a').find((link) => link.text().includes('All tools'))
    expect(allTools).toBeTruthy()
    expect(allTools.attributes('href')).toBe('/tools')
    const zap = wrapper.findAll('button').find((button) => button.text().includes('ZAP scan'))
    expect(zap).toBeTruthy()
  })

  it('keeps the instructor workspace separate from the learner library', async () => {
    const wrapper = await mountSidebar('instructor')
    const text = labels(wrapper)
    expect(text).toEqual(expect.arrayContaining([
      'Course workspace',
      'Exercise authoring',
      'Evidence review',
      'Contract review',
      'Reports & analytics',
      'Surveys',
    ]))
    expect(text).not.toContain('My Courses')
    expect(text).not.toContain('My Exercises')
  })

  it('uses plain-language admin labels and still offers the tools', async () => {
    const wrapper = await mountSidebar('admin')
    const text = labels(wrapper)
    expect(text).toEqual(expect.arrayContaining([
      'Course catalogue',
      'Exercise library',
      'Sessions & activity',
      'System health',
      'Platform settings',
      'All tools',
    ]))
    expect(text).not.toContain('All courses')
    expect(text).not.toContain('All exercises')
    expect(text).not.toContain('System')
    expect(text).not.toContain('Settings')
  })
})
