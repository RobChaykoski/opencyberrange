import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  setOption: vi.fn(),
  resize: vi.fn(),
  dispose: vi.fn(),
  observe: vi.fn(),
  disconnect: vi.fn(),
}))

vi.mock('echarts/core', () => ({
  use: vi.fn(),
  init: vi.fn(() => ({
    setOption: mocks.setOption,
    resize: mocks.resize,
    dispose: mocks.dispose,
  })),
}))
vi.mock('echarts/charts', () => ({ BarChart: {}, LineChart: {} }))
vi.mock('echarts/components', () => ({
  GridComponent: {},
  LegendComponent: {},
  MarkLineComponent: {},
  TooltipComponent: {},
}))
vi.mock('echarts/renderers', () => ({ CanvasRenderer: {} }))

import EChart from '../EChart.vue'

class ResizeObserverStub {
  observe() {
    mocks.observe()
  }

  disconnect() {
    mocks.disconnect()
  }
}

describe('EChart', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    globalThis.ResizeObserver = ResizeObserverStub
  })

  it('applies options, updates them, and disposes cleanly', async () => {
    const wrapper = mount(EChart, {
      props: { option: { series: [] }, ariaLabel: 'Test chart' },
    })

    expect(wrapper.get('[role="img"]').attributes('aria-label')).toBe('Test chart')
    expect(mocks.setOption).toHaveBeenCalledTimes(1)
    expect(mocks.observe).toHaveBeenCalled()

    await wrapper.setProps({ option: { series: [{ data: [1] }] } })
    expect(mocks.setOption).toHaveBeenCalledTimes(2)

    wrapper.unmount()
    expect(mocks.dispose).toHaveBeenCalled()
    expect(mocks.disconnect).toHaveBeenCalled()
  })

  it('uses the requested height', () => {
    const wrapper = mount(EChart, {
      props: { option: {}, height: '200px' },
    })
    expect(wrapper.get('.echart').attributes('style')).toContain('height: 200px')
  })
})
