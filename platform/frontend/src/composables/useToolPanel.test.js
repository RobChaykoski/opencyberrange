import { describe, expect, it } from 'vitest'

import { useToolPanel } from './useToolPanel'

describe('useToolPanel', () => {
  it('publishes every allow-listed tool, including the ZAP planner', () => {
    const { toolList } = useToolPanel()
    const keys = toolList.value.map((tool) => tool.key)
    expect(keys).toEqual(['cyberchef', 'otscan', 'attacknavigator', 'zap'])
    for (const tool of toolList.value) {
      expect(tool.title).toBeTruthy()
      expect(tool.description).toBeTruthy()
      expect(tool.url.startsWith('/') || tool.url.startsWith('https://')).toBe(true)
    }
  })

  it('opens a tool by key and ignores an unknown key', () => {
    const { activeTool, openTool, closeTool } = useToolPanel()
    openTool('zap')
    expect(activeTool.value.key).toBe('zap')
    openTool('not-a-tool')
    expect(activeTool.value.key).toBe('zap')
    closeTool()
  })
})
