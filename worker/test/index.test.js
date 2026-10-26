// Run with `node --test` (or `mise run worker-test`); no dependencies, GitHub is replaced by a stub.
import { test } from "node:test";
import assert from "node:assert/strict";
import worker, { issueBody } from "../src/index.js";

const env = { SITE_ORIGIN: "https://example.org", GITHUB_REPO: "your-org/content", GITHUB_TOKEN: "t0ken" };

function post(fields, origin = env.SITE_ORIGIN) {
  const body = new URLSearchParams(fields);
  return new Request("https://example.org/api/feedback", { method: "POST", body, headers: { Origin: origin } });
}

function stubGitHub(status = 201) {
  const calls = [];
  globalThis.fetch = async (url, init) => { calls.push({ url, init }); return new Response("{}", { status }); };
  return calls;
}

test("files an issue and redirects to the thanks page", async () => {
  const calls = stubGitHub();
  const res = await worker.fetch(post({ message: "Typo in the second paragraph", page: "/notes/a/" }), env);
  assert.equal(res.status, 303);
  assert.equal(res.headers.get("Location"), "https://example.org/thanks/");
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "https://api.github.com/repos/your-org/content/issues");
  assert.equal(JSON.parse(calls[0].init.body).title, "Feedback on /notes/a/");
});

test("refuses posts from other origins", async () => {
  const calls = stubGitHub();
  const res = await worker.fetch(post({ message: "hi", page: "/" }, "https://evil.example"), env);
  assert.equal(res.status, 403);
  assert.equal(calls.length, 0);
});

test("drops bots that fill the hidden field, without telling them", async () => {
  const calls = stubGitHub();
  const res = await worker.fetch(post({ message: "buy now", page: "/", website: "spam.example" }), env);
  assert.equal(res.status, 303);
  assert.equal(calls.length, 0);
});

test("rejects empty and oversized messages and odd paths", async () => {
  stubGitHub();
  assert.equal((await worker.fetch(post({ message: "  ", page: "/" }), env)).status, 400);
  assert.equal((await worker.fetch(post({ message: "x".repeat(2001), page: "/" }), env)).status, 400);
  assert.equal((await worker.fetch(post({ message: "hi", page: "//evil.example" }), env)).status, 400);
});

test("respects the rate limiter", async () => {
  const calls = stubGitHub();
  const limited = { ...env, FEEDBACK_LIMIT: { limit: async () => ({ success: false }) } };
  assert.equal((await worker.fetch(post({ message: "hi", page: "/" }), limited)).status, 429);
  assert.equal(calls.length, 0);
});

test("reports a GitHub failure as 502, never leaking the token", async () => {
  stubGitHub(500);
  const res = await worker.fetch(post({ message: "hi", page: "/" }), env);
  assert.equal(res.status, 502);
  assert.ok(!(await res.text()).includes("t0ken"));
});

test("quotes the message and defuses mentions", () => {
  assert.equal(issueBody("https://example.org/", "hi @octocat\nsecond"), "From a reader on https://example.org/\n\n> hi @​octocat\n> second\n");
});

test("only answers POST /api/feedback", async () => {
  assert.equal((await worker.fetch(new Request("https://example.org/api/other"), env)).status, 404);
  assert.equal((await worker.fetch(new Request("https://example.org/api/feedback"), env)).status, 405);
});
