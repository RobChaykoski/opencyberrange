import { reactive } from 'vue'

// Shared, in-memory Cyber GPS answers. The questions are optional and the
// answers are not persisted by the platform; sharing the object lets the
// profile prompt preselect an answer in the GPS form.
const answers = reactive({})

export function useGpsAnswers() {
  return { answers }
}
