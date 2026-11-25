(function () {
  "use strict";

  var mode = "baseline";
  var target = document.getElementById("target");
  var runner = document.getElementById("runner");
  var minutes = document.getElementById("minutes");
  var level = document.getElementById("level");
  var command = document.getElementById("command");
  var copy = document.getElementById("copy");
  var copyState = document.getElementById("copy-state");
  var auth = document.getElementById("auth");
  var disposable = document.getElementById("disposable");
  var scope = document.getElementById("scope");
  var authWarning = document.getElementById("auth-warning");
  var fullWarning = document.getElementById("full-warning");
  var modeHint = document.getElementById("mode-hint");
  var modeBaseline = document.getElementById("mode-baseline");
  var modeFull = document.getElementById("mode-full");
  var reportHtml = document.getElementById("report-html");
  var reportJson = document.getElementById("report-json");
  var reportMd = document.getElementById("report-md");

  try {
    var stored = localStorage.getItem("theme");
    if (stored === "light" || stored === "contrast") {
      document.documentElement.setAttribute("data-theme", stored === "light" ? "light" : "dark");
    }
  } catch (err) { /* private mode */ }

  function safeTarget(value) {
    var raw = value.trim();
    if (!raw) return null;
    if (/\s/.test(raw)) return null;
    if (/^[a-z][a-z0-9+.-]*:\/\//i.test(raw) && !/^https?:\/\//i.test(raw)) return null;
    if (!/^https?:\/\//i.test(raw)) raw = "https://" + raw;
    var url;
    try {
      url = new URL(raw);
    } catch (err) {
      return null;
    }
    if (url.protocol !== "http:" && url.protocol !== "https:") return null;
    if (!url.hostname) return null;
    // The URL is written into a shell command. Reject anything that would
    // need more than single-quote escaping, and reject credentials.
    if (url.username || url.password) return null;
    if (/[\\"'`$\n\r]/.test(url.href)) return null;
    return url.href;
  }

  function quote(value) {
    return "'" + value + "'";
  }

  function reportFlags() {
    var flags = [];
    if (reportHtml.checked) flags.push("-r zap-report.html");
    if (reportJson.checked) flags.push("-J zap-report.json");
    if (reportMd.checked) flags.push("-w zap-report.md");
    return flags;
  }

  function build() {
    var safe = safeTarget(target.value);
    var baseline = mode === "baseline";
    var docker = runner.value === "docker";
    var allChecked = auth.checked && disposable.checked && scope.checked;

    fullWarning.classList.toggle("show", !baseline);
    modeHint.textContent = baseline
      ? "Baseline spider and passive rules. Safe for a normal practice app."
      : "Full scan sends active attacks. Use a disposable target and a restore path.";
    authWarning.classList.toggle("show", !allChecked);

    if (!safe) {
      command.textContent = target.value.trim()
        ? "Enter a valid http:// or https:// target URL without credentials."
        : "Enter an authorised target URL to generate a command.";
      copy.disabled = true;
      return;
    }

    var script = baseline ? "zap-baseline.py" : "zap-full-scan.py";
    var parts = [];
    if (docker) {
      parts.push('docker run --rm -t -v "$PWD:/zap/wrk/:rw" zaproxy/zap-stable');
    }
    parts.push(script);
    parts.push("-t " + quote(safe));
    parts = parts.concat(reportFlags());
    parts.push("-m " + minutes.value);
    parts.push("-l " + level.value);

    if (!reportHtml.checked && !reportJson.checked && !reportMd.checked) {
      parts.push("-r zap-report.html");
    }

    command.textContent = parts.join(" ");
    copy.disabled = !allChecked;
  }

  function setMode(next) {
    mode = next;
    modeBaseline.setAttribute("aria-pressed", String(next === "baseline"));
    modeFull.setAttribute("aria-pressed", String(next === "full"));
    build();
  }

  modeBaseline.addEventListener("click", function () { setMode("baseline"); });
  modeFull.addEventListener("click", function () { setMode("full"); });
  [target, runner, minutes, level, reportHtml, reportJson, reportMd, auth, disposable, scope].forEach(function (element) {
    element.addEventListener("input", build);
    element.addEventListener("change", build);
  });

  copy.addEventListener("click", function () {
    var text = command.textContent;
    if (!text || copy.disabled) return;
    function done() {
      copyState.textContent = "Copied";
      window.setTimeout(function () { copyState.textContent = ""; }, 1800);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(fallback);
    } else {
      fallback();
    }
    function fallback() {
      var area = document.createElement("textarea");
      area.value = text;
      document.body.appendChild(area);
      area.select();
      try { document.execCommand("copy"); done(); } catch (err) { copyState.textContent = "Select and copy manually"; }
      document.body.removeChild(area);
    }
  });

  // A full scan is the risky default to explain, so start in baseline mode.
  setMode("baseline");
  build();
})();
