# Frontend Implementation Conventions

## Framework

- Vue 3 with `<script setup>` and the Composition API.
- Vue Router for navigation. Never use `window.location` for internal routes.
- Axios instance at `platform/frontend/src/api/axios.js` (base URL `/api`).
- No new UI framework, CSS framework, animation library, or icon package.
- Keep page CSS scoped. Global styles belong in `App.vue` only.

## Preferred composition

```vue
<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../api/axios'
import { useModules } from '../composables/useModules'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const data = ref(null)

const visible = computed(() => data.value?.items ?? [])

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data: payload } = await axios.get('/endpoint')
    data.value = payload
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load this page.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
```

## Reuse existing helpers

- `useModules()` for optional modules and `exerciseAuthoring`.
- `useVpnStatus()` for VPN status.
- `usePoll()` for polling that pauses on hidden tabs.
- `components/icons/trackIcons.js` — `getTrackIcon(track.icon)`.
- Existing certificate and transcript routes.

## Styling

- Use the CSS variables in `App.vue`.
- Use scoped class names such as `.profile-hero__name`.
- Avoid inline styles except dynamic values (progress width, track colour).
- Use `overflow-wrap: anywhere` for emails, usernames, IDs, and paths.
- Define responsive rules at the bottom of the scoped block.
- For print, add a scoped `@media print` block and hide `.no-print`.
- Do not use untrusted HTML. Render user/API text with interpolation or `textContent`.

## Accessibility

- Native controls first.
- Add labels and `aria-*` only where native semantics are insufficient.
- Use `:aria-valuenow` and friends on custom progress bars.
- Use `aria-hidden="true"` on decorative SVGs.
- Keep button text readable when the button is disabled.

## Security

- Never bind secrets to the DOM, even hidden elements.
- Do not build URLs with concatenated user input; use `encodeURIComponent` or the router.
- Do not trust `v-html`; it is only acceptable with a deliberate sanitizer such as DOMPurify and a documented reason.
- Never persist sensitive data in `localStorage` beyond the existing token/user contract.
- Treat API error text as untrusted; render it as text, not HTML.

## Quality gates

```bash
cd platform/frontend
npm run lint
npm run build
```

If backend contracts changed:

```bash
cd platform/backend
python -m pytest -q
```
