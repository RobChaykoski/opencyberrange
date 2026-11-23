<template>
  <div class="echart" :style="{ height }">
    <div
      ref="chartEl"
      class="echart__canvas"
      role="img"
      :aria-label="ariaLabel"
    ></div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { init, use } from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  TooltipComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([
  BarChart,
  LineChart,
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  TooltipComponent,
  CanvasRenderer,
])

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '280px' },
  ariaLabel: { type: String, default: 'Chart' },
})

const emit = defineEmits(['chart-ready'])

const chartEl = ref(null)
let chart = null
let observer = null

const resize = () => {
  chart?.resize()
}

const render = () => {
  if (!chart || !props.option) return
  // Data refreshes replace the whole option object. notMerge avoids stale
  // series lingering when a dataset shrinks; lazyUpdate keeps the swap smooth.
  chart.setOption(props.option, { notMerge: true, lazyUpdate: true })
}

onMounted(() => {
  if (!chartEl.value) return
  chart = init(chartEl.value, null, { renderer: 'canvas' })
  render()
  emit('chart-ready', chart)

  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(resize)
    observer.observe(chartEl.value)
  } else {
    window.addEventListener('resize', resize)
  }
})

// Callers replace the whole option object on every data change (and notMerge
// is used below), so a shallow watch has the same behaviour without walking a
// large nested option tree on every refresh.
watch(() => props.option, render)

onBeforeUnmount(() => {
  observer?.disconnect()
  observer = null
  window.removeEventListener('resize', resize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.echart {
  width: 100%;
  min-width: 0;
}

.echart__canvas {
  width: 100%;
  height: 100%;
}
</style>
