(function () {
  "use strict";

  var PROTOCOLS = {
    modbus: { port: "502", script: "modbus-discover" },
    s7: { port: "102", script: "s7-info" },
    enip: { port: "44818", script: "enip-info" },
    dnp3: { port: "20000", script: "dnp3-info" }
  };

  var mode = "discover";
  var target = document.getElementById("target");
  var delay = document.getElementById("delay");
  var command = document.getElementById("command");
  var copy = document.getElementById("copy");
  var copyState = document.getElementById("copy-state");
  var warning = document.getElementById("warning");
  var auth = document.getElementById("auth");
  var modeDiscover = document.getElementById("mode-discover");
  var modeService = document.getElementById("mode-service");
  var protocolWrap = document.getElementById("protocol-wrap");

  try {
    var stored = localStorage.getItem("theme");
    if (stored === "light" || stored === "contrast") {
      document.documentElement.setAttribute("data-theme", stored === "light" ? "light" : "dark");
    }
  } catch (err) { /* private mode */ }

  function validIPv4(value) {
    var parts = value.split(".");
    if (parts.length !== 4) return false;
    for (var i = 0; i < 4; i++) {
      if (!/^\d{1,3}$/.test(parts[i])) return false;
      var n = Number(parts[i]);
      if (n < 0 || n > 255) return false;
    }
    return true;
  }

  function validTarget(value) {
    var v = value.trim();
    if (!v) return null;
    var slash = v.indexOf("/");
    if (slash === -1) return validIPv4(v) ? v : null;
    var host = v.slice(0, slash);
    var mask = v.slice(slash + 1);
    if (!validIPv4(host) || !/^\d{1,2}$/.test(mask)) return null;
    var bits = Number(mask);
    if (bits < 0 || bits > 32) return null;
    return host + "/" + bits;
  }

  function selectedProtocols() {
    var out = [];
    document.querySelectorAll(".protocols input:checked").forEach(function (el) {
      if (PROTOCOLS[el.value]) out.push(PROTOCOLS[el.value]);
    });
    return out;
  }

  function build() {
    var safe = validTarget(target.value);
    auth.checked ? warning.classList.remove("show") : warning.classList.add("show");

    if (!safe) {
      command.textContent = "Enter a valid IPv4 address or CIDR range.";
      copy.disabled = true;
      return;
    }

    if (mode === "discover") {
      command.textContent = "nmap -sn -PR " + safe;
    } else {
      var protocols = selectedProtocols();
      if (!protocols.length) {
        command.textContent = "Select at least one protocol.";
        copy.disabled = true;
        return;
      }
      var ports = protocols.map(function (p) { return p.port; }).join(",");
      var scripts = protocols.map(function (p) { return p.script; }).join(",");
      command.textContent =
        "nmap -sT -Pn -p " + ports +
        " --scan-delay " + delay.value +
        " --max-parallelism 1" +
        " --script " + scripts +
        " " + safe;
    }

    copy.disabled = !auth.checked;
  }

  function setMode(next) {
    mode = next;
    modeDiscover.setAttribute("aria-pressed", String(next === "discover"));
    modeService.setAttribute("aria-pressed", String(next === "service"));
    protocolWrap.style.display = next === "service" ? "" : "none";
    build();
  }

  modeDiscover.addEventListener("click", function () { setMode("discover"); });
  modeService.addEventListener("click", function () { setMode("service"); });
  target.addEventListener("input", build);
  delay.addEventListener("change", build);
  document.querySelectorAll(".protocols input").forEach(function (el) {
    el.addEventListener("change", build);
  });
  auth.addEventListener("change", build);

  copy.addEventListener("click", function () {
    var text = command.textContent;
    if (!text) return;
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

  setMode("discover");
  target.value = "10.100.3.60";
  build();
})();
