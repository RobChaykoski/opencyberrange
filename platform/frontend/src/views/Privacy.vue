<template>
  <div class="privacy-page">
    <main class="privacy-card" aria-labelledby="privacy-title">
      <header class="privacy-card__header">
        <p class="privacy-card__eyebrow">SWOCTS Cyber Range</p>
        <h1 id="privacy-title">Privacy notice</h1>
        <p class="privacy-card__lead">
          This notice explains how the SWOCTS Cyber Range handles personal
          information. It supplements the
          <a href="https://www.swocts.com/privacy" target="_blank" rel="noopener noreferrer">
            SWOCTS Privacy Policy
          </a>
          and is written to align with Canada's Personal Information Protection
          and Electronic Documents Act (PIPEDA).
        </p>
        <p class="privacy-card__meta">Effective 10 November 2026</p>
      </header>

      <section>
        <h2>Contact and accountability</h2>
        <p>
          SWOCTS is responsible for the personal information described here.
          Privacy questions, access requests, correction requests, consent
          withdrawals, and complaints can be sent to the SWOCTS Privacy Officer
          at <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>. We will
          respond within a reasonable time and, where required, work with the
          Office of the Privacy Commissioner of Canada.
        </p>
      </section>

      <section>
        <h2>Scope</h2>
        <p>
          This notice applies to the SWOCTS Cyber Range training platform,
          including its web interface, APIs, lab environments, VPN access,
          courses, exercises, certificates, surveys, and support channels. The
          separate
          <a href="https://www.swocts.com/privacy" target="_blank" rel="noopener noreferrer">
            SWOCTS Privacy Policy
          </a>
          also covers SWOCTS events, workshops, volunteer sign-ups, mailing
          lists, and the SWOCTS Hub website.
        </p>
      </section>

      <section>
        <h2>What we collect</h2>
        <ul>
          <li>
            <strong>Account details:</strong> username, email address, name,
            organisation, and student identifier where an institution provides
            one.
          </li>
          <li>
            <strong>Authentication and security data:</strong> password hashes,
            optional MFA secrets and recovery codes, trusted devices, session
            records, login timestamps, and IP addresses.
          </li>
          <li>
            <strong>Learning activity:</strong> course enrolment, lab starts,
            flag attempts, completions, hints, quiz attempts, achievements,
            certificates, and transcript records.
          </li>
          <li>
            <strong>Optional feedback and surveys:</strong> pulse responses,
            course check-ins, free-text comments, and research responses only
            where the learner has opted in.
          </li>
          <li>
            <strong>VPN and lab access data:</strong> WireGuard public keys,
            assigned client addresses, and session records needed to operate
            isolated exercises.
          </li>
          <li>
            <strong>Support and operational records:</strong> messages sent to
            administrators, audit events, backups, and diagnostic logs.
          </li>
        </ul>
        <p>We collect only the information needed for the purposes below.</p>
      </section>

      <section>
        <h2>Why we use it</h2>
        <ul>
          <li>To create and secure accounts and authenticate users.</li>
          <li>To deliver courses, exercises, labs, workbooks, and certificates.</li>
          <li>To show learners their progress and give instructors authorised course visibility.</li>
          <li>To operate the VPN, lab orchestration, backups, and platform security.</li>
          <li>To investigate misuse, protect the service, and meet legal or institutional obligations.</li>
          <li>To run optional surveys or research only with the required consent.</li>
        </ul>
        <p>
          We do not sell personal information. We do not use learner data for
          advertising, and we do not use optional survey or research data for
          purposes that were not disclosed when consent was collected.
        </p>
      </section>

      <section>
        <h2>Our privacy practices</h2>
        <p>We apply these practices across the platform:</p>
        <ul>
          <li>
            <strong>Privacy by design and by default.</strong> Optional
            feedback, surveys, and research are off until the learner opts in.
            Course and exercise analytics are suppressed below the configured
            minimum cohort (default 5 learners), and the interface shows
            "Suppressed" or "No evidence" instead of a misleading zero. Public
            rankings are not used, and celebrations are voluntary and anonymous.
          </li>
          <li>
            <strong>Data minimisation and purpose limitation.</strong> We collect
            the account, learning, security, VPN, and support data needed to run
            the training service. We do not collect keystrokes, screen
            recordings, or browsing history outside the platform. We do not sell
            personal information or use it for advertising, and optional data is
            used only for the purpose disclosed at collection.
          </li>
          <li>
            <strong>Least-privilege access.</strong> Learners see their own
            records. Instructors see the courses they own or are authorised to
            support. Administrative access is restricted and audited, and
            exports require a recorded reason.
          </li>
          <li>
            <strong>Separate identity from analytics.</strong> Class-level
            analytics and reports use counts, medians, and minimum-cohort
            suppression. Individual records are available only to the learner
            and authorised instructors, and reports are designed for a stated
            teaching decision rather than ranking.
          </li>
          <li>
            <strong>Retention and deletion.</strong> Account deletion removes
            identity, credential, VPN, learning, survey, and session data,
            anonymises activity events, and keeps a keyed suppression hash so a
            restore cannot resurrect the account. Backups default to 30 days,
            and audit and activity records are kept for a short documented
            period. Instructor deletion is blocked until owned courses are
            transferred.
          </li>
          <li>
            <strong>Security safeguards.</strong> We use Argon2id password
            hashing, optional MFA, session revocation, role-based authorization,
            encrypted transport, encrypted WireGuard key storage, isolated
            per-lab networks, audit logging, restricted administrative access,
            and access-controlled backup handling. No system is perfectly
            secure.
          </li>
          <li>
            <strong>Operational logging.</strong> We record sign-in, security,
            export, and administrative events, including IP addresses and
            account identifiers where needed for security and audit. We do not
            use advertising trackers or third-party behavioural analytics. Logs
            are restricted and retained for a documented period.
          </li>
          <li>
            <strong>Vendors and transfers.</strong> Hosting, network, and
            support providers process personal information only under
            confidentiality and security obligations. Where information is
            processed outside Canada, we take reasonable steps to provide
            comparable protection. Operators should document their hosting
            location and subprocessors.
          </li>
          <li>
            <strong>Requests and complaints.</strong> Learners can export or
            delete their account from
            <strong>Profile &rarr; Privacy and data</strong>. Access,
            correction, consent withdrawal, and other requests go to
            <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>. We verify
            identity, respond within a reasonable time, and escalate unresolved
            concerns to the Office of the Privacy Commissioner of Canada where
            required.
          </li>
          <li>
            <strong>Accountability and assessment.</strong> The SWOCTS Privacy
            Officer is accountable for these practices. Staff with access receive
            privacy and security guidance. Institutional operators should
            complete a privacy impact assessment, document the lawful basis, and
            review retention, consent, and minors' requirements before
            deployment.
          </li>
        </ul>
      </section>

      <section>
        <h2>Consent and withdrawal</h2>
        <p>
          Creating an account and using the platform provides the information
          needed to operate the training service. Optional features, including
          account email, surveys, feedback publication, and research
          participation, are separate choices. You can withdraw optional consent
          from <strong>Profile &rarr; Privacy and data</strong> or by contacting
          <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>. Withdrawal
          may limit optional features but does not affect access to core
          learning records where retention is required by the institution or
          law.
        </p>
      </section>

      <section>
        <h2>Disclosure and transfers</h2>
        <p>
          We may disclose personal information to the learner's institution and
          its authorised instructors, to service providers that host, secure, or
          support the platform under confidentiality obligations, and to legal or
          regulatory authorities where required by law. Where information is
          processed outside Canada, we take reasonable steps to protect it at a
          comparable level.
        </p>
      </section>

      <section>
        <h2>Retention</h2>
        <p>
          Account, course, and learning records are kept for the period required
          by the institution's retention schedule. Operational audit and activity
          records are retained for a short documented period. Backups default to
          30 days. Account deletion removes identity, credential, VPN, learning,
          survey, and session data, anonymises activity events, and keeps a
          suppression hash so a restore cannot resurrect the account. The
          detailed technical behaviour is documented in the platform's privacy,
          erasure, and backup guidance.
        </p>
      </section>

      <section>
        <h2>Safeguards</h2>
        <p>
          Safeguards include role-based access control, Argon2id password
          hashing, optional MFA, encrypted transport, isolated lab networks,
          audit logging, restricted administrative access, and encrypted backup
          handling. No system is perfectly secure; report suspected issues to
          <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>.
        </p>
      </section>

      <section>
        <h2>Your rights under PIPEDA</h2>
        <p>Subject to applicable exceptions, you may:</p>
        <ul>
          <li>request access to personal information we hold about you;</li>
          <li>request correction of inaccurate or incomplete information;</li>
          <li>withdraw optional consent;</li>
          <li>request export or deletion of your account data;</li>
          <li>challenge our compliance with PIPEDA.</li>
        </ul>
        <p>
          Some requests require identity verification. Learners can export or
          delete their account from <strong>Profile &rarr; Privacy and data</strong>.
          Others can write to
          <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>. If a concern
          is not resolved, it may be raised with the Office of the Privacy
          Commissioner of Canada.
        </p>
      </section>

      <section>
        <h2>Cookies and local storage</h2>
        <p>
          The platform uses browser storage for the signed-in session, theme,
          privacy-mode preference, and similar interface state. It does not use
          advertising trackers. Blocking required storage may prevent sign-in or
          other core features from working.
        </p>
      </section>

      <section>
        <h2>Institutional deployments</h2>
        <p>
          Where the platform is operated by a Canadian public institution,
          Ontario's FIPPA or MFIPPA, institutional privacy policies, and research
          ethics requirements may also apply. This notice is a platform-level
          statement, not legal advice. Operators should review it with their
          privacy office and adjust retention, consent, and contact details to
          match the deployment.
        </p>
      </section>

      <section>
        <h2>Learners under 18</h2>
        <p>
          Where the platform is used in a high-school or youth programme, the
          institution or programme operator is responsible for obtaining any
          required parent or guardian consent and for limiting collection to what
          the programme needs. Learners under 18 should not be included in
          optional research, public showcases, or external reporting without the
          required consent.
        </p>
      </section>

      <section>
        <h2>Suspected privacy incidents</h2>
        <p>
          Report suspected privacy or security incidents to
          <a href="mailto:privacy@swocts.com">privacy@swocts.com</a>. We will
          contain and assess the incident, preserve the relevant evidence,
          notify the institution and affected individuals, and notify regulators
          where required by law.
        </p>
      </section>

      <section>
        <h2>Changes</h2>
        <p>
          We may update this notice as the platform or legal requirements change.
          The effective date will be revised and, where appropriate, the change
          will be announced in the platform or by email.
        </p>
      </section>

      <footer class="privacy-card__footer">
        <router-link to="/">Return to the platform</router-link>
        <span aria-hidden="true"> · </span>
        <a href="https://www.swocts.com/privacy" target="_blank" rel="noopener noreferrer">
          Full SWOCTS Privacy Policy
        </a>
      </footer>
    </main>
  </div>
</template>

<style scoped>
.privacy-page {
  min-height: 100vh;
  display: grid;
  place-items: start center;
  padding: clamp(1rem, 3vw, 2.5rem);
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.08), transparent 32rem),
    var(--bg-primary);
}

.privacy-card {
  width: min(100%, 900px);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: clamp(1.25rem, 3vw, 2.5rem);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18);
}

.privacy-card__header {
  padding-bottom: 1.25rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.privacy-card__eyebrow {
  margin: 0 0 0.35rem;
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.privacy-card h1 {
  margin: 0 0 0.75rem;
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  color: var(--text-primary);
}

.privacy-card__lead,
.privacy-card__meta {
  color: var(--text-secondary);
  line-height: 1.7;
}

.privacy-card__meta {
  margin: 0.75rem 0 0;
  font-size: 0.85rem;
}

.privacy-card section {
  margin-top: 1.6rem;
}

.privacy-card h2 {
  margin: 0 0 0.55rem;
  font-size: 1.08rem;
  color: var(--text-primary);
}

.privacy-card p,
.privacy-card li {
  color: var(--text-secondary);
  line-height: 1.7;
}

.privacy-card ul {
  margin: 0.5rem 0 0;
  padding-left: 1.25rem;
}

.privacy-card li + li {
  margin-top: 0.35rem;
}

.privacy-card a {
  color: var(--accent);
}

.privacy-card__footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.9rem;
}

@media (max-width: 640px) {
  .privacy-page {
    padding: 0.75rem;
  }

  .privacy-card {
    padding: 1.15rem;
    border-radius: 12px;
  }
}
</style>
