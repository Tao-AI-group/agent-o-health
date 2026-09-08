import { expect, test } from "@playwright/test";


test.beforeEach(async ({ request }) => {
  const response = await request.get("/api/sessions");
  if (!response.ok()) return;
  const sessions = await response.json() as Array<{ id: string }>;
  for (const session of sessions) {
    await request.delete(`/api/sessions/${session.id}`);
  }
});


test("completes the primary Agent Card workflow", async ({ page }, testInfo) => {
  const mobile = testInfo.project.name === "mobile";
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Build a structured Agent Card" })).toBeVisible();
  await expect(page.getByText(/Reporting completeness is separate from agent quality/)).toBeVisible();

  await page.getByRole("button", { name: /Describe an existing agent/ }).click();
  await expect(page.getByText(/This intake creates a structured AGENT-O Agent Card/)).toBeVisible();
  await expect(page.getByText("Card title", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: "More session actions" }).click();
  const renameDialog = page.getByRole("dialog", { name: "Rename session" });
  await renameDialog.getByRole("textbox", { name: "Session name" }).fill("E2E Agent Session");
  await renameDialog.getByRole("button", { name: "Save" }).click();
  await expect(page.getByRole("heading", { name: "E2E Agent Session" })).toBeVisible();

  const composer = page.getByRole("textbox", { name: "Message" });
  await composer.fill("card_title: E2E Agent Card");
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(page.getByText("Card version", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: /Review extracted facts/ }).click();
  await page.getByRole("button", { name: "Card metadata" }).click();
  await page.getByRole("button", { name: /Card title.*E2E Agent Card/ }).click();
  const editDialog = page.getByRole("dialog", { name: "Edit Card title" });
  await editDialog.getByRole("textbox", { name: "Reported value" }).fill("Reviewed E2E Agent Card");
  await editDialog.getByRole("button", { name: "Update field" }).click();
  await expect(page.getByText("Reviewed E2E Agent Card", { exact: true })).toBeVisible();

  if (mobile) {
    await page.getByRole("button", { name: "Issues", exact: true }).click();
    await page.getByRole("button", { name: "Run validation", exact: true }).click();
  } else {
    await page.getByRole("button", { name: "Validate", exact: true }).click();
  }
  await expect(page.getByText("Validation issues", { exact: true })).toBeVisible();
  await expect(page.getByText("Needs attention", { exact: true })).toBeVisible();
  await expect(page.getByText(/findings across \d+ data triples/)).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export", exact: true }).last().click();
  await page.getByRole("button", { name: /Download draft/ }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^agent-card-.*\.zip$/);

  await page.reload();
  await expect(page.getByRole("heading", { name: "E2E Agent Session" })).toBeVisible();
  await page.getByRole("button", { name: /Review extracted facts/ }).click();
  await page.getByRole("button", { name: "Card metadata" }).click();
  await expect(page.getByText("Reviewed E2E Agent Card", { exact: true })).toBeVisible();

  const viewportFits = await page.evaluate(
    () => document.documentElement.scrollWidth <= document.documentElement.clientWidth,
  );
  expect(viewportFits).toBe(true);
  await page.screenshot({ path: testInfo.outputPath("agent-card-workflow.png"), fullPage: true });

  await page.getByRole("button", { name: "Delete", exact: true }).click();
  const deleteDialog = page.getByRole("dialog", { name: "Delete session" });
  await deleteDialog.getByRole("button", { name: "Delete session" }).click();
  await expect(page.getByRole("heading", { name: "Build a structured Agent Card" })).toBeVisible();
});


test("supports keyboard-only session creation and message submission", async ({ page }) => {
  await page.goto("/");

  const mode = page.getByRole("button", { name: /Describe an existing agent/ });
  await mode.focus();
  await expect(mode).toBeFocused();
  await page.keyboard.press("Enter");

  const composer = page.getByRole("textbox", { name: "Message" });
  await expect(composer).toBeVisible();
  await composer.focus();
  await expect(composer).toBeFocused();
  await page.keyboard.type("card_title: Keyboard Agent Card");
  await page.keyboard.press("Enter");

  await expect(page.getByText("card_title: Keyboard Agent Card", { exact: true })).toBeVisible();
  await expect(page.getByText("Card version", { exact: true })).toBeVisible();
});


test("stops an active response without losing persisted input", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Describe an existing agent/ }).click();

  let releaseResponse!: () => void;
  let markPersisted!: () => void;
  const responseGate = new Promise<void>((resolve) => { releaseResponse = resolve; });
  const persisted = new Promise<void>((resolve) => { markPersisted = resolve; });

  await page.route("**/api/sessions/*/messages?stream=true", async (route) => {
    const response = await route.fetch();
    markPersisted();
    await responseGate;
    try {
      await route.fulfill({ response });
    } catch {
      // The browser request is expected to be gone after Stop response aborts it.
    }
  });

  const content = "card_title: Stopped Response Agent Card";
  await page.getByRole("textbox", { name: "Message" }).fill(content);
  await page.getByRole("button", { name: "Send message" }).click();
  await persisted;

  const stop = page.getByRole("button", { name: "Stop response" });
  await expect(stop).toBeVisible();
  await stop.click();
  releaseResponse();

  await expect(stop).toBeHidden();
  await expect(page.getByRole("alert")).toHaveCount(0);
  await page.reload();
  await expect(page.getByText(content, { exact: true })).toBeVisible();
  await expect(page.getByText("Card version", { exact: true })).toBeVisible();
});
