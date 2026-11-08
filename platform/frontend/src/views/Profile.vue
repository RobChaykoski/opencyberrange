<template>
  <div class="profile-page">
    <div class="profile-container">
      <div v-if="loading" class="loading-message">Loading profile information...</div>

      <div v-else-if="user" class="profile-content">
        <!-- Profile hero: avatar, identity, and completion stats -->
        <section class="profile-hero">
          <div class="profile-avatar">
            <UserAvatar
              :src="avatarPreview"
              :name="displayName"
              :border-style="avatarBorderStyle"
              :border-color="avatarBorderColor"
              :size="118"
              alt="Your profile picture"
            />
            <input
              ref="avatarInput"
              type="file"
              accept="image/png,image/jpeg,image/webp"
              class="avatar-input"
              @change="onAvatarSelected"
            />
            <div class="profile-avatar__actions">
              <button type="button" class="btn btn--secondary btn--sm" :disabled="avatarSaving" @click="chooseAvatar">
                {{ avatarSaving ? 'Saving...' : (avatarPreview ? 'Change photo' : 'Add photo') }}
              </button>
              <button v-if="avatarPreview" type="button" class="btn btn--ghost-danger btn--sm" :disabled="avatarSaving" @click="removeAvatar">
                Remove
              </button>
            </div>

            <div ref="borderMenuRef" class="avatar-border-control">
              <button
                ref="borderTriggerRef"
                type="button"
                class="avatar-border-trigger"
                :aria-expanded="borderMenuOpen"
                aria-controls="avatar-border-menu"
                @click="toggleBorderMenu"
              >
                <span
                  class="avatar-border-trigger__ring"
                  :class="`ring-preview--${avatarBorderStyle}`"
                  :style="{ '--preview-color': currentBorderHex }"
                  aria-hidden="true"
                ></span>
                <span class="avatar-border-trigger__copy">
                  <span class="avatar-border-trigger__label">Avatar border</span>
                  <span class="avatar-border-trigger__value">{{ currentBorderLabel }}</span>
                </span>
                <ChevronIcon class="avatar-border-trigger__chevron" :class="{ 'is-open': borderMenuOpen }" />
              </button>

              <Transition name="border-menu">
                <div
                  v-if="borderMenuOpen"
                  id="avatar-border-menu"
                  class="avatar-border-menu"
                  role="dialog"
                  aria-label="Customize avatar border"
                >
                  <div class="avatar-border-menu__head">
                    <div>
                      <p class="avatar-border-menu__eyebrow">Customize</p>
                      <h2>Avatar border</h2>
                    </div>
                    <button
                      type="button"
                      class="avatar-border-menu__close"
                      aria-label="Close border menu"
                      @click="closeBorderMenu(true)"
                    >
                      <XIcon />
                    </button>
                  </div>

                  <div class="avatar-border-menu__section">
                    <div class="avatar-border-menu__section-head">
                      <span>Style</span>
                      <span>{{ currentStyleLabel }}</span>
                    </div>
                    <div class="avatar-border-styles" role="radiogroup" aria-label="Avatar border style">
                      <label
                        v-for="option in borderStyleOptions"
                        :key="option.value"
                        class="avatar-border-style"
                        :class="{ 'avatar-border-style--active': avatarBorderStyle === option.value }"
                      >
                        <input
                          v-model="avatarBorderStyle"
                          type="radio"
                          name="avatar-border-style"
                          :value="option.value"
                          :disabled="borderSaving"
                          @change="saveAvatarBorder"
                        />
                        <span
                          class="avatar-border-style__ring"
                          :class="`ring-preview--${option.value}`"
                          :style="{ '--preview-color': currentBorderHex }"
                          aria-hidden="true"
                        ></span>
                        <span class="avatar-border-style__label">{{ option.label }}</span>
                        <CheckIcon
                          v-if="avatarBorderStyle === option.value"
                          class="avatar-border-style__check"
                        />
                      </label>
                    </div>
                  </div>

                  <div class="avatar-border-menu__section">
                    <div class="avatar-border-menu__section-head">
                      <span>Colour</span>
                      <span>{{ currentColorLabel }}</span>
                    </div>
                    <div class="avatar-border-colors" role="radiogroup" aria-label="Avatar border colour">
                      <label
                        v-for="option in borderColorOptions"
                        :key="option.value"
                        class="avatar-border-color"
                        :class="{ 'avatar-border-color--active': avatarBorderColor === option.value }"
                      >
                        <input
                          v-model="avatarBorderColor"
                          type="radio"
                          name="avatar-border-colour"
                          :value="option.value"
                          :disabled="borderSaving"
                          @change="saveAvatarBorder"
                        />
                        <span
                          class="avatar-border-color__swatch"
                          :style="{ '--swatch': option.hex }"
                          aria-hidden="true"
                        >
                          <CheckIcon v-if="avatarBorderColor === option.value" />
                        </span>
                        <span class="avatar-border-color__label">{{ option.label }}</span>
                      </label>
                    </div>
                  </div>

                  <div class="avatar-border-menu__foot">
                    <button type="button" class="avatar-border-menu__reset" @click="resetAvatarBorder">
                      Reset
                    </button>
                    <span class="avatar-border-menu__status" aria-live="polite">
                      {{ borderSaving ? 'Saving…' : (borderMessage || 'Changes save automatically') }}
                    </span>
                  </div>
                </div>
              </Transition>
            </div>

            <p v-if="avatarMessage" :class="avatarError ? 'error-message' : 'success-message'" class="avatar-message">
              {{ avatarMessage }}
            </p>
          </div>

          <div class="profile-hero__identity">
            <p class="profile-hero__eyebrow">SWOCTS Cyber Range profile</p>
            <h1 class="profile-hero__name">{{ displayName }}</h1>
            <p class="profile-hero__handle">
              <span>@{{ user.username }}</span>
              <span class="profile-hero__dot">·</span>
              <span>{{ user.email }}</span>
            </p>
            <p v-if="user.organization" class="profile-hero__org">{{ user.organization }}</p>
            <div class="profile-hero__badges">
              <span class="status-badge" :class="roleBadgeClass">{{ roleLabel }}</span>
              <span v-if="user.is_approved" class="status-badge status-badge--approved">Approved</span>
              <span v-else class="status-badge status-badge--pending">Pending approval</span>
              <span
                v-if="summary?.skill_dna?.titles?.equipped"
                class="profile-hero__title"
                :class="`profile-hero__title--${summary.skill_dna.titles.equipped.rarity}`"
              >
                {{ summary.skill_dna.titles.equipped.label }}
              </span>
              <span v-if="user.created_at" class="profile-hero__joined">Member since {{ formatDateOnly(user.created_at) }}</span>
            </div>

            <div v-if="summary" class="profile-hero__progress">
              <div class="profile-hero__progress-head">
                <span>Your learning trail</span>
                <span>{{ summary.totals.labs_completed }} / {{ summary.totals.labs_total }} exercises</span>
              </div>
              <div
                class="profile-hero__progress-bar"
                role="progressbar"
                :aria-valuenow="summary.totals.progress_percent"
                aria-valuemin="0"
                aria-valuemax="100"
                :aria-label="`Overall progress: ${summary.totals.progress_percent}%`"
              >
                <span :style="{ width: summary.totals.progress_percent + '%' }"></span>
              </div>
              <p class="profile-hero__progress-note">{{ progressMessage }}</p>
            </div>
          </div>

          <div class="profile-stats">
            <div class="profile-stat">
              <span class="profile-stat__value">{{ summary ? summary.totals.certificates : '—' }}</span>
              <span class="profile-stat__label">Certificates</span>
            </div>
            <div class="profile-stat">
              <span class="profile-stat__value">
                {{ summary ? summary.totals.labs_completed : '—' }}<small v-if="summary">/{{ summary.totals.labs_total }}</small>
              </span>
              <span class="profile-stat__label">Exercises</span>
            </div>
            <div class="profile-stat">
              <span class="profile-stat__value">{{ summary ? summary.totals.progress_percent : '—' }}<small v-if="summary">%</small></span>
              <span class="profile-stat__label">Complete</span>
            </div>
            <div class="profile-stat">
              <span class="profile-stat__value">{{ summary ? summary.totals.achievements : '—' }}</span>
              <span class="profile-stat__label">Badges</span>
            </div>
          </div>
        </section>

        <nav class="profile-tabs" role="tablist" aria-label="Profile sections">
          <button
            v-for="tab in profileTabs"
            :key="tab.key"
            :id="`profile-tab-${tab.key}`"
            type="button"
            role="tab"
            class="profile-tab"
            :class="{ 'profile-tab--active': activeTab === tab.key }"
            :aria-selected="activeTab === tab.key"
            :aria-controls="`profile-panel-${tab.key}`"
            :tabindex="activeTab === tab.key ? 0 : -1"
            @click="setTab(tab.key)"
            @keydown.left.prevent="moveTab(-1)"
            @keydown.right.prevent="moveTab(1)"
            @keydown.home.prevent="moveTabTo('overview')"
            @keydown.end.prevent="moveTabTo('security')"
          >
            {{ tab.label }}
            <span v-if="tab.count !== undefined" class="profile-tab__count">{{ tab.count }}</span>
          </button>
        </nav>

        <p v-if="summaryLoading && !summary" class="help-text">Loading your profile signals...</p>
        <p v-if="summaryError" class="error-message">{{ summaryError }}</p>

        <div
          v-show="activeTab === 'overview'"
          id="profile-panel-overview"
          class="profile-panel"
          role="tabpanel"
          aria-labelledby="profile-tab-overview"
        >
          <section class="profile-section overview-section" aria-labelledby="overview-title">
            <div class="overview-section__head">
              <div>
                <p class="profile-hero__eyebrow">At a glance</p>
                <h2 id="overview-title" class="section-title">Your profile in four signals</h2>
                <p class="help-text">
                  A short read of where your practice is pointing. Open a tab for the
                  evidence behind it.
                </p>
              </div>
            </div>

            <div class="overview-grid">
              <article class="overview-card overview-card--accent">
                <p class="overview-card__eyebrow">Next practice step</p>
                <h3>{{ topAffinity?.label || 'Start your first exercise' }}</h3>
                <p>{{ topAffinity?.next_step || 'Complete one exercise to give your skill tree its first branch.' }}</p>
                <p v-if="topAffinity?.evidence" class="overview-card__evidence">{{ topAffinity.evidence }}</p>
                <button type="button" class="btn btn--secondary btn--sm" @click="setTab('skill-tree')">
                  Open skill tree
                </button>
              </article>

              <article class="overview-card">
                <p class="overview-card__eyebrow">Learning evidence</p>
                <div class="overview-stat-row">
                  <div><strong>{{ learningHours }}</strong><span>hours</span></div>
                  <div><strong>{{ cleanSolves }}</strong><span>clean solves</span></div>
                  <div><strong>{{ advancedCompletions }}</strong><span>advanced</span></div>
                </div>
                <p>
                  Clean solves are exercises completed with no hints and one attempt.
                  Advanced exercises are marked advanced or expert.
                </p>
              </article>

              <article class="overview-card">
                <p class="overview-card__eyebrow">Cyber DNA</p>
                <div class="overview-dna">
                  <strong>{{ summary?.skill_dna?.class?.class_name || 'Recruit' }}</strong>
                  <span>{{ summary?.skill_dna?.class?.label || 'No class yet' }}</span>
                </div>
                <p v-if="summary?.skill_dna">
                  {{ summary.skill_dna.overall }} / 100 overall, {{ summary.skill_dna.tier }}.
                  Your highest branch is {{ summary.skill_dna.class.label }}.
                </p>
                <p v-else>Complete exercises to build your six branches.</p>
              </article>

              <article class="overview-card">
                <p class="overview-card__eyebrow">Recent recognition</p>
                <div v-if="recentAchievements.length" class="overview-badges">
                  <span v-for="badge in recentAchievements" :key="badge.type + badge.label" class="overview-badge">
                    <span aria-hidden="true">{{ badge.icon }}</span>{{ badge.label }}
                  </span>
                </div>
                <p v-else>No badges yet. Your first completed exercise starts the collection.</p>
                <button type="button" class="btn btn--secondary btn--sm" @click="setTab('learning')">
                  See learning record
                </button>
              </article>
            </div>
          </section>
        </div>

        <div
          v-show="activeTab === 'skill-tree'"
          id="profile-panel-skill-tree"
          class="profile-panel"
          role="tabpanel"
          aria-labelledby="profile-tab-skill-tree"
        >
          <div class="profile-panel__actions">
            <button type="button" class="btn btn--secondary btn--sm" :disabled="careerExporting" @click="downloadCareerProfile('md')">
              Download career profile (Markdown)
            </button>
            <button type="button" class="btn btn--secondary btn--sm" :disabled="careerExporting" @click="downloadCareerProfile('html')">
              Download career profile (printable HTML)
            </button>
          </div>
          <p v-if="careerExportMessage" :class="careerExportError ? 'error-message' : 'success-message'">
            {{ careerExportMessage }}
          </p>
          <SkillDnaProfile
            v-if="summary?.skill_dna"
            :dna="summary.skill_dna"
            :busy="titleSaving"
            @equip-title="equipTitle"
          />
          <p v-else class="help-text">Complete an exercise to grow your skill tree.</p>
          <p
            v-if="titleMessage"
            :class="titleError ? 'error-message' : 'success-message'"
            class="dna-title-message"
          >
            {{ titleMessage }}
          </p>
        </div>

        <div
          v-show="activeTab === 'learning'"
          id="profile-panel-learning"
          class="profile-panel"
          role="tabpanel"
          aria-labelledby="profile-tab-learning"
        >
        <!-- Course achievements: grouped by course so the profile is a summary,
             not a raw badge feed. -->
        <section
          v-if="summary"
          class="profile-section achievements-section"
          aria-labelledby="course-achievements-title"
        >
          <div class="achievements-section__head">
            <div>
              <p class="profile-hero__eyebrow">Recognition</p>
              <h2 id="course-achievements-title" class="section-title">Course achievements</h2>
              <p class="help-text">
                Badges earned through your courses, grouped so progress is easy to scan.
                Event and range-wide awards appear separately.
              </p>
            </div>
            <div class="achievements-section__total">
              <strong>{{ achievements.length }}</strong>
              <span>{{ achievements.length === 1 ? 'badge earned' : 'badges earned' }}</span>
              <button
                type="button"
                class="btn btn--secondary btn--sm"
                :disabled="hiddenAchievementsSaving"
                @click="toggleHiddenAchievements"
              >
                {{ showHiddenAchievements ? 'Hide secret badges' : 'Show secret badges' }}
              </button>
            </div>
          </div>

          <div class="course-achievement-grid">
            <article
              v-for="group in courseAchievements"
              :key="group.course_id"
              class="course-achievement-card"
            >
              <header class="course-achievement-card__head">
                <div>
                  <span class="course-achievement-card__code">{{ group.course_code }}</span>
                  <h3>{{ group.course_name }}</h3>
                </div>
                <span
                  class="course-achievement-card__count"
                  :aria-label="`${group.total_awards} badges in ${group.course_name}`"
                >{{ group.total_awards }}</span>
              </header>
              <div class="course-achievement-card__badges">
                <span
                  v-for="badge in group.badges"
                  :key="badge.type"
                  class="course-achievement-badge"
                  :title="badge.description || badge.label"
                >
                  <span class="course-achievement-badge__icon" aria-hidden="true">{{ badge.icon }}</span>
                  <span>{{ badge.label }}</span>
                  <span v-if="badge.count > 1" class="course-achievement-badge__count">×{{ badge.count }}</span>
                </span>
              </div>
              <footer class="course-achievement-card__foot">
                <span>{{ group.unique_badges }} unique {{ group.unique_badges === 1 ? 'badge' : 'badges' }}</span>
                <span v-if="group.latest_awarded_at">Latest {{ formatDateOnly(group.latest_awarded_at) }}</span>
              </footer>
            </article>

            <article
              v-if="otherAchievementBadges.length"
              class="course-achievement-card course-achievement-card--other"
            >
              <header class="course-achievement-card__head">
                <div>
                  <span class="course-achievement-card__code">Across the range</span>
                  <h3>Events &amp; special badges</h3>
                </div>
                <span class="course-achievement-card__count">{{ otherAchievements.length }}</span>
              </header>
              <div class="course-achievement-card__badges">
                <span
                  v-for="badge in otherAchievementBadges"
                  :key="badge.type"
                  class="course-achievement-badge"
                  :title="badge.description || badge.label"
                >
                  <span class="course-achievement-badge__icon" aria-hidden="true">{{ badge.icon }}</span>
                  <span>{{ badge.label }}</span>
                  <span v-if="badge.count > 1" class="course-achievement-badge__count">×{{ badge.count }}</span>
                </span>
              </div>
              <footer class="course-achievement-card__foot">
                <span>{{ otherAchievementBadges.length }} unique {{ otherAchievementBadges.length === 1 ? 'badge' : 'badges' }}</span>
                <span>Not tied to a course</span>
              </footer>
            </article>
          </div>
        </section>

        <!-- Certificates and printable transcript -->
        <section class="profile-section transcript-section">
          <div class="transcript-head">
            <div>
              <h2 class="section-title">Certificates &amp; completion</h2>
              <p class="help-text transcript-help">
                Certificates are issued when every visible exercise in a level is complete.
                The PDF includes your certificates, every completed exercise, and course achievements.
              </p>
            </div>
            <button type="button" class="btn btn--primary transcript-download" :disabled="downloadingPdf || summaryLoading" @click="downloadTranscript">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ downloadingPdf ? 'Preparing PDF...' : 'Download PDF' }}
            </button>
          </div>

          <p v-if="pdfMessage" :class="pdfError ? 'error-message' : 'success-message'" class="transcript-message">{{ pdfMessage }}</p>
          <p v-if="summaryLoading && !summary" class="help-text">Loading your completion record...</p>

          <template v-if="summary">
            <div v-if="certificates.length" class="certificate-grid">
              <router-link
                v-for="cert in certificates"
                :key="cert.certificate_id"
                :to="`/certificate/${cert.track_slug}/${cert.level_id}`"
                class="certificate-card"
              >
                <span class="certificate-card__seal" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <circle cx="12" cy="9" r="5"/>
                    <path d="M8.5 13.2 7 21l5-2.6L17 21l-1.5-7.8"/>
                  </svg>
                </span>
                <span class="certificate-card__track" :style="{ color: cert.track_color || 'var(--accent)' }">{{ cert.track_name }}</span>
                <span class="certificate-card__title">Level {{ cert.level_number }}: {{ cert.level_name }}</span>
                <span class="certificate-card__meta">
                  Awarded {{ cert.issued_display }} · {{ cert.exercises_completed }} exercises
                  <template v-if="cert.quiz_score !== null && cert.quiz_score !== undefined"> · Quiz {{ cert.quiz_score }}%</template>
                </span>
                <span class="certificate-card__id">{{ cert.certificate_id }}</span>
              </router-link>
            </div>
            <p v-else class="empty-transcript">
              No certificates yet. Finish every exercise in a level and the certificate appears here.
            </p>

            <div v-if="tracks.length" class="profile-tracks">
              <h3 class="subsection-title">Track progress</h3>
              <div v-for="track in tracks" :key="track.track_slug" class="track-progress">
                <div class="track-progress__head">
                  <span class="track-progress__name">{{ track.track_name }}</span>
                  <span class="track-progress__count">{{ track.completed_labs }} / {{ track.total_labs }} exercises</span>
                </div>
                <div class="track-progress__bar" role="progressbar" :aria-label="`${track.track_name} progress`" :aria-valuenow="track.progress_percent" aria-valuemin="0" aria-valuemax="100">
                  <span :style="{ width: track.progress_percent + '%' }"></span>
                </div>
                <div class="track-progress__levels">
                  <div
                    v-for="level in track.levels"
                    :key="level.id"
                    class="level-card"
                    :class="{
                      'level-card--complete': level.is_complete,
                      'level-card--started': level.completed_labs > 0 && !level.is_complete,
                    }"
                  >
                    <div class="level-card__head">
                      <span class="level-card__number">Level {{ level.level_number }}</span>
                      <span class="level-card__status">{{ levelStatus(level) }}</span>
                    </div>
                    <span class="level-card__name">{{ level.level_name }}</span>
                    <div
                      class="level-card__progress"
                      role="progressbar"
                      :aria-valuenow="levelPercent(level)"
                      aria-valuemin="0"
                      aria-valuemax="100"
                      :aria-label="`${level.level_name}: ${level.completed_labs} of ${level.total_labs} exercises complete`"
                    >
                      <span :style="{ width: levelPercent(level) + '%' }"></span>
                    </div>
                    <div class="level-card__foot">
                      <span>{{ level.completed_labs }} / {{ level.total_labs }} exercises</span>
                      <span v-if="level.certificate_id" class="level-card__cert">Certificate</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <details v-if="completions.length" class="completion-details">
              <summary>Completion details ({{ completions.length }})</summary>
              <div class="completion-table-wrap">
                <table class="completion-table" aria-label="Completed exercises">
                  <thead>
                    <tr>
                      <th scope="col">Exercise</th>
                      <th scope="col">Track</th>
                      <th scope="col">Completed</th>
                      <th scope="col">Attempts</th>
                      <th scope="col">Hints</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in completions" :key="item.lab_id">
                      <td>
                        <span class="completion-table__lab">{{ item.lab_name }}</span>
                        <span class="completion-table__level">Level {{ item.level_number }}: {{ item.level_name }}</span>
                      </td>
                      <td>{{ item.track_name }}</td>
                      <td>{{ formatCompletionDate(item.completed_at) }}</td>
                      <td>{{ item.attempts }}</td>
                      <td>{{ item.hints_used }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>
          </template>
        </section>
        </div>

        <div
          v-show="activeTab === 'account'"
          id="profile-panel-account"
          class="profile-panel"
          role="tabpanel"
          aria-labelledby="profile-tab-account"
        >
        <div class="profile-section">
          <h2 class="section-title">Personal Information</h2>
          <p class="help-text" style="margin: -0.5rem 0 1rem;">
            Your first and last name are printed on completion certificates.
            If you leave both blank, your username is used instead.
          </p>

          <form class="name-form" @submit.prevent="saveName">
            <div class="name-grid">
              <div class="form-group">
                <label for="firstName">First name</label>
                <input
                  id="firstName"
                  v-model="nameForm.first_name"
                  type="text"
                  maxlength="80"
                  class="form-input"
                  placeholder="e.g. Alex"
                  autocomplete="given-name"
                />
              </div>
              <div class="form-group">
                <label for="lastName">Last name</label>
                <input
                  id="lastName"
                  v-model="nameForm.last_name"
                  type="text"
                  maxlength="80"
                  class="form-input"
                  placeholder="e.g. Morgan"
                  autocomplete="family-name"
                />
              </div>
              <div class="form-group">
                <label for="organization">Organization <span class="help-text">(optional)</span></label>
                <input
                  id="organization"
                  v-model="nameForm.organization"
                  type="text"
                  maxlength="120"
                  class="form-input"
                  placeholder="e.g. University or team"
                  autocomplete="organization"
                />
              </div>
            </div>

            <p class="help-text certificate-preview">
              Certificates will show:
              <strong>{{ certificateName }}</strong>
            </p>
            <p v-if="nameMessage" :class="nameError ? 'error-message' : 'success-message'" style="margin-top: 0.75rem;">
              {{ nameMessage }}
            </p>
            <button type="submit" :disabled="nameSaving" class="btn btn--primary">
              {{ nameSaving ? 'Saving...' : 'Save name' }}
            </button>
          </form>
        </div>

        <!-- Account Information Section -->
        <div class="profile-section">
          <h2 class="section-title">Account Information</h2>
          
          <div class="info-grid">
            <div class="info-item">
              <label class="info-label">Username</label>
              <div class="info-value">{{ user.username }}</div>
            </div>

            <div class="info-item">
              <label class="info-label">Email</label>
              <div class="info-value">{{ user.email }}</div>
            </div>

            <div class="info-item">
              <label class="info-label">Account Status</label>
              <div class="info-value">
                <span v-if="user.is_approved" class="status-badge status-badge--approved">Approved</span>
                <span v-else class="status-badge status-badge--pending">Pending Approval</span>
              </div>
            </div>

            <div class="info-item">
              <label class="info-label">Account Active</label>
              <div class="info-value">
                <span v-if="user.is_active !== false" class="status-badge status-badge--active">Active</span>
                <span v-else class="status-badge status-badge--inactive">Inactive</span>
              </div>
            </div>

            <div class="info-item" v-if="user.created_at">
              <label class="info-label">Registration Date</label>
              <div class="info-value">{{ formatDate(user.created_at) }}</div>
            </div>

            <div class="info-item">
              <label class="info-label">VPN Registered</label>
              <div class="info-value">
                <!-- Use shared composable logic - same as Dashboard -->
                <span v-if="isVpnRegistered()" class="status-badge status-badge--vpn">Yes</span>
                <span v-else class="status-badge status-badge--no-vpn">No</span>
              </div>
            </div>

            <div class="info-item">
              <label class="info-label">Role</label>
              <div class="info-value">
                <span v-if="user.role === 'admin'" class="status-badge status-badge--admin">Admin</span>
                <span v-else-if="user.role === 'instructor'" class="status-badge status-badge--instructor">Instructor</span>
                <span v-else class="status-badge status-badge--user">Student</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Exercise Studio LLM connections (instructor/admin, editions that ship Studio) -->
        <div class="profile-section" v-if="isInstructor && exerciseAuthoring">
          <h2 class="section-title">Exercise Studio</h2>
          <label class="info-label">LLM provider connections</label>
          <p class="help-text" style="margin: 0.35rem 0 0.85rem;">
            Connect a model to generate exercises. Add more than one and pick a default; the one marked Default is used unless you choose another at generation time. Keys are stored encrypted and never shown again.
          </p>

          <!-- Saved profiles -->
          <div v-if="llm.profiles.length" class="llm-list">
            <div v-for="p in llm.profiles" :key="p.id" class="llm-row">
              <div class="llm-row__main">
                <span class="llm-row__label">{{ p.label }}</span>
                <span class="llm-row__meta">{{ providerLabel(p.provider) }} : {{ p.model || 'default model' }}</span>
                <span v-if="p.base_url" class="llm-row__meta llm-row__url">{{ p.base_url }}</span>
              </div>
              <div class="llm-row__actions">
                <span v-if="p.is_default" class="status-badge status-badge--approved">Default</span>
                <button v-else class="btn btn--secondary btn--sm" @click="makeDefault(p.id)">Make default</button>
                <button class="btn btn--ghost-danger btn--sm" @click="removeProfile(p.id)">Remove</button>
              </div>
            </div>
          </div>
          <p v-else class="help-text" style="margin: 0 0 0.85rem;">No connections yet. Add one below.</p>

          <!-- Add a connection -->
          <div class="llm-add">
            <div class="llm-field">
              <label class="info-label">Provider</label>
              <select aria-label="Provider" v-model="llm.form.provider" class="form-input" @change="onProviderChange">
                <option v-for="c in llm.catalog" :key="c.id" :value="c.id">{{ c.label }}</option>
              </select>
            </div>
            <div class="llm-field" v-if="currentSpec && currentSpec.fields.includes('base_url')">
              <label class="info-label">Endpoint URL</label>
              <input aria-label="Endpoint URL" v-model="llm.form.base_url" type="text" class="form-input" :placeholder="currentSpec.base_url_hint || 'https://...'" />
            </div>
            <div class="llm-field" v-if="currentSpec && currentSpec.fields.includes('api_key')">
              <label class="info-label">API key <span v-if="!currentSpec.needs_key" class="help-text">(optional)</span></label>
              <input v-model="llm.form.api_key" type="password" class="form-input" :placeholder="currentSpec.key_hint || ''" autocomplete="off" />
            </div>
            <div class="llm-field" v-if="currentSpec && currentSpec.fields.includes('model')">
              <label class="info-label">Model</label>
              <input aria-label="Model" v-if="!(currentSpec.models && currentSpec.models.length)" v-model="llm.form.model" type="text" class="form-input" :placeholder="currentSpec.model_hint || currentSpec.default_model || ''" />
              <select v-else v-model="llm.form.model" class="form-input">
                <option v-for="m in currentSpec.models" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="llm-field">
              <label class="info-label">Label <span class="help-text">(optional)</span></label>
              <input v-model="llm.form.label" type="text" class="form-input" placeholder="e.g. My Provider, Lab Ollama" />
            </div>
            <div class="llm-actions">
              <button class="btn btn--secondary" :disabled="llm.testing || llm.saving" @click="testConnection">
                {{ llm.testing ? 'Testing...' : 'Test connection' }}
              </button>
              <button class="btn btn--primary" :disabled="llm.saving" @click="saveProfile">
                {{ llm.saving ? 'Saving...' : 'Save connection' }}
              </button>
            </div>
            <p v-if="llm.testMsg" :class="llm.testOk ? 'success-message' : 'error-message'" style="margin-top: 0.5rem;">{{ llm.testMsg }}</p>
            <p v-if="llm.msg" :class="llm.err ? 'error-message' : 'success-message'" style="margin-top: 0.5rem;">{{ llm.msg }}</p>
          </div>
        </div>

        <!-- Course Enrollment Section -->
        <div class="profile-section">
          <h2 class="section-title">Course Enrollment</h2>

          <div class="join-course-form">
            <label class="info-label">Join a Course</label>
            <div class="join-row">
              <input
                v-model="inviteCode"
                type="text"
                placeholder="Enter invite code"
                class="form-input"
                @keyup.enter="joinCourse"
              />
              <button @click="joinCourse" :disabled="!inviteCode.trim() || joiningCourse" class="btn btn--primary">
                {{ joiningCourse ? 'Joining...' : 'Join' }}
              </button>
            </div>
            <p v-if="joinMessage" :class="joinError ? 'error-message' : 'success-message'" style="margin-top: 0.75rem;">{{ joinMessage }}</p>
          </div>

          <div v-if="enrolledCourses.length > 0" class="enrolled-courses">
            <h4 class="enrolled-courses__title">My Courses</h4>
            <div class="enrolled-courses__list">
              <router-link
                v-for="c in enrolledCourses"
                :key="c.id"
                :to="'/courses/' + c.id"
                class="enrolled-course-card"
              >
                <div class="enrolled-course-card__info">
                  <span class="enrolled-course-card__name">{{ c.name }}</span>
                  <span class="enrolled-course-card__code">{{ c.code }} &mdash; {{ c.semester }}</span>
                </div>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="enrolled-course-card__arrow">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </router-link>
            </div>
          </div>
          <p v-else class="empty-courses">Not enrolled in any courses yet.</p>
        </div>
        </div>

        <div
          v-show="activeTab === 'security'"
          id="profile-panel-security"
          class="profile-panel"
          role="tabpanel"
          aria-labelledby="profile-tab-security"
        >
        <!-- Two-Factor Authentication (TOTP) -->
        <div class="profile-section">
          <h2 class="section-title">Two-Factor Authentication (TOTP)</h2>
          <p class="help-text" style="margin: 0 0 0.85rem;">
            Add a second factor using an authenticator app (Google Authenticator, Authy, 1Password, etc.).
          </p>

          <div v-if="user.mfa_enabled" class="info-grid">
            <div class="info-item">
              <label class="info-label">Status</label>
              <div class="info-value"><span class="status-badge status-badge--approved">Enabled</span></div>
            </div>
          </div>

          <div v-if="!user.mfa_enabled && !mfa.enrolling" class="join-row" style="margin-top: 0.5rem;">
            <button class="btn btn--primary" :disabled="mfa.loading" @click="startMfaEnroll">
              {{ mfa.loading ? 'Starting...' : 'Enable MFA' }}
            </button>
            <p v-if="mfa.error" class="error-message" style="margin-top: 0.5rem;">{{ mfa.error }}</p>
          </div>

          <div v-if="!user.mfa_enabled && mfa.enrolling" style="margin-top: 0.75rem;">
            <p class="help-text">Scan the QR code with your authenticator app, or enter the secret manually:</p>
            <div v-if="mfa.qr" class="mfa-qr-wrap">
              <img :src="mfa.qr" alt="QR code to add this account to an authenticator app" class="mfa-qr" />
              <p class="help-text">Works with Google Authenticator, 1Password, Authy, and similar apps.</p>
            </div>
            <details class="mfa-manual">
              <summary>Can't scan? Enter the secret manually</summary>
              <div class="info-item" style="margin: 0.5rem 0;">
                <label class="info-label">Secret</label>
                <div class="info-value"><code>{{ mfa.secret }}</code></div>
              </div>
              <div class="info-item" style="margin: 0.5rem 0;">
                <label class="info-label">Provisioning URI</label>
                <div class="info-value" style="word-break: break-all;"><code>{{ mfa.uri }}</code></div>
              </div>
            </details>
            <div class="join-row" style="margin-top: 0.75rem;">
              <input v-model="mfa.code" type="text" inputmode="numeric" placeholder="6-digit code" class="form-input" @keyup.enter="verifyMfa" />
              <button class="btn btn--primary" :disabled="mfa.loading || !mfa.code.trim()" @click="verifyMfa">
                {{ mfa.loading ? 'Verifying...' : 'Verify & Enable' }}
              </button>
              <button class="btn btn--secondary" @click="cancelMfaEnroll">Cancel</button>
            </div>
            <p v-if="mfa.error" class="error-message" style="margin-top: 0.5rem;">{{ mfa.error }}</p>
            <p v-if="mfa.success" class="success-message" style="margin-top: 0.5rem;">{{ mfa.success }}</p>
          </div>

          <div v-if="user.mfa_enabled" style="margin-top: 0.75rem;">
            <div class="join-row" style="flex-wrap: wrap;">
              <input v-model="mfa.password" type="password" placeholder="Current password" class="form-input" />
              <input v-model="mfa.code" type="text" inputmode="numeric" placeholder="6-digit code" class="form-input" />
              <button class="btn btn--ghost-danger" :disabled="mfa.loading" @click="disableMfa">
                {{ mfa.loading ? 'Disabling...' : 'Disable MFA' }}
              </button>
            </div>
            <p v-if="mfa.error" class="error-message" style="margin-top: 0.5rem;">{{ mfa.error }}</p>
            <p v-if="mfa.success" class="success-message" style="margin-top: 0.5rem;">{{ mfa.success }}</p>
          </div>
        </div>

        <!-- Password Change Section -->
        <div class="profile-section">
          <h2 class="section-title">Change Password</h2>
          
          <form @submit.prevent="changePassword" class="password-form">
            <div class="form-group">
              <label for="currentPassword">Current Password</label>
              <div class="input-wrapper">
                <input
                  id="currentPassword"
                  v-model="passwordForm.currentPassword"
                  :type="showCurrentPassword ? 'text' : 'password'"
                  placeholder="Enter current password"
                  class="form-input"
                  :class="{ 'error': passwordErrors.currentPassword }"
                  required
                />
                <button
                  type="button"
                  @click="showCurrentPassword = !showCurrentPassword"
                  class="password-toggle"
                  :aria-label="showCurrentPassword ? 'Hide current password' : 'Show current password'"
                  :aria-pressed="showCurrentPassword"
                >
                  <svg v-if="showCurrentPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <p v-if="passwordErrors.currentPassword" class="error-text">{{ passwordErrors.currentPassword }}</p>
            </div>

            <div class="form-group">
              <label for="newPassword">New Password</label>
              <div class="input-wrapper">
                <input
                  id="newPassword"
                  v-model="passwordForm.newPassword"
                  :type="showNewPassword ? 'text' : 'password'"
                  placeholder="Enter new password"
                  class="form-input"
                  :class="{ 'error': passwordErrors.newPassword }"
                  required
                  @blur="validateNewPassword"
                />
                <button
                  type="button"
                  @click="showNewPassword = !showNewPassword"
                  class="password-toggle"
                  :aria-label="showNewPassword ? 'Hide new password' : 'Show new password'"
                  :aria-pressed="showNewPassword"
                >
                  <svg v-if="showNewPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <p v-if="passwordErrors.newPassword" class="error-text">{{ passwordErrors.newPassword }}</p>
              <p v-else-if="passwordForm.newPassword && !passwordErrors.newPassword" class="help-text">
                Password must be at least 8 characters and contain uppercase, lowercase, and a number.
              </p>
            </div>

            <div class="form-group">
              <label for="confirmPassword">Confirm New Password</label>
              <div class="input-wrapper">
                <input
                  id="confirmPassword"
                  v-model="passwordForm.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="Confirm new password"
                  class="form-input"
                  :class="{ 'error': passwordErrors.confirmPassword }"
                  required
                  @blur="validateConfirmPassword"
                />
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="password-toggle"
                  :aria-label="showConfirmPassword ? 'Hide confirmed password' : 'Show confirmed password'"
                  :aria-pressed="showConfirmPassword"
                >
                  <svg v-if="showConfirmPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <p v-if="passwordErrors.confirmPassword" class="error-text">{{ passwordErrors.confirmPassword }}</p>
            </div>

            <p v-if="passwordErrorMessage" class="error-message">{{ passwordErrorMessage }}</p>
            <p v-if="passwordSuccessMessage" class="success-message">{{ passwordSuccessMessage }}</p>

            <button type="submit" :disabled="passwordLoading" class="btn btn--primary">
              <span v-if="passwordLoading">Changing Password...</span>
              <span v-else>Change Password</span>
            </button>
          </form>
        </div>

        <SurveyConsentPanel />
        <PrivacyDataPanel :mfa-enabled="!!user.mfa_enabled" />
        </div>
      </div>

      <div v-else class="error-message">Failed to load profile information</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../api/axios'
import { useVpnStatus } from '../composables/useVpnStatus'
import { usePoll } from '../composables/usePoll'
import { useModules } from '../composables/useModules'
import PrivacyDataPanel from '../components/PrivacyDataPanel.vue'
import SurveyConsentPanel from '../components/SurveyConsentPanel.vue'
import SkillDnaProfile from '../components/SkillDnaProfile.vue'
import UserAvatar from '../components/UserAvatar.vue'
import CheckIcon from '../components/icons/CheckIcon.vue'
import ChevronIcon from '../components/icons/ChevronIcon.vue'
import XIcon from '../components/icons/XIcon.vue'
import { getUserTimeZone } from '../utils/timezone'

const route = useRoute()
const router = useRouter()
const { exerciseAuthoring, fetchModules } = useModules()
const user = ref(null)
const { vpnStatus, fetchVpnStatus, isVpnRegistered } = useVpnStatus()

const mfa = reactive({
  loading: false,
  enrolling: false,
  secret: '',
  uri: '',
  qr: '',
  code: '',
  password: '',
  error: '',
  success: '',
})
const loading = ref(true)

// Completion record (certificates, track progress, achievements) for the hero
// and transcript sections. Loaded separately from /auth/me so the account
// forms render immediately even when that aggregate query is slow.
const summary = ref(null)
const PROFILE_TABS = ['overview', 'skill-tree', 'learning', 'account', 'security']
const activeTab = ref(
  PROFILE_TABS.includes(String(route.query.tab || '')) ? String(route.query.tab) : 'overview'
)

const setTab = (tab) => {
  if (!PROFILE_TABS.includes(tab)) return
  activeTab.value = tab
  const query = { ...route.query, tab }
  if (tab === 'overview') delete query.tab
  router.replace({ query })
  nextTick(() => {
    document.getElementById(`profile-tab-${tab}`)?.scrollIntoView({
      inline: 'nearest',
      block: 'nearest',
      behavior: 'smooth',
    })
  })
}

const moveTabTo = (tab) => {
  setTab(tab)
  nextTick(() => document.getElementById(`profile-tab-${tab}`)?.focus())
}

const moveTab = (direction) => {
  const index = PROFILE_TABS.indexOf(activeTab.value)
  const next = PROFILE_TABS[(index + direction + PROFILE_TABS.length) % PROFILE_TABS.length]
  moveTabTo(next)
}

watch(
  () => route.query.tab,
  (tab) => {
    const next = PROFILE_TABS.includes(String(tab || '')) ? String(tab) : 'overview'
    if (next !== activeTab.value) activeTab.value = next
  }
)
const summaryLoading = ref(true)
const summaryError = ref('')
const titleSaving = ref(false)
const titleMessage = ref('')
const titleError = ref(false)
const downloadingPdf = ref(false)
const pdfMessage = ref('')
const pdfError = ref(false)
const careerExporting = ref(false)
const careerExportMessage = ref('')
const careerExportError = ref(false)

async function downloadCareerProfile(format) {
  if (!['md', 'html'].includes(format) || careerExporting.value) return
  careerExporting.value = true
  careerExportMessage.value = ''
  careerExportError.value = false
  try {
    const response = await axios.get(`/profile/career-dossier.${format}`, {
      responseType: 'blob',
    })
    const type = format === 'html' ? 'text/html;charset=utf-8' : 'text/markdown;charset=utf-8'
    const blob = new Blob([response.data], { type })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `career-profile-${user.value?.username || 'learner'}.${format}`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    careerExportMessage.value = 'Career profile downloaded.'
  } catch (error) {
    careerExportError.value = true
    careerExportMessage.value =
      error.response?.data?.detail || 'Could not prepare the career profile. Please try again.'
  } finally {
    careerExporting.value = false
  }
}

// Profile avatar. Images are resized in the browser and stored on the user row
// as a data URL by /auth/settings, so no upload volume is required.
const avatarInput = ref(null)
const avatarSaving = ref(false)
const avatarMessage = ref('')
const avatarError = ref(false)
const avatarBorderStyle = ref('solid')
const avatarBorderColor = ref('blue')
const borderSaving = ref(false)
const borderMessage = ref('')
const borderMenuOpen = ref(false)
const borderMenuRef = ref(null)
const borderTriggerRef = ref(null)

const borderStyleOptions = [
  { value: 'none', label: 'None' },
  { value: 'solid', label: 'Solid' },
  { value: 'dashed', label: 'Dashed' },
  { value: 'double', label: 'Double' },
  { value: 'glow', label: 'Glow' },
  { value: 'gradient', label: 'Gradient' },
]

const borderColorOptions = [
  { value: 'blue', label: 'Blue', hex: '#3b82f6' },
  { value: 'violet', label: 'Violet', hex: '#8b5cf6' },
  { value: 'emerald', label: 'Emerald', hex: '#10b981' },
  { value: 'amber', label: 'Amber', hex: '#f59e0b' },
  { value: 'rose', label: 'Rose', hex: '#f43f5e' },
  { value: 'cyan', label: 'Cyan', hex: '#06b6d4' },
  { value: 'slate', label: 'Slate', hex: '#64748b' },
  { value: 'gold', label: 'Gold', hex: '#d4a017' },
]

const currentColorOption = computed(
  () => borderColorOptions.find((option) => option.value === avatarBorderColor.value)
    || borderColorOptions[0]
)
const currentStyleOption = computed(
  () => borderStyleOptions.find((option) => option.value === avatarBorderStyle.value)
    || borderStyleOptions[1]
)
const currentBorderHex = computed(() => currentColorOption.value.hex)
const currentColorLabel = computed(() => currentColorOption.value.label)
const currentStyleLabel = computed(() => currentStyleOption.value.label)
const currentBorderLabel = computed(
  () => `${currentStyleLabel.value} · ${currentColorLabel.value}`
)

const closeBorderMenu = (returnFocus = false) => {
  borderMenuOpen.value = false
  if (returnFocus) {
    borderTriggerRef.value?.focus()
  }
}

const toggleBorderMenu = () => {
  borderMenuOpen.value = !borderMenuOpen.value
}

const handleBorderMenuPointer = (event) => {
  if (!borderMenuOpen.value) return
  if (borderMenuRef.value && !borderMenuRef.value.contains(event.target)) {
    closeBorderMenu()
  }
}

const handleBorderMenuKeydown = (event) => {
  if (event.key === 'Escape' && borderMenuOpen.value) {
    event.stopPropagation()
    closeBorderMenu(true)
  }
}

const syncAvatarBorder = (source) => {
  if (!source) return
  avatarBorderStyle.value = source.avatar_border_style || 'solid'
  avatarBorderColor.value = source.avatar_border_color || 'blue'
}

async function saveAvatarBorder() {
  if (borderSaving.value) return
  borderSaving.value = true
  borderMessage.value = ''
  try {
    await axios.put('/auth/settings', {
      avatar_border_style: avatarBorderStyle.value,
      avatar_border_color: avatarBorderColor.value,
    })
    if (user.value) {
      user.value.avatar_border_style = avatarBorderStyle.value
      user.value.avatar_border_color = avatarBorderColor.value
    }
    if (summary.value?.user) {
      summary.value.user.avatar_border_style = avatarBorderStyle.value
      summary.value.user.avatar_border_color = avatarBorderColor.value
    }
    borderMessage.value = 'Saved'
  } catch (error) {
    borderMessage.value = responseMessage(error, 'Could not save your avatar border.')
    syncAvatarBorder(user.value)
  } finally {
    borderSaving.value = false
  }
}

function resetAvatarBorder() {
  avatarBorderStyle.value = 'solid'
  avatarBorderColor.value = 'blue'
  saveAvatarBorder()
}

const displayName = computed(() => {
  if (!user.value) return ''
  const parts = [user.value.first_name, user.value.last_name].filter(part => part && part.trim())
  return parts.length ? parts.join(' ') : user.value.username
})

const levelPercent = (level) => {
  const total = Number(level?.total_labs) || 0
  const done = Number(level?.completed_labs) || 0
  return total ? Math.round((done / total) * 100) : 0
}

const levelStatus = (level) => {
  if (level?.is_complete) return 'Complete'
  return Number(level?.completed_labs) > 0 ? 'In progress' : 'Not started'
}

const avatarPreview = computed(() => user.value?.avatar_data || '')

const roleLabel = computed(() => {
  if (user.value?.role === 'admin') return 'Admin'
  if (user.value?.role === 'instructor') return 'Instructor'
  return 'Student'
})

const roleBadgeClass = computed(() => ({
  'status-badge--admin': user.value?.role === 'admin',
  'status-badge--instructor': user.value?.role === 'instructor',
  'status-badge--user': !['admin', 'instructor'].includes(user.value?.role),
}))

const certificates = computed(() => summary.value?.certificates || [])

const progressMessage = computed(() => {
  const percent = summary.value?.totals?.progress_percent ?? 0
  if (percent >= 100) return 'Every visible exercise is complete. Excellent work.'
  if (percent >= 75) return 'Strong run. The finish line is close.'
  if (percent >= 50) return 'More than halfway there. Keep the momentum going.'
  if (percent >= 25) return 'You are building a solid rhythm.'
  if (percent > 0) return 'Your first steps are in. Keep going.'
  return 'Your first exercise is waiting when you are ready.'
})
const tracks = computed(() => summary.value?.tracks || [])
const completions = computed(() => summary.value?.completions || [])
const achievements = computed(() => summary.value?.achievements || [])
const courseAchievements = computed(() => summary.value?.course_achievements || [])

const profileTabs = computed(() => [
  { key: 'overview', label: 'Overview' },
  { key: 'skill-tree', label: 'Skill tree' },
  { key: 'learning', label: 'Learning record', count: achievements.value.length || undefined },
  { key: 'account', label: 'Account' },
  { key: 'security', label: 'Security & privacy' },
])

const learningMinutes = computed(() =>
  completions.value.reduce((total, item) => total + (Number(item.time_spent_minutes) || 0), 0)
)
const learningHours = computed(() => {
  const hours = learningMinutes.value / 60
  return Number.isInteger(hours) ? String(hours) : hours.toFixed(1)
})
const cleanSolves = computed(() =>
  completions.value.filter(
    (item) => (item.hints_used || 0) === 0 && (item.attempts || 1) <= 1
  ).length
)
const advancedCompletions = computed(() =>
  completions.value.filter((item) =>
    ['advanced', 'expert'].includes(String(item.difficulty || '').toLowerCase())
  ).length
)
const topAffinity = computed(() => {
  const affinities = summary.value?.skill_dna?.affinities || []
  return affinities.find((item) => item.recommended) || affinities[0] || null
})
const recentAchievements = computed(() => achievements.value.slice(0, 4))
const showHiddenAchievements = computed(
  () => !!user.value?.show_hidden_achievements
)
const hiddenAchievementsSaving = ref(false)

async function toggleHiddenAchievements() {
  if (hiddenAchievementsSaving.value) return
  hiddenAchievementsSaving.value = true
  try {
    const next = !showHiddenAchievements.value
    await axios.put('/auth/settings', { show_hidden_achievements: next })
    if (user.value) user.value.show_hidden_achievements = next
    await fetchSummary()
  } finally {
    hiddenAchievementsSaving.value = false
  }
}
const otherAchievements = computed(
  () => achievements.value.filter((item) => !item.course_id)
)
const otherAchievementBadges = computed(() => {
  const grouped = new Map()
  for (const item of otherAchievements.value) {
    const entry = grouped.get(item.type) || {
      type: item.type,
      label: item.label,
      icon: item.icon,
      description: item.description,
      count: 0,
    }
    entry.count += 1
    grouped.set(item.type, entry)
  }
  return [...grouped.values()].sort(
    (a, b) => b.count - a.count || a.label.localeCompare(b.label)
  )
})

// Personal information shown on certificates
const nameForm = reactive({ first_name: '', last_name: '', organization: '' })
const nameSaving = ref(false)
const nameMessage = ref('')
const nameError = ref(false)

const certificateName = computed(() => {
  const parts = [nameForm.first_name.trim(), nameForm.last_name.trim()].filter(Boolean)
  return parts.length ? parts.join(' ') : (user.value?.username || '')
})

const saveName = async () => {
  if (nameSaving.value) return
  nameSaving.value = true
  nameMessage.value = ''
  nameError.value = false
  // Empty strings are deliberate: the settings endpoint treats null as
  // "leave unchanged", while "" clears a previously saved name.
  const payload = {
    first_name: nameForm.first_name.trim(),
    last_name: nameForm.last_name.trim(),
    organization: nameForm.organization.trim(),
  }
  try {
    await axios.put('/auth/settings', payload)
    if (user.value) {
      user.value.first_name = payload.first_name || null
      user.value.last_name = payload.last_name || null
      user.value.organization = payload.organization || null
    }
    // Keep the cached login object in sync so other views see the new name.
    const cached = JSON.parse(localStorage.getItem('user') || '{}')
    cached.first_name = payload.first_name || null
    cached.last_name = payload.last_name || null
    cached.organization = payload.organization || null
    localStorage.setItem('user', JSON.stringify(cached))
    nameMessage.value = (payload.first_name || payload.last_name)
      ? 'Name saved. It will appear on your certificates.'
      : 'Name cleared. Certificates will use your username.'
    if (window.__updateAuthState) window.__updateAuthState()
  } catch (e) {
    nameError.value = true
    nameMessage.value = e.response?.data?.detail || 'Failed to save your name. Please try again.'
  } finally {
    nameSaving.value = false
  }
}

function responseMessage(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail) && detail.length) return detail[0]?.msg || fallback
  return fallback
}

function chooseAvatar() {
  avatarInput.value?.click()
}

function resizeAvatar(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('Could not read that image.'))
    reader.onload = () => {
      const image = new Image()
      image.onerror = () => reject(new Error('That file is not a readable image.'))
      image.onload = () => {
        const maxSize = 320
        const scale = Math.min(1, maxSize / Math.max(image.width, image.height))
        const width = Math.max(1, Math.round(image.width * scale))
        const height = Math.max(1, Math.round(image.height * scale))
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const context = canvas.getContext('2d')
        // JPEG has no alpha; fill white so transparent PNGs do not turn black.
        context.fillStyle = '#ffffff'
        context.fillRect(0, 0, width, height)
        context.drawImage(image, 0, 0, width, height)
        resolve(canvas.toDataURL('image/jpeg', 0.86))
      }
      image.src = reader.result
    }
    reader.readAsDataURL(file)
  })
}

async function onAvatarSelected(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  if (!/^image\/(png|jpeg|webp)$/.test(file.type)) {
    avatarError.value = true
    avatarMessage.value = 'Choose a PNG, JPEG, or WebP image.'
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    avatarError.value = true
    avatarMessage.value = 'Choose an image smaller than 10 MB.'
    return
  }

  avatarSaving.value = true
  avatarMessage.value = ''
  avatarError.value = false
  try {
    const dataUrl = await resizeAvatar(file)
    await axios.put('/auth/settings', { avatar_data: dataUrl })
    if (user.value) user.value.avatar_data = dataUrl
    if (summary.value?.user) summary.value.user.avatar_data = dataUrl
    avatarMessage.value = 'Profile photo updated.'
  } catch (error) {
    avatarError.value = true
    avatarMessage.value = responseMessage(error, 'Could not save your profile photo.')
  } finally {
    avatarSaving.value = false
  }
}

async function removeAvatar() {
  if (avatarSaving.value) return
  avatarSaving.value = true
  avatarMessage.value = ''
  avatarError.value = false
  try {
    await axios.put('/auth/settings', { avatar_data: '' })
    if (user.value) user.value.avatar_data = null
    if (summary.value?.user) summary.value.user.avatar_data = null
    avatarMessage.value = 'Profile photo removed.'
  } catch (error) {
    avatarError.value = true
    avatarMessage.value = responseMessage(error, 'Could not remove your profile photo.')
  } finally {
    avatarSaving.value = false
  }
}

async function fetchSummary() {
  summaryLoading.value = true
  summaryError.value = ''
  try {
    const { data } = await axios.get('/profile/summary')
    summary.value = data
    if (user.value && data.user) {
      if (data.user.avatar_data) user.value.avatar_data = data.user.avatar_data
      user.value.organization = data.user.organization
      user.value.avatar_border_style = data.user.avatar_border_style
      user.value.avatar_border_color = data.user.avatar_border_color
      syncAvatarBorder(data.user)
    }
  } catch (error) {
    summaryError.value = responseMessage(error, 'Could not load your completion record.')
  } finally {
    summaryLoading.value = false
  }
}

async function equipTitle(key) {
  if (titleSaving.value) return
  titleSaving.value = true
  titleMessage.value = ''
  titleError.value = false
  try {
    await axios.put('/profile/title', { title: key })
    await fetchSummary()
    titleMessage.value = key
      ? 'Title equipped.'
      : 'Title cleared. Your class title is showing again.'
  } catch (error) {
    titleError.value = true
    titleMessage.value = responseMessage(error, 'Could not update your title.')
  } finally {
    titleSaving.value = false
  }
}

async function downloadTranscript() {
  if (downloadingPdf.value) return
  downloadingPdf.value = true
  pdfMessage.value = ''
  pdfError.value = false
  try {
    const response = await axios.get('/profile/transcript.pdf', { responseType: 'blob' })
    const blob = response.data instanceof Blob
      ? response.data
      : new Blob([response.data], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `SWOCTS-Cyber-Range-Transcript-${user.value?.username || 'profile'}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
    pdfMessage.value = 'Your transcript PDF was downloaded.'
  } catch (error) {
    pdfError.value = true
    pdfMessage.value = responseMessage(error, 'Could not generate the transcript PDF.')
  } finally {
    downloadingPdf.value = false
  }
}

const formatDateOnly = (dateStr) => {
  if (!dateStr) return '—'
  const value = dateStr.endsWith('Z') || dateStr.includes('+') ? dateStr : dateStr + 'Z'
  return new Date(value).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

const formatCompletionDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

// Exercise Studio LLM connections (instructor/admin)
const isInstructor = computed(() => ['instructor', 'admin'].includes(user.value?.role))
const llm = reactive({
  profiles: [], catalog: [],
  form: { provider: 'custom', base_url: '', api_key: '', model: '', label: '' },
  saving: false, testing: false, msg: '', err: false, testMsg: '', testOk: false,
})
const currentSpec = computed(() => llm.catalog.find(c => c.id === llm.form.provider) || null)
function providerLabel(id) { const c = llm.catalog.find(x => x.id === id); return c ? c.label.split(' (')[0] : id }
function onProviderChange() {
  const s = currentSpec.value
  llm.form.base_url = s?.default_base_url || ''
  llm.form.api_key = ''
  llm.form.model = s?.default_model || (s?.models && s.models[0]) || ''
  llm.testMsg = ''; llm.msg = ''
}
async function loadStudioLlm() {
  // Exercise Studio is not in every edition; without it these routes 404 and
  // the LLM provider panel is dead controls.
  if (!exerciseAuthoring.value) { llm.profiles = []; llm.catalog = []; return }
  try {
    const r = await axios.get('/studio/providers')
    llm.profiles = r.data.profiles || []
    llm.catalog = r.data.catalog || []
    if (!currentSpec.value && llm.catalog.length) llm.form.provider = llm.catalog[0].id
    onProviderChange()
  } catch { llm.profiles = []; llm.catalog = [] }
}
function _formPayload() {
  return {
    provider: llm.form.provider,
    label: llm.form.label.trim() || null,
    base_url: llm.form.base_url.trim() || null,
    model: llm.form.model.trim() || null,
    api_key: llm.form.api_key.trim() || null,
  }
}
async function testConnection() {
  llm.testing = true; llm.testMsg = ''; llm.msg = ''
  try {
    const r = await axios.post('/studio/providers/test', _formPayload())
    llm.testOk = !!r.data.ok
    llm.testMsg = (r.data.ok ? 'OK: ' : 'Failed: ') + (r.data.detail || '')
      + (r.data.models && r.data.models.length ? ' (' + r.data.models.slice(0, 8).join(', ') + ')' : '')
  } catch (e) {
    llm.testOk = false; llm.testMsg = e.response?.data?.detail || 'Could not reach the test endpoint.'
  } finally { llm.testing = false }
}
async function saveProfile() {
  llm.saving = true; llm.msg = ''
  try {
    await axios.post('/studio/providers', { ..._formPayload(), make_default: llm.profiles.length === 0 })
    llm.form.api_key = ''; llm.form.label = ''
    llm.msg = 'Connection saved.'; llm.err = false; llm.testMsg = ''
    await loadStudioLlm()
  } catch (e) {
    llm.msg = e.response?.data?.detail || 'Could not save the connection.'; llm.err = true
  } finally { llm.saving = false }
}
async function makeDefault(id) {
  try { const r = await axios.post(`/studio/providers/${id}/default`); llm.profiles = r.data.profiles || llm.profiles }
  catch (e) { llm.msg = e.response?.data?.detail || 'Could not set default.'; llm.err = true }
}
async function removeProfile(id) {
  try { const r = await axios.delete(`/studio/providers/${id}`); llm.profiles = r.data.profiles || [] }
  catch (e) { llm.msg = e.response?.data?.detail || 'Could not remove the connection.'; llm.err = true }
}

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordErrors = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// Course enrollment
const inviteCode = ref('')
const joiningCourse = ref(false)
const joinMessage = ref('')
const joinError = ref(false)
const enrolledCourses = ref([])

const fetchEnrolledCourses = async () => {
  try {
    const res = await axios.get('/courses/')
    enrolledCourses.value = res.data.courses || []
  } catch (e) {
    console.error('Failed to fetch courses:', e)
  }
}

const joinCourse = async () => {
  if (!inviteCode.value.trim() || joiningCourse.value) return
  joiningCourse.value = true
  joinMessage.value = ''
  joinError.value = false
  try {
    const res = await axios.post('/courses/join', { invite_code: inviteCode.value.trim() })
    joinMessage.value = res.data.message || 'Successfully enrolled!'
    joinError.value = false
    inviteCode.value = ''
    fetchEnrolledCourses()
  } catch (e) {
    joinMessage.value = e.response?.data?.detail || 'Failed to join course'
    joinError.value = true
  } finally {
    joiningCourse.value = false
  }
}

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const passwordLoading = ref(false)
const passwordErrorMessage = ref('')
const passwordSuccessMessage = ref('')

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr.endsWith('Z') || dateStr.includes('+') ? dateStr : dateStr + 'Z')
  return d.toLocaleString('en-US', { timeZone: getUserTimeZone() })
}

const validateNewPassword = () => {
  passwordErrors.newPassword = ''
  if (!passwordForm.newPassword) return
  
  if (passwordForm.newPassword.length < 8) {
    passwordErrors.newPassword = 'Password must be at least 8 characters'
    return
  }
  if (!/[A-Z]/.test(passwordForm.newPassword)) {
    passwordErrors.newPassword = 'Password must contain at least one uppercase letter'
    return
  }
  if (!/[a-z]/.test(passwordForm.newPassword)) {
    passwordErrors.newPassword = 'Password must contain at least one lowercase letter'
    return
  }
  if (!/[0-9]/.test(passwordForm.newPassword)) {
    passwordErrors.newPassword = 'Password must contain at least one number'
    return
  }
}

const validateConfirmPassword = () => {
  passwordErrors.confirmPassword = ''
  if (!passwordForm.confirmPassword) return
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = 'Passwords do not match'
  }
}

const changePassword = async () => {
  passwordErrorMessage.value = ''
  passwordSuccessMessage.value = ''
  
  // Validate
  validateNewPassword()
  validateConfirmPassword()
  
  if (passwordErrors.newPassword || passwordErrors.confirmPassword) {
    return
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordErrorMessage.value = 'Passwords do not match'
    return
  }
  
  passwordLoading.value = true
  
  try {
    await axios.post('/auth/change-password', {
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword,
      confirm_password: passwordForm.confirmPassword
    })
    
    passwordSuccessMessage.value = 'Password changed successfully! Please sign in again.'
    
    // Clear form
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    
    // The backend revokes every outstanding token after a password change.
    // Drop the invalid local session and return to the login page.
    localStorage.removeItem('token')
    localStorage.removeItem('user')

    // Trigger App.vue reactivity update
    if (window.__updateAuthState) {
      window.__updateAuthState()
    }

    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error) {
    if (error.response?.data?.detail) {
      passwordErrorMessage.value = error.response.data.detail
    } else {
      passwordErrorMessage.value = 'Failed to change password. Please try again.'
    }
  } finally {
    passwordLoading.value = false
  }
}

// fetchVpnStatus is now provided by useVpnStatus composable

const startMfaEnroll = async () => {
  mfa.loading = true
  mfa.error = ''
  mfa.success = ''
  try {
    const r = await axios.post('/auth/mfa/enroll')
    mfa.secret = r.data.secret
    mfa.uri = r.data.provisioning_uri
    mfa.qr = r.data.qr_data_url || ''
    mfa.enrolling = true
  } catch (e) {
    mfa.error = e.response?.data?.detail || 'Failed to start MFA enrollment'
  } finally {
    mfa.loading = false
  }
}

const cancelMfaEnroll = () => {
  mfa.enrolling = false
  mfa.secret = ''
  mfa.uri = ''
  mfa.qr = ''
  mfa.code = ''
  mfa.error = ''
}

const verifyMfa = async () => {
  mfa.loading = true
  mfa.error = ''
  mfa.success = ''
  try {
    const response = await axios.post('/auth/mfa/verify', { code: mfa.code.trim() })
    if (user.value) user.value.mfa_enabled = response.data?.mfa_enabled !== false
    mfa.success = 'MFA enabled successfully.'
    mfa.enrolling = false
    mfa.qr = ''
    mfa.code = ''
    await fetchUserInfo()
  } catch (e) {
    mfa.error = e.response?.data?.detail || 'Invalid MFA code'
  } finally {
    mfa.loading = false
  }
}

const disableMfa = async () => {
  mfa.loading = true
  mfa.error = ''
  mfa.success = ''
  try {
    const response = await axios.post('/auth/mfa/disable', { password: mfa.password, code: mfa.code.trim() })
    if (user.value) user.value.mfa_enabled = response.data?.mfa_enabled === true
    mfa.success = 'MFA disabled.'
    mfa.password = ''
    mfa.code = ''
    await fetchUserInfo()
  } catch (e) {
    mfa.error = e.response?.data?.detail || 'Failed to disable MFA'
  } finally {
    mfa.loading = false
  }
}

const fetchUserInfo = async () => {
  try {
    const [userResponse] = await Promise.all([
      axios.get('/auth/me'),
      fetchVpnStatus() // Fetch VPN status in parallel using shared composable
    ])
    user.value = userResponse.data
    syncAvatarBorder(user.value)
    nameForm.first_name = user.value?.first_name || ''
    nameForm.last_name = user.value?.last_name || ''
    nameForm.organization = user.value?.organization || ''
    if (['instructor', 'admin'].includes(user.value?.role)) {
      await fetchModules()
      loadStudioLlm()
    }
  } catch (error) {
    console.error('Failed to fetch user info:', error)
  } finally {
    loading.value = false
  }
}

// Refresh VPN status every 10 seconds to match Dashboard behavior. usePoll
// pauses while the tab is hidden and refreshes immediately on return, which
// replaces the old visibilitychange handler.
//
// Returning to a hidden tab fires visibilitychange (usePoll refreshes) and
// then focus, so the focus handler skips a fetch that just ran to avoid a
// duplicate request.
let lastVpnRefresh = 0
const refreshVpnStatus = () => {
  lastVpnRefresh = Date.now()
  fetchVpnStatus()
}
const onWindowFocus = () => {
  if (Date.now() - lastVpnRefresh < 1000) return
  refreshVpnStatus()
}
usePoll(refreshVpnStatus, 10000)

onMounted(() => {
  fetchUserInfo()
  fetchSummary()
  fetchEnrolledCourses()
  nextTick(() => {
    document.getElementById(`profile-tab-${activeTab.value}`)?.scrollIntoView({
      inline: 'nearest',
      block: 'nearest',
    })
  })

  // Window focus covers clicking back into the browser from another app,
  // which does not fire visibilitychange (the tab was never hidden).
  window.addEventListener('focus', onWindowFocus)
  document.addEventListener('pointerdown', handleBorderMenuPointer)
  document.addEventListener('keydown', handleBorderMenuKeydown)
})

// Cleanup on unmount
onUnmounted(() => {
  window.removeEventListener('focus', onWindowFocus)
  document.removeEventListener('pointerdown', handleBorderMenuPointer)
  document.removeEventListener('keydown', handleBorderMenuKeydown)
})

// Watch for route changes (when navigating to profile page)
watch(() => route.path, (newPath) => {
  if (newPath === '/profile') {
    // Refresh VPN status when navigating to profile page
    // Add small delay to ensure any pending VPN registrations complete
    setTimeout(() => {
      fetchVpnStatus()
    }, 500)
  }
}, { immediate: true })
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 64px);
  padding: 2rem;
  background: var(--bg-primary);
}

.profile-container {
  max-width: 1080px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2rem;
}

.loading-message {
  color: var(--text-secondary);
  text-align: center;
  padding: 2rem;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.profile-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 0 0.25rem;
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
  scrollbar-width: thin;
}

.profile-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.7rem 0.85rem;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: 6px 6px 0 0;
  background: transparent;
  color: var(--text-secondary);
  font: inherit;
  font-size: 0.8125rem;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
}

.profile-tab:hover {
  color: var(--text-primary);
  background: var(--hover-bg);
}

.profile-tab--active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.profile-tab:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.profile-tab__count {
  min-width: 1.35rem;
  padding: 0.05rem 0.35rem;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent);
  font-size: 0.6875rem;
  text-align: center;
}

.profile-panel {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.profile-panel__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.overview-section__head {
  margin-bottom: 1rem;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.85rem;
}

.overview-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.overview-card--accent {
  border-color: var(--accent);
  box-shadow: inset 0 0 0 1px var(--accent);
}

.overview-card__eyebrow {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.overview-card h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.35;
}

.overview-card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.5;
}

.overview-card__evidence {
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.overview-card .btn {
  align-self: flex-start;
  margin-top: auto;
}

.overview-stat-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
}

.overview-stat-row div {
  min-width: 0;
  padding: 0.55rem;
  border-radius: 8px;
  background: var(--bg-secondary);
}

.overview-stat-row strong {
  display: block;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-variant-numeric: tabular-nums;
}

.overview-stat-row span {
  color: var(--text-muted);
  font-size: 0.68rem;
}

.overview-dna {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.overview-dna strong {
  color: var(--text-primary);
  font-size: 1.1rem;
}

.overview-dna span {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.overview-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.overview-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.profile-section {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.info-value {
  font-size: 1rem;
  color: var(--text-primary);
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
}

.status-badge--approved {
  background: rgba(34, 197, 94, 0.15);
  color: #10b981;
  border: 1px solid #10b981;
}

.status-badge--pending {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
  border: 1px solid var(--warning);
}

.status-badge--active {
  background: rgba(34, 197, 94, 0.15);
  color: #10b981;
  border: 1px solid #10b981;
}

.status-badge--inactive {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
  border: 1px solid var(--danger);
}

.status-badge--vpn {
  background: rgba(34, 197, 94, 0.15);
  color: #10b981;
  border: 1px solid #10b981;
}

.status-badge--no-vpn {
  background: rgba(100, 116, 139, 0.15);
  color: var(--text-muted);
  border: 1px solid var(--text-muted);
}

.status-badge--admin {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border: 1px solid #8b5cf6;
}

.status-badge--instructor {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid var(--accent);
}

.status-badge--user {
  background: rgba(148, 163, 184, 0.15);
  color: var(--text-secondary);
  border: 1px solid var(--text-secondary);
}

.name-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.name-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.name-form .form-input {
  padding-right: 1rem;
}

.certificate-preview {
  margin: 0.25rem 0 0;
}

.certificate-preview strong {
  color: var(--text-primary);
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #e2e8f0;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}

.form-input.error {
  border-color: #dc2626;
}

.form-input::placeholder {
  color: var(--text-muted);
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  transition: color 0.2s ease;
}

.password-toggle:hover {
  color: var(--text-primary);
}

.password-toggle svg {
  width: 20px;
  height: 20px;
}

.help-text {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.error-text {
  font-size: 0.8125rem;
  color: #dc2626;
  margin-top: 0.25rem;
}

.error-message {
  font-size: 0.875rem;
  color: #dc2626;
  padding: 0.75rem;
  background: rgba(220, 38, 38, 0.1);
  border-radius: 6px;
  border: 1px solid #dc2626;
}

.success-message {
  font-size: 0.875rem;
  color: #10b981;
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 6px;
  border: 1px solid #10b981;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  align-self: flex-start;
}

.btn--primary {
  background: var(--accent);
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn--primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.key-connected {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.key-connected .btn {
  align-self: auto;
}

.btn--secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn--secondary:hover {
  background: var(--nav-label);
}

.btn--ghost-danger {
  background: transparent;
  color: var(--danger);
  border: 1px solid var(--danger);
}

.btn--ghost-danger:hover {
  background: var(--danger-bg);
}

.btn--sm {
  padding: 0.3rem 0.7rem;
  font-size: 0.82rem;
}

/* LLM provider connections */
.llm-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.llm-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.6rem 0.8rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.llm-row__main {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.llm-row__label {
  font-weight: 600;
  color: var(--text-primary);
}

.llm-row__meta {
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.llm-row__url {
  font-family: monospace;
  word-break: break-all;
}

.llm-row__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.llm-add {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.08));
}

.llm-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.llm-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

/* Course Enrollment */
.join-course-form {
  margin-bottom: 1.5rem;
}

.join-row {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.join-row .form-input {
  flex: 1;
  max-width: 320px;
}

.join-row .btn {
  white-space: nowrap;
}

.enrolled-courses {
  margin-top: 1.5rem;
}

.enrolled-courses__title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

.enrolled-courses__list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.enrolled-course-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.15s;
}

.enrolled-course-card:hover {
  border-color: var(--accent);
  background: rgba(59, 130, 246, 0.05);
}

.enrolled-course-card__info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.enrolled-course-card__name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.enrolled-course-card__code {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.enrolled-course-card__arrow {
  width: 16px;
  height: 16px;
  color: var(--nav-label);
  flex-shrink: 0;
}

.empty-courses {
  color: var(--nav-label);
  font-size: 0.875rem;
  margin-top: 1rem;
}

/* ------------------------------------------------------------------ */
/* Profile hero                                                        */
/* ------------------------------------------------------------------ */

.profile-hero {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 1.75rem;
  padding: 1.75rem;
  border-radius: 18px;
  border: 1px solid var(--border-color);
  background:
    radial-gradient(circle at 8% 18%, rgba(59, 130, 246, 0.18), transparent 42%),
    radial-gradient(circle at 92% 82%, rgba(139, 92, 246, 0.14), transparent 46%),
    var(--bg-secondary);
  box-shadow: 0 18px 45px rgba(2, 6, 23, 0.18);
  overflow: visible;
}

.profile-hero::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  border-radius: 18px 18px 0 0;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #f59e0b);
}

.profile-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
  width: 200px;
}

.avatar-border-control {
  position: relative;
  width: 100%;
}

.avatar-border-trigger {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  width: 100%;
  padding: 0.45rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.avatar-border-trigger:hover {
  border-color: color-mix(in srgb, var(--accent) 55%, var(--border-color));
}

.avatar-border-trigger[aria-expanded="true"] {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}

.avatar-border-trigger__ring {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-tertiary);
}

.avatar-border-trigger__copy {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
  line-height: 1.2;
}

.avatar-border-trigger__label {
  color: var(--text-muted);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.avatar-border-trigger__value {
  overflow: hidden;
  color: var(--text-primary);
  font-size: 0.72rem;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.avatar-border-trigger__chevron {
  flex-shrink: 0;
  width: 14px;
  height: 14px;
  color: var(--text-muted);
  transition: transform 0.15s ease;
}

.avatar-border-trigger__chevron.is-open {
  transform: rotate(180deg);
}

.avatar-border-menu {
  position: absolute;
  top: 0;
  left: calc(100% + 0.8rem);
  z-index: 30;
  width: min(330px, calc(100vw - 3rem));
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  background: var(--bg-secondary);
  box-shadow: 0 20px 55px rgba(2, 6, 23, 0.38);
}

.avatar-border-menu__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.9rem;
}

.avatar-border-menu__eyebrow {
  margin: 0 0 0.1rem;
  color: var(--accent);
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.avatar-border-menu__head h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.05rem;
  letter-spacing: -0.01em;
}

.avatar-border-menu__close {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.avatar-border-menu__close:hover,
.avatar-border-menu__close:focus-visible {
  border-color: var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
}

.avatar-border-menu__close svg {
  width: 14px;
  height: 14px;
}

.avatar-border-menu__section + .avatar-border-menu__section {
  margin-top: 0.85rem;
}

.avatar-border-menu__section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 0.4rem;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.avatar-border-menu__section-head span:last-child {
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: none;
}

.avatar-border-styles {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.4rem;
}

.avatar-border-style {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 0.3rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.avatar-border-style:hover {
  border-color: color-mix(in srgb, var(--accent) 55%, var(--border-color));
}

.avatar-border-style--active {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.avatar-border-style input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.avatar-border-style__ring {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-tertiary);
}

.avatar-border-style__label {
  color: var(--text-secondary);
  font-size: 0.66rem;
  font-weight: 600;
}

.avatar-border-style--active .avatar-border-style__label {
  color: var(--text-primary);
}

.avatar-border-style__check {
  position: absolute;
  top: 0.28rem;
  right: 0.28rem;
  width: 12px;
  height: 12px;
  color: var(--accent);
}

.avatar-border-colors {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.35rem;
}

.avatar-border-color {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.32rem;
  padding: 0.28rem 0.35rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.avatar-border-color:hover {
  border-color: color-mix(in srgb, var(--accent) 55%, var(--border-color));
}

.avatar-border-color--active {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.avatar-border-color input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.avatar-border-color__swatch {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--swatch);
  color: #fff;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.28);
}

.avatar-border-color__swatch svg {
  width: 10px;
  height: 10px;
}

.avatar-border-color__label {
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 0.65rem;
  font-weight: 600;
  text-overflow: ellipsis;
}

.avatar-border-color--active .avatar-border-color__label {
  color: var(--text-primary);
}

.avatar-border-menu__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  margin-top: 0.9rem;
  padding-top: 0.7rem;
  border-top: 1px solid var(--border-color);
}

.avatar-border-menu__reset {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
}

.avatar-border-menu__reset:hover {
  color: var(--accent);
}

.avatar-border-menu__status {
  color: var(--text-muted);
  font-size: 0.63rem;
  text-align: right;
}

.border-menu-enter-active,
.border-menu-leave-active {
  transition: opacity 0.14s ease, transform 0.14s ease;
}

.border-menu-enter-from,
.border-menu-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}

.ring-preview--none {
  border: 1px dashed var(--border-color);
}

.ring-preview--solid {
  border: 3px solid var(--preview-color);
}

.ring-preview--dashed {
  border: 3px dashed var(--preview-color);
}

.ring-preview--double {
  border: 4px double var(--preview-color);
}

.ring-preview--glow {
  border: 3px solid var(--preview-color);
  box-shadow:
    0 0 0 3px color-mix(in srgb, var(--preview-color) 22%, transparent),
    0 0 12px color-mix(in srgb, var(--preview-color) 55%, transparent);
}

.ring-preview--gradient {
  background: conic-gradient(
    from 140deg,
    var(--preview-color),
    color-mix(in srgb, var(--preview-color) 28%, #ffffff),
    var(--preview-color),
    color-mix(in srgb, var(--preview-color) 38%, #000000),
    var(--preview-color)
  );
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 4px), #000 calc(100% - 4px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 4px), #000 calc(100% - 4px));
}

@media (max-width: 900px) {
  .avatar-border-menu {
    top: calc(100% + 0.5rem);
    left: 0;
  }
}

.avatar-input {
  display: none;
}

.profile-avatar__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.35rem;
}

.profile-avatar__actions .btn {
  align-self: auto;
}

.avatar-message {
  margin: 0;
  max-width: 180px;
  padding: 0.35rem 0.5rem;
  font-size: 0.72rem;
  text-align: center;
}

.profile-hero__identity {
  min-width: 0;
}

.profile-hero__eyebrow {
  margin: 0 0 0.35rem;
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.profile-hero__name {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.8rem, 3.5vw, 2.6rem);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.02em;
  overflow-wrap: anywhere;
}

.profile-hero__handle {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0.55rem 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  overflow-wrap: anywhere;
}

.profile-hero__dot {
  color: var(--text-muted);
}

.profile-hero__org {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.profile-hero__badges {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.9rem;
}

.profile-hero__progress {
  margin-top: 1rem;
  width: min(100%, 440px);
}

.profile-hero__progress-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.35rem;
  color: var(--text-secondary);
  font-size: 0.7rem;
  font-weight: 600;
}

.profile-hero__progress-bar {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.profile-hero__progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--purple));
  transition: width 0.35s ease;
}

.profile-hero__progress-note {
  margin: 0.4rem 0 0;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.profile-hero__joined {
  color: var(--text-muted);
  font-size: 0.78rem;
}

.profile-hero__title {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 600;
}

.profile-hero__title--uncommon { color: var(--success); border-color: var(--success); }
.profile-hero__title--rare { color: var(--accent); border-color: var(--accent); }
.profile-hero__title--epic { color: var(--purple); border-color: var(--purple); }
.profile-hero__title--legendary { color: var(--warning); border-color: var(--warning); }

.dna-title-message {
  margin: 0.5rem 0 0;
}

.profile-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.profile-stat {
  min-width: 86px;
  padding: 0.7rem 0.8rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: rgba(15, 23, 42, 0.22);
  text-align: center;
}

[data-theme="light"] .profile-stat {
  background: rgba(255, 255, 255, 0.72);
}

.profile-stat__value {
  display: block;
  color: var(--text-primary);
  font-size: 1.55rem;
  font-weight: 800;
  line-height: 1.15;
}

.profile-stat__value small {
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
}

.profile-stat__label {
  display: block;
  margin-top: 0.2rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

/* ------------------------------------------------------------------ */
/* Certificates and completion record                                  */
/* ------------------------------------------------------------------ */

.transcript-section {
  padding: 1.6rem;
}

.transcript-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.transcript-head .section-title {
  margin: 0 0 0.3rem;
  padding-bottom: 0;
  border-bottom: 0;
}

.transcript-help {
  margin: 0;
  max-width: 660px;
  font-size: 0.82rem;
}

.transcript-download {
  flex-shrink: 0;
  align-self: flex-start;
}

.transcript-download svg {
  width: 16px;
  height: 16px;
}

.transcript-message {
  margin-top: 1rem;
}

.certificate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(245px, 1fr));
  gap: 0.85rem;
  margin-top: 1.35rem;
}

.certificate-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 1.05rem 1rem 0.95rem;
  border-radius: 14px;
  border: 1px solid rgba(176, 141, 60, 0.35);
  background:
    linear-gradient(150deg, rgba(245, 158, 11, 0.11), transparent 58%),
    var(--bg-primary);
  color: inherit;
  text-decoration: none;
  transition: transform 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease;
}

.certificate-card:hover {
  transform: translateY(-2px);
  border-color: #b08d3c;
  box-shadow: 0 12px 26px rgba(2, 6, 23, 0.18);
}

.certificate-card__seal {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  margin-bottom: 0.3rem;
  border-radius: 50%;
  border: 1px solid rgba(176, 141, 60, 0.55);
  background: rgba(245, 158, 11, 0.12);
  color: #b08d3c;
}

.certificate-card__seal svg {
  width: 22px;
  height: 22px;
}

.certificate-card__track {
  font-size: 0.67rem;
  font-weight: 800;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.certificate-card__title {
  color: var(--text-primary);
  font-size: 0.98rem;
  font-weight: 700;
  line-height: 1.35;
}

.certificate-card__meta {
  color: var(--text-secondary);
  font-size: 0.75rem;
  line-height: 1.45;
}

.certificate-card__id {
  margin-top: 0.25rem;
  color: var(--text-muted);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.62rem;
  letter-spacing: 0.02em;
  overflow-wrap: anywhere;
}

.empty-transcript {
  margin-top: 1.25rem;
  padding: 1rem;
  border-radius: 10px;
  border: 1px dashed var(--border-color);
  color: var(--text-muted);
  font-size: 0.85rem;
}

.profile-tracks {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-color);
}

.subsection-title {
  margin: 0 0 0.75rem;
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.track-progress {
  margin-top: 0.75rem;
  padding: 0.85rem 0.95rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.track-progress__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
}

.track-progress__name {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 600;
}

.track-progress__count {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.track-progress__bar {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.track-progress__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transition: width 0.35s ease;
}

.track-progress__levels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.5rem;
  margin-top: 0.7rem;
}

.level-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.level-card--started {
  border-color: color-mix(in srgb, var(--accent) 45%, var(--border-color));
}

.level-card--complete {
  border-color: color-mix(in srgb, var(--success) 45%, var(--border-color));
  background: var(--success-bg);
}

.level-card__head,
.level-card__foot {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
}

.level-card__number {
  color: var(--text-muted);
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.level-card__status {
  color: var(--text-secondary);
  font-size: 0.64rem;
  font-weight: 600;
}

.level-card--complete .level-card__status {
  color: var(--success);
}

.level-card__name {
  overflow-wrap: anywhere;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1.3;
}

.level-card__progress {
  height: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.level-card__progress span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
  transition: width 0.35s ease;
}

.level-card--complete .level-card__progress span {
  background: var(--success);
}

.level-card__foot {
  color: var(--text-muted);
  font-size: 0.66rem;
}

.level-card__cert {
  color: var(--success);
  font-weight: 700;
}

.completion-details {
  margin-top: 1.5rem;
  padding-top: 1.1rem;
  border-top: 1px solid var(--border-color);
}

.completion-details summary {
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.completion-details summary:hover {
  color: var(--accent);
}

.completion-table-wrap {
  margin-top: 0.85rem;
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.completion-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.completion-table th {
  padding: 0.55rem 0.7rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-align: left;
  text-transform: uppercase;
  white-space: nowrap;
}

.completion-table td {
  padding: 0.55rem 0.7rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  vertical-align: top;
}

.completion-table tr:last-child td {
  border-bottom: 0;
}

.completion-table__lab {
  display: block;
  color: var(--text-primary);
  font-weight: 600;
}

.completion-table__level {
  display: block;
  margin-top: 0.1rem;
  color: var(--text-muted);
  font-size: 0.7rem;
}

.achievements-section {
  position: relative;
  overflow: hidden;
}

.achievements-section::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), #8b5cf6, #f59e0b);
}

.achievements-section__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.achievements-section__head .section-title {
  margin-bottom: 0.25rem;
}

.achievements-section__total {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  min-width: 104px;
  padding: 0.65rem 0.85rem;
  border: 1px solid color-mix(in srgb, var(--accent) 35%, var(--border-color));
  border-radius: 14px;
  background: var(--accent-bg);
}

.achievements-section__total strong {
  color: var(--text-primary);
  font-size: 1.45rem;
  font-weight: 800;
  line-height: 1.1;
}

.achievements-section__total span {
  margin-top: 0.1rem;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-align: center;
  text-transform: uppercase;
}

.course-achievement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.85rem;
}

.course-achievement-card {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background:
    radial-gradient(circle at 100% 0%, color-mix(in srgb, var(--accent) 12%, transparent), transparent 58%),
    var(--bg-primary);
}

.course-achievement-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.course-achievement-card__code {
  display: block;
  margin-bottom: 0.1rem;
  color: var(--accent);
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.course-achievement-card__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.25;
}

.course-achievement-card__count {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  min-width: 34px;
  height: 34px;
  padding: 0 0.45rem;
  border-radius: 10px;
  background: var(--accent-bg);
  color: var(--accent);
  font-size: 0.92rem;
  font-weight: 800;
}

.course-achievement-card__badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.course-achievement-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.7rem;
  line-height: 1.25;
}

.course-achievement-badge__icon {
  font-size: 0.85rem;
  line-height: 1;
}

.course-achievement-badge__count {
  color: var(--accent);
  font-weight: 800;
}

.course-achievement-card__foot {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.6rem;
  margin-top: auto;
  padding-top: 0.6rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.64rem;
}

.course-achievement-card--other {
  background:
    radial-gradient(circle at 100% 0%, rgba(234, 179, 8, 0.14), transparent 58%),
    var(--bg-primary);
}

.course-achievement-card--other .course-achievement-card__code,
.course-achievement-card--other .course-achievement-card__count {
  color: #b45309;
}

.course-achievement-card--other .course-achievement-card__count {
  background: rgba(234, 179, 8, 0.14);
}

@media (max-width: 900px) {
  .profile-hero {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .achievements-section__head {
    flex-direction: column;
  }

  .achievements-section__total {
    align-items: flex-start;
    width: 100%;
  }

  .profile-stats {
    grid-column: 1 / -1;
    justify-content: stretch;
  }

  .profile-stat {
    flex: 1;
  }
}

@media (max-width: 640px) {
  .profile-page {
    padding: 1rem;
  }

  .profile-hero {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
    padding: 1.4rem 1rem;
  }

  .profile-hero__handle,
  .profile-hero__badges {
    justify-content: center;
  }

  .profile-stats {
    width: 100%;
  }

  .profile-stat {
    min-width: 0;
    padding: 0.6rem 0.4rem;
  }

  .transcript-section {
    padding: 1.1rem;
  }

  .transcript-head {
    flex-direction: column;
  }

  .transcript-download {
    width: 100%;
  }

  .profile-tabs {
    margin: 0 -0.25rem;
  }

  .profile-tab {
    min-height: 44px;
    padding: 0.6rem 0.65rem;
  }

  .overview-stat-row {
    grid-template-columns: 1fr;
  }
}

.mfa-qr-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  margin: 0.6rem 0;
}

.mfa-qr {
  width: 180px;
  height: 180px;
  padding: 8px;
  border-radius: 8px;
  background: #fff;
  image-rendering: pixelated;
}

.mfa-manual {
  margin-top: 0.35rem;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.mfa-manual summary {
  cursor: pointer;
  color: var(--accent);
  font-weight: 600;
}
</style>

