import { defineConfig } from "@playwright/test";
import packagedChromium from "@sparticuz/chromium";

const chromiumExecutable = await packagedChromium.executablePath();

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  workers: 1,
  outputDir: "./test-results",
  use: {
    baseURL: "http://127.0.0.1:7860",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    launchOptions: {
      executablePath: chromiumExecutable,
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    },
  },
  webServer: {
    command: "../.venv/bin/python -m uvicorn app.main:app --app-dir ../backend --host 127.0.0.1 --port 7860",
    cwd: ".",
    env: {
      APP_HOST: "127.0.0.1",
      APP_PORT: "7860",
      APP_DATA_DIR: "/tmp/agent-card-intake-e2e",
      LLM_PROVIDER: "mock",
    },
    url: "http://127.0.0.1:7860/api/health",
    reuseExistingServer: false,
    timeout: 30_000,
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 } } },
  ],
});
