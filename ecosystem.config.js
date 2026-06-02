// PM2 process config — how ShellAgent's VM starts this agent on deploy.
// Reads PORT from .env (ShellAgent allocates one at provisioning), then
// launches uvicorn against the FastAPI app in src/main.py. Mirrors the
// platform's fastapi template so the "external agent" path provisions it
// with no changes.
const fs = require("fs");
const path = require("path");

function loadEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const out = {};
  for (const raw of fs.readFileSync(filePath, "utf8").split("\n")) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq < 1) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    out[key] = value;
  }
  return out;
}

const envFromFile = loadEnvFile(path.join(__dirname, ".env"));
const port = envFromFile.PORT || process.env.PORT || "3000";

module.exports = {
  apps: [
    {
      name: "wordwise",
      script: "./.venv/bin/uvicorn",
      interpreter: "none",
      cwd: __dirname,
      args: `app.main:app --host 0.0.0.0 --port ${port}`,
      max_restarts: 10,
      min_uptime: "30s",
      env: { ...envFromFile },
    },
  ],
};
