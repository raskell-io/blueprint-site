// Reader feedback, the one thing this site cannot do with files: a POST from the form in every page's footer becomes
// a GitHub issue in the content repository, where it is moderated with everything else. The Worker holds one secret,
// GITHUB_TOKEN: a fine-grained token that can open issues in that one repository and nothing more.
//
// Bindings (wrangler.jsonc): vars SITE_ORIGIN and GITHUB_REPO ("owner/name"), secret GITHUB_TOKEN, and an optional
// rate limiter FEEDBACK_LIMIT. Every response is a redirect back to the site or a short plain-text error.

const MAX_MESSAGE = 2000;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== "/api/feedback") return text("Not found", 404);
    if (request.method !== "POST") return text("Use POST", 405, { Allow: "POST" });

    // Only the site's own pages may post here.
    if (request.headers.get("Origin") !== env.SITE_ORIGIN) return text("Forbidden", 403);

    if (env.FEEDBACK_LIMIT) {
      const ip = request.headers.get("CF-Connecting-IP") || "unknown";
      const { success } = await env.FEEDBACK_LIMIT.limit({ key: ip });
      if (!success) return text("Too many messages, try again in a minute", 429);
    }

    const form = await request.formData().catch(() => null);
    if (!form) return text("Expected a form", 400);
    const message = String(form.get("message") || "").trim();
    const page = String(form.get("page") || "/");
    // The hidden field people never see; anything that fills it is a bot. Pretend it worked.
    if (form.get("website")) return thanks(env);
    if (!message || message.length > MAX_MESSAGE) return text(`A message of 1 to ${MAX_MESSAGE} characters, please`, 400);
    if (!page.startsWith("/") || page.startsWith("//")) return text("Bad page", 400);

    const res = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/issues`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "site-feedback-worker",
      },
      body: JSON.stringify({
        title: `Feedback on ${page}`,
        body: issueBody(env.SITE_ORIGIN + page, message),
        labels: ["feedback"],
      }),
    });
    if (!res.ok) return text("Could not file the message, please try again later", 502);
    return thanks(env);
  },
};

// The message goes in as a quote, with @-mentions defused so a reader cannot ping people through the site.
export function issueBody(pageUrl, message) {
  const quoted = message.replace(/@/g, "@​").split("\n").map((l) => "> " + l).join("\n");
  return `From a reader on ${pageUrl}\n\n${quoted}\n`;
}

function thanks(env) {
  return new Response(null, { status: 303, headers: { Location: `${env.SITE_ORIGIN}/thanks/` } });
}

function text(body, status, headers = {}) {
  return new Response(body, { status, headers: { "Content-Type": "text/plain; charset=utf-8", ...headers } });
}
