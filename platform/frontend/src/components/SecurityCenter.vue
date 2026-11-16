<template>
  <section class="security-center" aria-labelledby="security-center-title">
    <header class="panel-header">
      <div>
        <h2 id="security-center-title" class="panel-title">Security center</h2>
        <p class="security-center__sub">
          Append-only security, audit, and privacy events; emergency access; and
          non-human service identities.
        </p>
      </div>
      <button type="button" class="btn btn--outline btn--sm" :disabled="loading" @click="refreshAll">
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </header>

    <div class="sub-tabs" role="tablist" aria-label="Security workspace">
      <button
        v-for="(tab, index) in tabs"
        :key="tab.key"
        :id="`security-tab-${tab.key}`"
        type="button"
        role="tab"
        :aria-selected="activeView === tab.key"
        :aria-controls="`security-panel-${tab.key}`"
        :tabindex="activeView === tab.key ? 0 : -1"
        :class="['sub-tab', { active: activeView === tab.key }]"
        @click="activeView = tab.key"
        @keydown="onTabKeydown($event, index)"
      >
        {{ tab.label }}
      </button>
    </div>

    <p v-if="error" class="security-state security-state--error" role="alert">{{ error }}</p>

    <template v-if="activeView === 'events'">
      <div
        id="security-panel-events"
        role="tabpanel"
        aria-labelledby="security-tab-events"
        class="security-panel"
      >
      <div class="security-summary" v-if="summary">
        <div class="security-summary__card">
          <span>Total</span><strong>{{ summary.total }}</strong>
        </div>
        <div class="security-summary__card">
          <span>Critical</span><strong>{{ summary.by_severity?.critical || 0 }}</strong>
        </div>
        <div class="security-summary__card">
          <span>Warnings</span><strong>{{ summary.by_severity?.warning || 0 }}</strong>
        </div>
        <div class="security-summary__card">
          <span>Denied</span><strong>{{ summary.by_outcome?.denied || 0 }}</strong>
        </div>
      </div>

      <div class="security-filters">
        <label>
          <span>Category</span>
          <select v-model="filters.category" @change="loadEvents">
            <option value="">All</option>
            <option value="security">Security</option>
            <option value="audit">Audit</option>
            <option value="privacy">Privacy</option>
          </select>
        </label>
        <label>
          <span>Severity</span>
          <select v-model="filters.severity" @change="loadEvents">
            <option value="">All</option>
            <option value="info">Info</option>
            <option value="notice">Notice</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
        </label>
        <label class="security-filters__search">
          <span>Search</span>
          <input v-model.trim="filters.search" type="search" placeholder="event, actor, path, target" @keyup.enter="loadEvents" />
        </label>
        <button type="button" class="btn btn--primary btn--sm" @click="loadEvents">Apply</button>
      </div>

      <div class="table-container" v-if="events.length">
        <table class="data-table">
          <caption class="visually-hidden">Security events, newest first</caption>
          <thead>
            <tr>
              <th scope="col">Time</th>
              <th scope="col">Severity</th>
              <th scope="col">Event</th>
              <th scope="col">Actor</th>
              <th scope="col">Target / path</th>
              <th scope="col">Outcome</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in events" :key="row.id">
              <td class="security-mono">{{ formatTime(row.occurred_at) }}</td>
              <td><span :class="['security-badge', `security-badge--${row.severity}`]">{{ row.severity }}</span></td>
              <td>
                <strong>{{ row.event_type }}</strong>
                <div v-if="row.action && row.action !== row.event_type" class="security-meta">{{ row.action }}</div>
              </td>
              <td>
                {{ row.actor_username || row.actor_id || 'system' }}
                <div v-if="row.actor_role" class="security-meta">{{ row.actor_role }}</div>
              </td>
              <td>
                {{ row.target_label || row.target_id || row.path || '-' }}
                <div v-if="row.path" class="security-meta security-mono">{{ row.path }}</div>
              </td>
              <td>{{ row.outcome }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="security-state">No events match the current filters.</p>
      </div>
    </template>

    <template v-else-if="activeView === 'break-glass'">
      <div
        id="security-panel-break-glass"
        role="tabpanel"
        aria-labelledby="security-tab-break-glass"
        class="security-panel"
      >
      <form class="security-form" @submit.prevent="requestBreakGlass">
        <h3>Request emergency access</h3>
        <p class="security-meta">
          MFA is required. The grant is time-bound, scoped when a learner id is
          supplied, and every use is a critical event.
        </p>
        <label>
          <span>Permission</span>
          <select v-model="grantForm.permission" required>
            <option v-for="item in eligiblePermissions" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>
        <label>
          <span>Reason (minimum 10 characters)</span>
          <textarea v-model.trim="grantForm.reason" rows="3" required minlength="10" />
        </label>
        <div class="security-form__row">
          <label>
            <span>Reference</span>
            <input v-model.trim="grantForm.reference" placeholder="INC-42" />
          </label>
          <label>
            <span>Minutes</span>
            <input v-model.number="grantForm.minutes" type="number" min="1" max="1440" />
          </label>
          <label>
            <span>Learner id (optional)</span>
            <input v-model.number="grantForm.user_id" type="number" min="1" />
          </label>
        </div>
        <button type="submit" class="btn btn--danger btn--sm" :disabled="saving">
          {{ saving ? 'Requesting...' : 'Request break-glass' }}
        </button>
      </form>

      <div class="table-container" v-if="grants.length">
        <table class="data-table">
          <caption class="visually-hidden">Break-glass grants</caption>
          <thead>
            <tr><th scope="col">User</th><th scope="col">Permission</th><th scope="col">Status</th><th scope="col">Expires</th><th scope="col">Uses</th><th scope="col">Review</th><th scope="col">Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in grants" :key="row.id">
              <td>{{ row.username || row.user_id }}</td>
              <td>{{ row.permission }}<div v-if="row.reference" class="security-meta">{{ row.reference }}</div></td>
              <td><span :class="['security-badge', `security-badge--${row.status}`]">{{ row.status }}</span></td>
              <td class="security-mono">{{ formatTime(row.expires_at) }}</td>
              <td>{{ row.use_count }}</td>
              <td>{{ row.review_status }}</td>
              <td class="security-actions">
                <button v-if="row.status === 'pending'" type="button" class="btn btn--outline btn--sm" @click="approveGrant(row)">Approve</button>
                <button v-if="row.status === 'active' || row.status === 'pending'" type="button" class="btn btn--outline btn--sm" @click="revokeGrant(row)">Revoke</button>
                <button v-if="row.review_status !== 'reviewed'" type="button" class="btn btn--outline btn--sm" @click="reviewGrant(row)">Review</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="security-state">No break-glass grants.</p>
      </div>
    </template>

    <template v-else-if="activeView === 'services'">
      <div
        id="security-panel-services"
        role="tabpanel"
        aria-labelledby="security-tab-services"
        class="security-panel"
      >
      <form class="security-form" @submit.prevent="createService">
        <h3>Create a service identity</h3>
        <p class="security-meta">
          The raw token is shown once. A service identity has no password login and
          only the scopes you select.
        </p>
        <div class="security-form__row">
          <label>
            <span>Name</span>
            <input v-model.trim="serviceForm.name" required minlength="3" />
          </label>
          <label>
            <span>Days</span>
            <input v-model.number="serviceForm.days" type="number" min="1" max="365" />
          </label>
        </div>
        <label>
          <span>Scopes</span>
          <select v-model="serviceForm.scopes" multiple size="6" class="security-scopes">
            <option v-for="item in serviceScopes" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>
        <button type="submit" class="btn btn--primary btn--sm" :disabled="saving">
          {{ saving ? 'Creating...' : 'Create service identity' }}
        </button>
        <p v-if="newServiceToken" class="security-token">
          <strong>Copy this token now:</strong>
          <code>{{ newServiceToken }}</code>
        </p>
      </form>

      <div class="table-container" v-if="services.length">
        <table class="data-table">
          <caption class="visually-hidden">Service identities</caption>
          <thead><tr><th scope="col">Name</th><th scope="col">User</th><th scope="col">Scopes</th><th scope="col">Expires</th><th scope="col">Last used</th><th scope="col">Actions</th></tr></thead>
          <tbody>
            <tr v-for="row in services" :key="row.id">
              <td>{{ row.name }}</td>
              <td class="security-mono">{{ row.username }}</td>
              <td>{{ (row.scopes || []).join(', ') }}</td>
              <td class="security-mono">{{ formatTime(row.expires_at) }}</td>
              <td class="security-mono">{{ formatTime(row.last_used_at) }}</td>
              <td><button v-if="row.active" type="button" class="btn btn--outline btn--sm" @click="revokeService(row)">Revoke</button></td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="security-state">No service identities.</p>
      </div>
    </template>

    <template v-else-if="activeView === 'roles'">
      <div
        id="security-panel-roles"
        role="tabpanel"
        aria-labelledby="security-tab-roles"
        class="security-panel"
      >
        <div class="security-section-head">
          <div>
            <h3>Role catalog</h3>
            <p class="security-meta">
              Roles are the reviewed starting point. A role grant is necessary
              but not sufficient: policy rules still decide the record, tenant,
              and consent scope.
            </p>
          </div>
          <button type="button" class="btn btn--outline btn--sm" @click="loadRoles">
            Refresh roles
          </button>
        </div>

        <div class="table-container" v-if="roles.length">
          <table class="data-table">
            <caption class="visually-hidden">RBAC roles</caption>
            <thead>
              <tr>
                <th scope="col">Role</th>
                <th scope="col">Label</th>
                <th scope="col">Tenant scope</th>
                <th scope="col">Allowed</th>
                <th scope="col">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in roles" :key="row.key">
                <th scope="row" class="security-mono">{{ row.key }}</th>
                <td>{{ row.label }}</td>
                <td>{{ row.tenant_scope || 'institution' }}</td>
                <td>{{ row.permissions.length }}</td>
                <td>
                  <button
                    type="button"
                    class="btn btn--outline btn--xs"
                    @click="editRole(row)"
                  >
                    Edit permissions
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="security-state">Role catalog unavailable.</p>

        <section
          v-if="selectedRole"
          class="role-editor"
          aria-labelledby="role-editor-title"
        >
          <div class="security-section-head">
            <div>
              <h3 id="role-editor-title">
                {{ selectedRole.label }}
                <span class="security-mono security-meta">{{ selectedRole.key }}</span>
              </h3>
              <p class="security-meta">
                Allow adds a grant. Deny removes it; the platform is deny-by-default.
                Private permissions stay owner/share/break-glass only.
              </p>
            </div>
            <div class="role-editor__actions">
              <button type="button" class="btn btn--outline btn--sm" @click="resetRoleDraft">
                Reset
              </button>
              <button
                type="button"
                class="btn btn--success btn--sm"
                :disabled="!roleDirty || roleSaving || roleChangeReason.trim().length < 5"
                @click="saveRolePermissions"
              >
                {{ roleSaving ? 'Saving...' : 'Save change set' }}
              </button>
            </div>
          </div>

          <div class="security-summary">
            <div class="security-summary__card">
              <span>Adds</span><strong>{{ roleDelta.adds }}</strong>
            </div>
            <div class="security-summary__card">
              <span>Denies</span><strong>{{ roleDelta.denies }}</strong>
            </div>
            <div class="security-summary__card">
              <span>Unchanged</span><strong>{{ roleDelta.unchanged }}</strong>
            </div>
            <div class="security-summary__card">
              <span>Total allowed</span><strong>{{ roleDraft.length }}</strong>
            </div>
          </div>

          <div class="security-filters">
            <label class="security-filters__search">
              <span>Search permissions</span>
              <input
                v-model.trim="permissionSearch"
                type="search"
                placeholder="permission, description, category"
              />
            </label>
            <label>
              <span>Category</span>
              <select v-model="permissionCategory">
                <option value="">All categories</option>
                <option v-for="category in permissionCategories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </label>
            <label class="security-filters__reason">
              <span>Why is this role changing?</span>
              <input
                v-model.trim="roleChangeReason"
                type="text"
                maxlength="500"
                placeholder="Ticket, access review, or reason (required)"
              />
            </label>
          </div>

          <div class="permission-groups">
            <section
              v-for="group in filteredPermissionGroups"
              :key="group.category"
              class="permission-group"
            >
              <h4>{{ group.category }}</h4>
              <div
                v-for="permission in group.permissions"
                :key="permission.key"
                class="permission-row"
              >
                <div class="permission-info">
                  <code>{{ permission.key }}</code>
                  <p>{{ permission.description }}</p>
                  <div class="permission-meta">
                    <span class="security-badge">{{ permission.scope }}</span>
                    <span :class="['security-badge', `security-badge--${permission.sensitivity}`]">
                      {{ permission.sensitivity }}
                    </span>
                    <span v-if="permission.read_only" class="security-badge security-badge--readonly">
                      read-only
                    </span>
                    <span v-if="permission.break_glass" class="security-badge security-badge--breakglass">
                      break-glass
                    </span>
                    <span v-if="permission.sensitivity === 'restricted'" class="security-badge security-badge--restricted">
                      owner/share only
                    </span>
                  </div>
                </div>
                <div class="permission-actions" role="group" :aria-label="`${permission.key} decision`">
                  <button
                    type="button"
                    class="permission-choice"
                    :class="{ 'permission-choice--allow': roleHasPermission(permission.key) }"
                    :disabled="permission.sensitivity === 'restricted'"
                    :aria-pressed="roleHasPermission(permission.key)"
                    @click="allowPermission(permission.key)"
                  >
                    Allow
                  </button>
                  <button
                    type="button"
                    class="permission-choice"
                    :class="{ 'permission-choice--deny': !roleHasPermission(permission.key) }"
                    :aria-pressed="!roleHasPermission(permission.key)"
                    @click="denyPermission(permission.key)"
                  >
                    Deny
                  </button>
                </div>
              </div>
            </section>
          </div>
          <p v-if="!filteredPermissionGroups.length" class="security-state">
            No permissions match the current filters.
          </p>
          <p class="security-meta">
            Saving records a <code>rbac.permissions_changed</code> event and
            invalidates active sessions for users with this role.
          </p>
        </section>

        <section class="mac-panel" aria-labelledby="mac-title">
          <div class="security-section-head">
            <div>
              <h3 id="mac-title">Moves, Adds, Changes</h3>
              <p class="security-meta">
                Add an expiring extra role, move a user's primary role, or remove
                an extra role. Every action is audited; reasons are required.
              </p>
            </div>
            <button type="button" class="btn btn--outline btn--sm" @click="loadMacUsers">
              {{ macLoading ? 'Loading...' : 'Reload users' }}
            </button>
          </div>

          <div class="mac-grid">
            <label>
              <span>Find user</span>
              <input v-model.trim="macUserSearch" type="search" placeholder="username, email, or role" />
            </label>
            <label>
              <span>User</span>
              <select v-model="macSelectedUserId" @change="loadMacUser">
                <option value="">Select a user</option>
                <option v-for="user in macFilteredUsers" :key="user.id" :value="String(user.id)">
                  {{ user.username }} · {{ user.role }}
                </option>
              </select>
            </label>
            <label>
              <span>Action</span>
              <select v-model="macAction" @change="onMacActionChange">
                <option value="add">Add extra role</option>
                <option value="move">Move primary role</option>
                <option value="remove">Remove extra role</option>
              </select>
            </label>
            <label>
              <span>Role</span>
              <select v-model="macRoleKey">
                <option value="">Select a role</option>
                <option v-for="role in macRoleOptions" :key="role.key" :value="role.key">
                  {{ role.label }}
                </option>
              </select>
            </label>
            <label>
              <span>Reason</span>
              <input v-model.trim="macReason" type="text" maxlength="500" placeholder="Access review or ticket (required)" />
            </label>
            <label v-if="macAction === 'add'">
              <span>Expires (optional)</span>
              <input v-model="macExpiresAt" type="datetime-local" />
            </label>
          </div>

          <p v-if="macSelectedUser" class="security-meta">
            Current roles:
            <span v-for="role in macUserRoles" :key="role" class="security-badge">{{ role }}</span>
          </p>
          <div class="form-actions">
            <button
              type="button"
              class="btn btn--primary btn--sm"
              :disabled="macBusy || !macCanSubmit"
              @click="submitMacChange"
            >
              {{ macBusy ? 'Applying...' : 'Apply access change' }}
            </button>
          </div>

          <div v-if="macEvents.length" class="mac-history">
            <h4>Recent RBAC changes</h4>
            <div class="table-container">
              <table class="data-table">
                <thead><tr><th scope="col">Time</th><th scope="col">Event</th><th scope="col">Actor</th><th scope="col">Target</th><th scope="col">Detail</th></tr></thead>
                <tbody>
                  <tr v-for="event in macEvents" :key="event.id">
                    <td class="security-mono">{{ formatTime(event.occurred_at) }}</td>
                    <td><code>{{ event.event_type }}</code></td>
                    <td>{{ event.actor_username || 'system' }}</td>
                    <td>{{ event.target_label || event.target_id || '—' }}</td>
                    <td class="security-meta">{{ macEventDetail(event) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
    </template>

    <template v-else>
      <div
        id="security-panel-matrix"
        role="tabpanel"
        aria-labelledby="security-tab-matrix"
        class="security-panel"
      >
        <div v-if="matrixLoading && !matrix" class="security-state">
          Loading the access matrix...
        </div>
        <p v-else-if="matrixError" class="security-state security-state--error" role="alert">
          {{ matrixError }}
        </p>
        <template v-else-if="matrix">
          <div class="security-summary">
            <div class="security-summary__card">
              <span>Roles</span><strong>{{ matrix.summary.roles }}</strong>
            </div>
            <div class="security-summary__card">
              <span>Permissions</span><strong>{{ matrix.summary.permissions }}</strong>
            </div>
            <div class="security-summary__card">
              <span>Restricted</span><strong>{{ matrix.summary.restricted }}</strong>
            </div>
            <div class="security-summary__card">
              <span>Break-glass eligible</span><strong>{{ matrix.summary.break_glass }}</strong>
            </div>
          </div>

          <div class="security-filters">
            <label class="security-filters__search">
              <span>Search permissions</span>
              <input
                v-model.trim="matrixFilters.search"
                type="search"
                placeholder="permission, description, category"
              />
            </label>
            <label>
              <span>Scope</span>
              <select v-model="matrixFilters.scope">
                <option value="">All scopes</option>
                <option v-for="scope in matrixScopes" :key="scope" :value="scope">{{ scope }}</option>
              </select>
            </label>
            <label>
              <span>Sensitivity</span>
              <select v-model="matrixFilters.sensitivity">
                <option value="">All sensitivities</option>
                <option v-for="level in matrixSensitivities" :key="level" :value="level">{{ level }}</option>
              </select>
            </label>
            <label>
              <span>Granted to</span>
              <select v-model="matrixFilters.role">
                <option value="">All roles</option>
                <option v-for="role in matrix.roles" :key="role.key" :value="role.key">{{ role.label }}</option>
              </select>
            </label>
            <label class="security-filter-check">
              <input v-model="matrixFilters.breakGlass" type="checkbox" />
              <span>Break-glass eligible only</span>
            </label>
            <button
              type="button"
              class="btn btn--outline btn--sm"
              :disabled="!matrixFiltersActive"
              @click="clearMatrixFilters"
            >
              Clear filters
            </button>
          </div>

          <p class="security-matrix__count" aria-live="polite">
            Showing {{ filteredMatrixRows.length }} of {{ matrix.permissions.length }} permissions.
          </p>

          <div class="security-matrix__legend">
            <span><span class="security-matrix__mark security-matrix__mark--yes" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg></span> Granted</span>
            <span><span class="security-matrix__mark security-matrix__mark--no" aria-hidden="true">–</span> Not granted</span>
            <span><span class="security-badge security-badge--restricted">restricted</span> private; owner, share, or break-glass only</span>
          </div>

          <div class="security-matrix__clip">
          <div
            class="table-container security-matrix__scroll"
            tabindex="0"
            role="region"
            aria-label="Role and permission matrix"
          >
            <table class="data-table security-matrix">
              <caption class="visually-hidden">
                Effective role grants by permission, with policy attributes
              </caption>
              <thead>
                <tr>
                  <th scope="col" class="security-matrix__permission">Permission</th>
                  <th v-for="role in visibleMatrixRoles" :key="role.key" scope="col">
                    <span class="security-matrix__role">{{ role.label }}</span>
                    <span class="security-meta">{{ role.key }} · rank {{ role.rank }}</span>
                    <span class="security-meta">tenant: {{ role.tenant_scope || 'institution' }}</span>
                  </th>
                  <th scope="col">Policy</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filteredMatrixRows" :key="row.key">
                  <th scope="row" class="security-matrix__permission">
                    <span class="security-mono">{{ row.key }}</span>
                    <span class="security-meta">{{ row.description }}</span>
                  </th>
                  <td v-for="role in visibleMatrixRoles" :key="role.key" class="security-matrix__cell">
                    <span
                      v-if="row.roles[role.key]"
                      class="security-matrix__mark security-matrix__mark--yes"
                    >
                      <span aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg></span>
                      <span class="visually-hidden">Granted to {{ role.label }}</span>
                    </span>
                    <span v-else class="security-matrix__mark security-matrix__mark--no">
                      <span aria-hidden="true">–</span>
                      <span class="visually-hidden">Not granted to {{ role.label }}</span>
                    </span>
                  </td>
                  <td class="security-matrix__policy">
                    <span class="security-badge">{{ row.scope }}</span>
                    <span :class="['security-badge', `security-badge--${row.sensitivity}`]">{{ row.sensitivity }}</span>
                    <span v-if="row.read_only" class="security-badge security-badge--readonly">read-only</span>
                    <span v-if="row.break_glass" class="security-badge security-badge--breakglass">break-glass</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          </div>

          <p v-if="!filteredMatrixRows.length" class="security-state">
            No permissions match the current filters.
            <button type="button" class="btn btn--outline btn--xs" @click="clearMatrixFilters">
              Clear filters
            </button>
          </p>

          <section class="security-policy" aria-labelledby="security-policy-title">
            <h3 id="security-policy-title">Policy attributes (PBAC)</h3>
            <p class="security-meta">
              A role grant is necessary but not sufficient. These rules decide
              whether the grant applies to a specific record, tenant, or learner.
            </p>
            <div class="security-policy__grid">
              <article v-for="rule in matrix.policy_rules" :key="rule.id" class="security-policy__card">
                <h4>{{ rule.label }}</h4>
                <p>{{ rule.rule }}</p>
                <span class="security-meta">Enforced by: {{ rule.enforced_by }}</span>
              </article>
            </div>
          </section>
        </template>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import axios from '../api/axios'
import { showToast } from './Toast.vue'

const tabs = [
  { key: 'events', label: 'Events' },
  { key: 'break-glass', label: 'Break-glass' },
  { key: 'services', label: 'Service identities' },
  { key: 'roles', label: 'Roles' },
  { key: 'matrix', label: 'Access matrix' },
]
const activeView = ref('events')
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const events = ref([])
const summary = ref(null)
const grants = ref([])
const services = ref([])
const roles = ref([])
const permissionCatalog = ref([])
const selectedRoleKey = ref('')
const roleDraft = ref([])
const roleChangeReason = ref('')
const roleSaving = ref(false)
const permissionSearch = ref('')
const permissionCategory = ref('')
const macUsers = ref([])
const macLoading = ref(false)
const macUserSearch = ref('')
const macSelectedUserId = ref('')
const macAction = ref('add')
const macRoleKey = ref('')
const macReason = ref('')
const macExpiresAt = ref('')
const macBusy = ref(false)
const macUserRoles = ref([])
const macEvents = ref([])
const matrix = ref(null)
const matrixLoading = ref(false)
const matrixError = ref('')
const matrixFilters = reactive({ search: '', scope: '', sensitivity: '', role: '', breakGlass: false })
const newServiceToken = ref('')
const filters = reactive({ category: '', severity: '', search: '' })
const grantForm = reactive({ permission: 'dna.view.private', reason: '', reference: '', minutes: 60, user_id: null })
const serviceForm = reactive({ name: '', days: 90, scopes: [] })
const eligiblePermissions = [
  'dna.view.private',
  'gps.view.private',
  'coach.transcript.view',
  'export.restricted',
  'audit.view',
]
const serviceScopes = computed(() => {
  const row = roles.value.find((item) => item.key === 'admin')
  return (row?.permissions || []).filter((item) => !item.includes('.private') && !item.endsWith('.restricted')).sort()
})

const permissionCategories = computed(() =>
  [...new Set(permissionCatalog.value.map((item) => item.category || 'Uncategorised'))].sort()
)
const filteredPermissionGroups = computed(() => {
  const query = permissionSearch.value.toLowerCase()
  const groups = new Map()
  for (const permission of permissionCatalog.value) {
    if (permissionCategory.value && (permission.category || 'Uncategorised') !== permissionCategory.value) {
      continue
    }
    if (
      query &&
      ![permission.key, permission.description, permission.category]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query))
    ) {
      continue
    }
    const category = permission.category || 'Uncategorised'
    if (!groups.has(category)) groups.set(category, [])
    groups.get(category).push(permission)
  }
  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([category, permissions]) => ({
      category,
      permissions: permissions.sort((a, b) => a.key.localeCompare(b.key)),
    }))
})
const selectedRole = computed(() => roles.value.find((row) => row.key === selectedRoleKey.value) || null)
const roleDraftSet = computed(() => new Set(roleDraft.value))
const roleDirty = computed(() => {
  if (!selectedRole.value) return false
  const original = [...selectedRole.value.permissions].sort()
  const draft = [...roleDraft.value].sort()
  return original.length !== draft.length || original.some((key, index) => key !== draft[index])
})
const roleDelta = computed(() => {
  if (!selectedRole.value) return { adds: 0, denies: 0, unchanged: 0 }
  const original = new Set(selectedRole.value.permissions)
  const draft = new Set(roleDraft.value)
  return {
    adds: [...draft].filter((key) => !original.has(key)).length,
    denies: [...original].filter((key) => !draft.has(key)).length,
    unchanged: [...draft].filter((key) => original.has(key)).length,
  }
})
const macFilteredUsers = computed(() => {
  const query = macUserSearch.value.toLowerCase()
  const rows = macUsers.value
  if (!query) return rows.slice(0, 60)
  return rows
    .filter((user) =>
      [user.username, user.email, user.role]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query))
    )
    .slice(0, 60)
})
const macSelectedUser = computed(
  () => macUsers.value.find((user) => String(user.id) === String(macSelectedUserId.value)) || null
)
const macExtraRoles = computed(() =>
  macUserRoles.value.filter((role) => role !== macSelectedUser.value?.role)
)
const macRoleOptions = computed(() => {
  if (macAction.value === 'remove') {
    return roles.value.filter((role) => macExtraRoles.value.includes(role.key))
  }
  return roles.value
})
const macCanSubmit = computed(() => {
  if (!macSelectedUser.value || !macRoleKey.value || macReason.value.trim().length < 5) return false
  if (macAction.value === 'move' && macRoleKey.value === macSelectedUser.value.role) return false
  if (macAction.value === 'add' && macUserRoles.value.includes(macRoleKey.value)) return false
  if (macAction.value === 'remove' && !macExtraRoles.value.includes(macRoleKey.value)) return false
  return true
})

const matrixScopes = computed(() => Object.keys(matrix.value?.summary?.scopes || {}))
const matrixSensitivities = computed(() => Object.keys(matrix.value?.summary?.sensitivities || {}))
const matrixFiltersActive = computed(
  () => Boolean(
    matrixFilters.search ||
      matrixFilters.scope ||
      matrixFilters.sensitivity ||
      matrixFilters.role ||
      matrixFilters.breakGlass
  )
)
const visibleMatrixRoles = computed(() => {
  const all = matrix.value?.roles || []
  if (!matrixFilters.role) return all
  return all.filter((role) => role.key === matrixFilters.role)
})
const filteredMatrixRows = computed(() => {
  const rows = matrix.value?.permissions || []
  const query = matrixFilters.search.toLowerCase()
  return rows.filter((row) => {
    if (matrixFilters.scope && row.scope !== matrixFilters.scope) return false
    if (matrixFilters.sensitivity && row.sensitivity !== matrixFilters.sensitivity) return false
    if (matrixFilters.breakGlass && !row.break_glass) return false
    if (matrixFilters.role && !row.roles?.[matrixFilters.role]) return false
    if (!query) return true
    return [row.key, row.description, row.category]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query))
  })
})

function clearMatrixFilters() {
  matrixFilters.search = ''
  matrixFilters.scope = ''
  matrixFilters.sensitivity = ''
  matrixFilters.role = ''
  matrixFilters.breakGlass = false
}

function onTabKeydown(event, index) {
  if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(event.key)) return
  event.preventDefault()
  let next = index
  if (event.key === 'ArrowRight') next = (index + 1) % tabs.length
  if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length
  if (event.key === 'Home') next = 0
  if (event.key === 'End') next = tabs.length - 1
  activeView.value = tabs[next].key
  const buttons = event.currentTarget.parentElement.querySelectorAll('[role="tab"]')
  buttons[next]?.focus()
}

function formatTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function loadEvents() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.category) params.category = filters.category
    if (filters.severity) params.severity = filters.severity
    if (filters.search) params.search = filters.search
    const [eventResponse, summaryResponse] = await Promise.all([
      axios.get('/admin/security/events', { params: { ...params, limit: 100 } }),
      axios.get('/admin/security/events/summary', { params: { days: 30 } }),
    ])
    events.value = eventResponse.data.events || []
    summary.value = summaryResponse.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load security events.'
  } finally {
    loading.value = false
  }
}

async function loadGrants() {
  const response = await axios.get('/admin/security/break-glass')
  grants.value = response.data.grants || []
}

async function loadServices() {
  const response = await axios.get('/admin/security/service-identities')
  services.value = response.data.credentials || []
}

async function loadRoles() {
  const response = await axios.get('/admin/security/rbac/roles')
  roles.value = response.data.roles || []
}

async function loadPermissions() {
  const response = await axios.get('/admin/security/rbac/permissions')
  permissionCatalog.value = response.data.permissions || []
}

function editRole(row) {
  selectedRoleKey.value = row.key
  roleDraft.value = [...row.permissions]
  roleChangeReason.value = ''
  permissionSearch.value = ''
  permissionCategory.value = ''
}

function resetRoleDraft() {
  if (!selectedRole.value) return
  roleDraft.value = [...selectedRole.value.permissions]
  roleChangeReason.value = ''
}

function roleHasPermission(key) {
  return roleDraftSet.value.has(key)
}

function allowPermission(key) {
  const permission = permissionCatalog.value.find((item) => item.key === key)
  if (permission?.sensitivity === 'restricted') return
  if (!roleDraftSet.value.has(key)) roleDraft.value = [...roleDraft.value, key]
}

function denyPermission(key) {
  roleDraft.value = roleDraft.value.filter((item) => item !== key)
}

async function saveRolePermissions() {
  if (!selectedRole.value || !roleDirty.value) return
  if (roleChangeReason.value.trim().length < 5) {
    showToast('Add a reason or ticket for the role change.', 'error')
    return
  }
  roleSaving.value = true
  try {
    await axios.put(`/admin/security/rbac/roles/${selectedRole.value.key}/permissions`, {
      permissions: roleDraft.value,
      reason: roleChangeReason.value.trim(),
    })
    await Promise.all([loadRoles(), loadMatrix(), loadMacEvents()])
    selectedRoleKey.value = ''
    roleDraft.value = []
    roleChangeReason.value = ''
    showToast('Role grants updated.', 'success')
  } catch (e) {
    const detail = e.response?.data?.detail
    showToast(detail?.message || detail || 'Role update failed.', 'error')
  } finally {
    roleSaving.value = false
  }
}

async function loadMacUsers() {
  macLoading.value = true
  try {
    const response = await axios.get('/admin/users')
    macUsers.value = response.data || []
  } catch (e) {
    showToast(e.response?.data?.detail || 'Could not load users for access changes.', 'error')
  } finally {
    macLoading.value = false
  }
}

async function loadMacUser() {
  macRoleKey.value = ''
  if (!macSelectedUserId.value) {
    macUserRoles.value = []
    return
  }
  try {
    const response = await axios.get(`/admin/security/rbac/users/${macSelectedUserId.value}`)
    macUserRoles.value = response.data.roles || []
  } catch (e) {
    macUserRoles.value = []
    showToast(e.response?.data?.detail || 'Could not load the user access record.', 'error')
  }
}

function onMacActionChange() {
  macRoleKey.value = ''
}

async function loadMacEvents() {
  try {
    const response = await axios.get('/admin/security/events', {
      params: { search: 'rbac', limit: 10 },
    })
    macEvents.value = response.data.events || []
  } catch {
    macEvents.value = []
  }
}

function macEventDetail(event) {
  const detail = event.detail || {}
  if (detail.reason) return detail.reason
  if (Array.isArray(detail.permissions)) return `${detail.permissions.length} permission(s)`
  if (detail.role) return detail.role
  return event.outcome || '—'
}

async function submitMacChange() {
  if (!macCanSubmit.value) return
  const user = macSelectedUser.value
  if (!user) return
  macBusy.value = true
  try {
    if (macAction.value === 'add') {
      await axios.post(`/admin/security/rbac/users/${user.id}/roles`, {
        role_key: macRoleKey.value,
        reason: macReason.value.trim(),
        expires_at: macExpiresAt.value ? new Date(macExpiresAt.value).toISOString() : null,
      })
    } else if (macAction.value === 'move') {
      await axios.put(`/admin/users/${user.id}`, { role: macRoleKey.value })
    } else {
      await axios.delete(`/admin/security/rbac/users/${user.id}/roles/${macRoleKey.value}`)
    }
    macReason.value = ''
    macExpiresAt.value = ''
    macRoleKey.value = ''
    await Promise.all([loadMacUser(), loadRoles(), loadMacEvents()])
    showToast('Access change applied.', 'success')
  } catch (e) {
    const detail = e.response?.data?.detail
    showToast(detail?.message || detail || 'Access change failed.', 'error')
  } finally {
    macBusy.value = false
  }
}

async function loadMatrix() {
  matrixLoading.value = true
  matrixError.value = ''
  try {
    const response = await axios.get('/admin/security/rbac/matrix')
    matrix.value = response.data
  } catch (e) {
    matrixError.value = e.response?.data?.detail || 'Could not load the access matrix.'
  } finally {
    matrixLoading.value = false
  }
}

async function refreshAll() {
  try {
    await Promise.all([loadEvents(), loadGrants(), loadServices(), loadRoles(), loadPermissions(), loadMatrix()])
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not refresh the security center.'
  }
}

async function requestBreakGlass() {
  saving.value = true
  try {
    const payload = {
      permission: grantForm.permission,
      reason: grantForm.reason,
      minutes: grantForm.minutes || 60,
      reference: grantForm.reference || null,
      user_id: grantForm.user_id || null,
    }
    await axios.post('/admin/security/break-glass', payload)
    grantForm.reason = ''
    grantForm.reference = ''
    grantForm.user_id = null
    await loadGrants()
    showToast('Break-glass request recorded.', 'success')
  } catch (e) {
    showToast(e.response?.data?.detail || 'Break-glass request failed.', 'error')
  } finally {
    saving.value = false
  }
}

async function approveGrant(row) {
  try {
    await axios.post(`/admin/security/break-glass/${row.id}/approve`)
    await loadGrants()
  } catch (e) {
    showToast(e.response?.data?.detail || 'Approval failed.', 'error')
  }
}

async function revokeGrant(row) {
  try {
    await axios.post(`/admin/security/break-glass/${row.id}/revoke`, { reason: 'Revoked from security center' })
    await loadGrants()
  } catch (e) {
    showToast(e.response?.data?.detail || 'Revocation failed.', 'error')
  }
}

async function reviewGrant(row) {
  const note = window.prompt('Review note (required)')
  if (!note?.trim()) return
  try {
    await axios.post(`/admin/security/break-glass/${row.id}/review`, { note })
    await loadGrants()
  } catch (e) {
    showToast(e.response?.data?.detail || 'Review failed.', 'error')
  }
}

async function createService() {
  saving.value = true
  newServiceToken.value = ''
  try {
    const response = await axios.post('/admin/security/service-identities', {
      name: serviceForm.name,
      days: serviceForm.days || 90,
      scopes: serviceForm.scopes,
    })
    newServiceToken.value = response.data.token
    serviceForm.name = ''
    serviceForm.scopes = []
    await loadServices()
    showToast('Service identity created. Copy the token now.', 'success')
  } catch (e) {
    showToast(e.response?.data?.detail || 'Service identity creation failed.', 'error')
  } finally {
    saving.value = false
  }
}

async function revokeService(row) {
  if (!window.confirm(`Revoke service identity "${row.name}"?`)) return
  try {
    await axios.delete(`/admin/security/service-identities/${row.id}`)
    await loadServices()
  } catch (e) {
    showToast(e.response?.data?.detail || 'Revocation failed.', 'error')
  }
}

watch(activeView, (view) => {
  if (view !== 'roles') return
  if (!permissionCatalog.value.length) loadPermissions()
  if (!macUsers.value.length) loadMacUsers()
  loadMacEvents()
})

onMounted(refreshAll)
</script>

<style scoped>
.security-center { display: grid; gap: 1rem; min-width: 0; overflow-x: clip; }
.security-center__sub { color: var(--text-muted); margin: 0.25rem 0 0; }
.security-panel { display: grid; gap: 1rem; min-width: 0; overflow-x: clip; }
.security-summary { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.75rem; }
.security-summary__card { border: 1px solid var(--border-color); background: var(--bg-secondary); border-radius: 12px; padding: 0.75rem; display: grid; gap: 0.25rem; }
.security-summary__card span { color: var(--text-secondary); font-size: 0.8rem; }
.security-summary__card strong { font-size: 1.4rem; color: var(--text-primary); }
.security-filters { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: end; }
.security-filters label { display: grid; gap: 0.25rem; font-size: 0.8rem; color: var(--text-secondary); }
.security-filters__search { flex: 1 1 16rem; }
.security-filter-check { display: flex; align-items: center; gap: 0.4rem; padding-bottom: 0.35rem; }
.security-filter-check input { width: auto; }
.security-filters input, .security-filters select, .security-form input, .security-form textarea, .security-form select { padding: 0.45rem 0.55rem; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-primary); color: var(--text-primary); }
.security-form { display: grid; gap: 0.75rem; border: 1px solid var(--border-color); background: var(--bg-secondary); border-radius: 12px; padding: 1rem; }
.security-form h3 { margin: 0; }
.security-form label { display: grid; gap: 0.25rem; font-size: 0.85rem; color: var(--text-secondary); }
.security-form__row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.75rem; }
.security-scopes { width: 100%; }
.security-meta { color: var(--text-muted); font-size: 0.8rem; }
.security-mono { font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.8rem; overflow-wrap: anywhere; }
.security-badge { display: inline-block; padding: 0.1rem 0.45rem; border-radius: 999px; font-size: 0.75rem; background: var(--bg-tertiary); color: var(--text-secondary); }
.security-badge--critical, .security-badge--revoked, .security-badge--restricted, .security-badge--high { background: var(--danger-bg); color: var(--danger); }
.security-badge--warning, .security-badge--pending, .security-badge--medium { background: var(--warning-bg); color: var(--warning); }
.security-badge--notice, .security-badge--active, .security-badge--low { background: var(--accent-bg); color: var(--accent-text); }
.security-badge--readonly { background: var(--bg-tertiary); color: var(--text-secondary); }
.security-badge--breakglass { background: var(--danger-bg); color: var(--danger); border: 1px solid var(--danger); }
.security-state { color: var(--text-muted); }
.security-state--error { color: var(--danger); }
.security-actions { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.security-token { background: var(--bg-primary); border: 1px dashed var(--border-color); padding: 0.75rem; border-radius: 10px; }
.security-token code { display: block; margin-top: 0.35rem; word-break: break-all; color: var(--text-primary); }
.security-matrix__count { margin: 0; color: var(--text-secondary); font-size: 0.8rem; }
.security-matrix__legend { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; color: var(--text-secondary); font-size: 0.8rem; }
.security-matrix__scroll { max-width: 100%; min-width: 0; max-height: 34rem; overflow: auto; contain: layout paint; border: 1px solid var(--border-color); border-radius: 10px; }
.security-matrix__clip { overflow: hidden; max-width: 100%; min-width: 0; }
.security-matrix { min-width: 980px; border-collapse: collapse; }
.security-matrix th, .security-matrix td { padding: 0.5rem 0.55rem; border-bottom: 1px solid var(--border-color); vertical-align: top; text-align: left; }
.security-matrix thead th { position: sticky; top: 0; background: var(--bg-secondary); z-index: 2; }
.security-matrix__permission { position: sticky; left: 0; background: var(--bg-secondary); z-index: 1; min-width: 18rem; max-width: 26rem; }
.security-matrix tbody .security-matrix__permission { background: var(--bg-primary); }
.security-matrix thead .security-matrix__permission { z-index: 3; }
.security-matrix__role { display: block; font-weight: 600; color: var(--text-primary); }
.security-matrix__cell { text-align: center; }
.security-matrix__mark { display: inline-flex; align-items: center; justify-content: center; width: 1.5rem; height: 1.5rem; border-radius: 999px; font-weight: 700; }
.security-matrix__mark svg { width: 0.9rem; height: 0.9rem; }
.security-matrix__mark--yes { color: var(--success); background: var(--success-bg); }
.security-matrix__mark--no { color: var(--text-muted); }
.security-matrix__policy { display: flex; flex-wrap: wrap; gap: 0.25rem; min-width: 12rem; }
.security-policy { display: grid; gap: 0.75rem; margin-top: 0.5rem; }
.security-policy h3 { margin: 0; }
.security-policy__grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 0.75rem; }
.security-policy__card { border: 1px solid var(--border-color); background: var(--bg-secondary); border-radius: 10px; padding: 0.85rem; display: grid; gap: 0.35rem; }
.security-policy__card h4 { margin: 0; font-size: 0.9rem; color: var(--text-primary); }
.security-policy__card p { margin: 0; color: var(--text-secondary); font-size: 0.82rem; line-height: 1.5; }
.security-center :is(button, input, select, textarea, [tabindex="0"]):focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.security-section-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.security-section-head h3 { margin: 0; }
.role-editor, .mac-panel { display: grid; gap: 0.9rem; border: 1px solid var(--border-color); border-radius: 12px; padding: 1rem; background: var(--bg-secondary); min-width: 0; }
.role-editor__actions { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.security-filters__reason { flex: 1 1 18rem; }
.permission-groups { display: grid; gap: 1rem; max-height: 34rem; overflow: auto; padding-right: 0.25rem; }
.permission-group { display: grid; gap: 0; }
.permission-group h4 { margin: 0 0 0.4rem; font-size: 0.85rem; color: var(--text-primary); }
.permission-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; padding: 0.65rem 0.7rem; border-top: 1px solid var(--border-color); }
.permission-info { display: grid; gap: 0.2rem; min-width: 0; }
.permission-info code { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 0.78rem; color: var(--accent-text); overflow-wrap: anywhere; }
.permission-info p { margin: 0; color: var(--text-secondary); font-size: 0.8rem; line-height: 1.45; }
.permission-meta { display: flex; flex-wrap: wrap; gap: 0.25rem; }
.permission-actions { display: flex; align-items: flex-start; gap: 0.3rem; flex-shrink: 0; }
.permission-choice { border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-primary); color: var(--text-secondary); padding: 0.3rem 0.55rem; font-size: 0.75rem; font-weight: 600; cursor: pointer; }
.permission-choice--allow { border-color: var(--success); color: var(--success); background: var(--success-bg); }
.permission-choice--deny { border-color: var(--danger); color: var(--danger); background: var(--danger-bg); }
.permission-choice:disabled { opacity: 0.45; cursor: not-allowed; }
.mac-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); gap: 0.65rem; }
.mac-grid label { display: grid; gap: 0.25rem; color: var(--text-secondary); font-size: 0.8rem; }
.mac-grid input, .mac-grid select { width: 100%; padding: 0.45rem 0.55rem; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-primary); color: var(--text-primary); }
.mac-history { display: grid; gap: 0.4rem; }
.mac-history h4 { margin: 0; }

@media (max-width: 760px) {
  .permission-row { flex-direction: column; }
  .permission-actions { align-self: flex-start; }
}
@media (max-width: 760px) {
  .security-summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .security-form__row { grid-template-columns: 1fr; }
  .security-matrix__permission { min-width: 14rem; }
}
@media (prefers-reduced-motion: reduce) {
  .security-center * { transition: none !important; animation: none !important; }
}
</style>
