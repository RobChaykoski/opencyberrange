import { ref } from 'vue'
import axios from '../api/axios'

// The pathway catalogue is static for a deployment. Several components need
// it (the target-role switcher and the readiness panel), so fetch it once and
// share the in-flight request instead of issuing one call per component.
const roles = ref([])
let loaded = false
let inflight = null

export function useCareerRoles() {
  async function load() {
    if (loaded && roles.value.length) return roles.value
    if (inflight) return inflight
    inflight = axios
      .get('/profile/roles')
      .then(({ data }) => {
        roles.value = Array.isArray(data?.roles) ? data.roles : []
        loaded = roles.value.length > 0
        return roles.value
      })
      .finally(() => {
        inflight = null
      })
    return inflight
  }

  return { roles, load }
}
