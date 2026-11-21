<template>
  <div class="youth-privacy">
    <main class="youth-card" aria-labelledby="youth-privacy-title">
      <header class="youth-card__header">
        <p class="youth-card__eyebrow">SWOCTS Cyber Range</p>
        <h1 id="youth-privacy-title">Your privacy, in plain language</h1>
        <p class="youth-card__lead">
          This page explains what the Cyber Range knows about you, what is
          optional, and how to change or delete it. The
          <router-link to="/privacy">full Privacy notice</router-link> has more detail.
        </p>
      </header>

      <section>
        <h2>What we need to run your account</h2>
        <ul>
          <li>Your username and email address to sign you in.</li>
          <li>Your password, stored only as a secure hash.</li>
          <li>Your course, exercise, and lab progress so you can see your work.</li>
          <li>Security logs, such as sign-in time and IP address, to keep the platform safe.</li>
        </ul>
        <p>
          We do not need your precise location, your contacts, or your browsing
          history outside the Cyber Range.
        </p>
      </section>

      <section>
        <h2>What is optional</h2>
        <p>
          These features are <strong>off until you choose them</strong>. Turning
          them down does not block your labs or courses.
        </p>
        <ul>
          <li><strong>Cyber DNA</strong> — a learning profile based on your practice.</li>
          <li><strong>Cyber GPS</strong> — learning routes and career suggestions.</li>
          <li><strong>Professional portfolio</strong> — a portfolio you can share later.</li>
          <li><strong>AI coach</strong> — chat history and AI memory.</li>
          <li><strong>Research</strong> — learner-level analytics used for research.</li>
          <li><strong>Account email</strong> — optional messages about your account.</li>
        </ul>
        <p>
          Public scoreboards and public certificate verification are also
          <strong>off by default</strong>. You choose whether to appear publicly.
        </p>
      </section>

      <section>
        <h2>What we never do</h2>
        <ul>
          <li>We do not sell your information.</li>
          <li>We do not use advertising or targeted ads.</li>
          <li>We do not use third-party behavioural analytics.</li>
          <li>We do not use your information to guess your emotions.</li>
          <li>
            We do not ask for your device's precise location. We log sign-in IP
            addresses for security.
          </li>
        </ul>
      </section>

      <section>
        <h2>Your choices</h2>
        <p>
          Open <strong>Profile → Security &amp; privacy</strong> to enable or
          revoke each optional feature. Revoking stops the feature and deletes its
          derived data. You can also download a copy of your data or delete your
          account from <strong>Profile → Security &amp; privacy → Privacy and data</strong>.
        </p>
      </section>

      <section>
        <h2>If you are under 13</h2>
        <p>
          A parent or guardian must agree before an under-13 account is created.
          Ask your instructor to create an institution-managed account with a
          parental or guardian consent reference. You can still ask us to delete
          your information at any time.
        </p>
      </section>

      <section>
        <h2>If you are 13 to 17</h2>
        <p>
          You can make your own privacy choices. We explain each optional feature
          before you turn it on, and you can change your mind whenever you want.
          A parent or guardian can help you use the platform and can contact us
          about your information.
        </p>
      </section>

      <section>
        <h2>Questions or complaints</h2>
        <p>
          Ask an adult you trust, or contact the privacy team at
          <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>. If you are
          not satisfied, you can contact the Office of the Privacy Commissioner of
          Canada.
        </p>
      </section>

      <footer class="youth-card__footer">
        <router-link to="/privacy">Full Privacy notice</router-link>
        <span aria-hidden="true"> · </span>
        <router-link to="/">Return to the platform</router-link>
      </footer>
    </main>
  </div>
</template>

<style scoped>
.youth-privacy {
  min-height: 100vh;
  padding: 2rem 1rem;
  background: var(--bg-primary);
}

.youth-card {
  max-width: 760px;
  margin: 0 auto;
  padding: 2rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
}

.youth-card__eyebrow {
  margin: 0 0 0.35rem;
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.youth-card h1 {
  margin: 0;
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  color: var(--text-primary);
}

.youth-card__lead {
  margin: 0.75rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.youth-card section {
  margin-top: 1.6rem;
}

.youth-card h2 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.youth-card p,
.youth-card li {
  color: var(--text-secondary);
  line-height: 1.65;
}

.youth-card ul {
  padding-left: 1.25rem;
}

.youth-card a {
  color: var(--accent);
}

.youth-card__footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.85rem;
  color: var(--text-muted);
}
</style>
