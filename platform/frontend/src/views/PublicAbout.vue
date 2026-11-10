<template>
  <div class="public-about">
    <header class="public-about__nav">
      <router-link to="/" class="public-about__brand" aria-label="SWOCTS Cyber Range home">
        <img src="/swocts-cyber-range-mark.png" alt="" />
        <span>SWOCTS Cyber Range</span>
      </router-link>
      <nav class="public-about__nav-links" aria-label="Public links">
        <router-link to="/verify">Verify a certificate</router-link>
        <router-link v-if="signedIn" to="/dashboard">Dashboard</router-link>
        <router-link v-if="signedIn && role === 'instructor'" to="/instructor">Instructor</router-link>
        <router-link v-if="signedIn && role === 'admin'" to="/admin">Admin</router-link>
        <router-link v-if="signedIn" to="/about/installation">Installation details</router-link>
        <router-link v-if="!signedIn" to="/login">Sign in</router-link>
        <router-link v-if="!signedIn" to="/register" class="public-about__cta">Create account</router-link>
      </nav>
    </header>

    <main class="public-about__main">
      <section class="public-about__hero" aria-labelledby="public-about-title">
        <div class="public-about__hero-copy">
          <p class="public-about__eyebrow">About this site</p>
          <h1 id="public-about-title">Hands-on cybersecurity training you can prove.</h1>
          <p class="public-about__lead">
            SWOCTS Cyber Range is a browser-based learning platform for practical
            cybersecurity skills. You work through guided labs, get feedback, and
            earn certificates that can be checked by employers and instructors.
          </p>
          <div class="public-about__actions">
            <router-link v-if="!signedIn" to="/register" class="btn btn--primary">Create an account</router-link>
            <router-link v-if="!signedIn" to="/login" class="btn btn--secondary">Sign in</router-link>
            <router-link v-if="signedIn" to="/dashboard" class="btn btn--primary">Go to dashboard</router-link>
            <router-link to="/verify" class="btn btn--secondary">Verify a certificate</router-link>
          </div>
        </div>

        <aside class="public-about__hero-card" aria-label="What you can do">
          <h2>What you can do</h2>
          <ul>
            <li>
              <span class="public-about__icon" aria-hidden="true">›</span>
              <span><strong>Learn by doing.</strong> Work in realistic labs, not just slides.</span>
            </li>
            <li>
              <span class="public-about__icon" aria-hidden="true">›</span>
              <span><strong>See your progress.</strong> Track completion, hints, attempts, and time.</span>
            </li>
            <li>
              <span class="public-about__icon" aria-hidden="true">›</span>
              <span><strong>Show what you can do.</strong> Share a certificate that can be verified online.</span>
            </li>
          </ul>
        </aside>
      </section>

      <section class="public-about__cards" aria-label="Why this platform">
        <article class="public-about__card">
          <h2>Built for learning</h2>
          <p>
            Exercises include objectives, estimated time, and knowledge checks.
            Instructors can see where a class is stuck and where learners are ready
            for more.
          </p>
        </article>
        <article class="public-about__card">
          <h2>Private by design</h2>
          <p>
            You control your profile, scoreboard name, optional email, survey
            participation, and public certificate verification. Your progress is
            not publicly ranked by default.
          </p>
        </article>
        <article class="public-about__card">
          <h2>Verifiable results</h2>
          <p>
            Certificates carry a unique ID. Anyone can paste that ID on the
            verification page to confirm the track, level, completion count, and
            award date without seeing account details.
          </p>
        </article>
      </section>

      <section class="public-about__details" aria-labelledby="public-about-details-title">
        <h2 id="public-about-details-title">What to know before you start</h2>
        <div class="public-about__details-grid">
          <article>
            <h3>Who this is for</h3>
            <p>
              Learners building practical security skills, instructors running a
              class or lab, and programmes that need evidence of completion.
            </p>
          </article>
          <article>
            <h3>Getting access</h3>
            <p>
              Create an account from the registration page. Some courses and events
              require an invite code from your instructor.
            </p>
          </article>
          <article>
            <h3>Privacy and security</h3>
            <p>
              Read the <router-link to="/privacy">Privacy notice</router-link> for
              what we collect, how long we keep it, and how to export or delete your
              account. Security questions can go to your instructor or administrator.
            </p>
          </article>
          <article>
            <h3>Need help?</h3>
            <p>
              Contact your instructor for course access. Privacy questions:
              <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>.
            </p>
          </article>
        </div>
      </section>
    </main>

    <footer class="public-about__footer">
      <span>Powered by OpenCyberRange.</span>
      <nav aria-label="Footer links">
        <router-link to="/privacy">Privacy</router-link>
        <router-link to="/verify">Verify a certificate</router-link>
        <router-link v-if="!signedIn" to="/login">Sign in</router-link>
      </nav>
    </footer>
  </div>
</template>

<script setup>
const user = JSON.parse(localStorage.getItem('user') || '{}')
const signedIn = Boolean(localStorage.getItem('token'))
const role = user.role || 'student'
</script>

<style scoped>
.public-about {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 12% 0%, rgba(56, 189, 248, 0.14), transparent 40%),
    radial-gradient(circle at 90% 20%, rgba(139, 92, 246, 0.12), transparent 42%),
    var(--bg-primary);
  color: var(--text-primary);
}

.public-about__nav {
  width: min(100% - 2rem, 1100px);
  margin: 0 auto;
  padding: 1rem 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.public-about__brand {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  color: var(--text-primary);
  font-weight: 700;
  text-decoration: none;
}

.public-about__brand img {
  width: 38px;
  height: 38px;
  object-fit: contain;
}

.public-about__nav-links {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.9rem;
  font-size: 0.85rem;
}

.public-about__nav-links a {
  color: var(--text-secondary);
  text-decoration: none;
}

.public-about__nav-links a:hover {
  color: var(--text-primary);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.public-about__cta {
  padding: 0.45rem 0.75rem;
  border: 1px solid var(--accent);
  border-radius: 8px;
  color: var(--accent) !important;
  font-weight: 700;
}

.public-about__main {
  width: min(100% - 2rem, 1100px);
  margin: 0 auto;
  flex: 1;
  padding: 2rem 0 3rem;
}

.public-about__hero {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.9fr);
  gap: 1.5rem;
  align-items: stretch;
  padding: 1.5rem 0 2rem;
}

.public-about__eyebrow {
  margin: 0 0 0.5rem;
  color: var(--accent);
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.public-about__hero h1 {
  margin: 0 0 0.8rem;
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.public-about__lead {
  max-width: 62ch;
  margin: 0;
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.65;
}

.public-about__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 1.25rem;
}

.public-about__hero-card {
  padding: 1.1rem 1.15rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  box-shadow: 0 12px 32px rgba(2, 6, 23, 0.18);
}

.public-about__hero-card h2 {
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
}

.public-about__hero-card ul {
  display: grid;
  gap: 0.7rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.public-about__hero-card li {
  display: flex;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.5;
}

.public-about__icon {
  flex: 0 0 auto;
  color: var(--accent);
  font-weight: 800;
}

.public-about__cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
  margin: 1rem 0 2rem;
}

.public-about__card {
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.public-about__card h2 {
  margin: 0 0 0.4rem;
  font-size: 0.95rem;
}

.public-about__card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.public-about__details h2 {
  margin: 0 0 0.8rem;
  font-size: 1.2rem;
}

.public-about__details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
}

.public-about__details-grid article {
  padding: 0.95rem 1.05rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.public-about__details-grid h3 {
  margin: 0 0 0.35rem;
  font-size: 0.9rem;
}

.public-about__details-grid p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.public-about a {
  color: var(--accent);
}

.public-about__footer {
  width: min(100% - 2rem, 1100px);
  margin: 0 auto;
  padding: 1rem 0 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  color: var(--text-muted);
  font-size: 0.78rem;
}

.public-about__footer nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
}

.public-about__footer a {
  color: var(--text-secondary);
  text-decoration: none;
}

.public-about__footer a:hover {
  color: var(--text-primary);
  text-decoration: underline;
}

.public-about a:focus-visible,
.public-about button:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
  border-radius: 4px;
}

@media (max-width: 760px) {
  .public-about__hero {
    grid-template-columns: 1fr;
    padding-top: 0.75rem;
  }

  .public-about__nav {
    align-items: flex-start;
    flex-direction: column;
  }

  .public-about__nav-links {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
