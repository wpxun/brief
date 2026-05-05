export default {
  async scheduled(event, env, ctx) {
    const GITHUB_TOKEN = env.GITHUB_TOKEN; // Set this in Cloudflare Worker Settings -> Variables
    const REPO_OWNER = "wpxun"; // GitHub username
    const REPO_NAME = "brief";
    const WORKFLOW_ID = "daily_news.yml";

    console.log(`Attempting to trigger GitHub Action for ${REPO_OWNER}/${REPO_NAME}...`);

    const response = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/${WORKFLOW_ID}/dispatches`,
      {
        method: "POST",
        headers: {
          "Accept": "application/vnd.github+json",
          "Authorization": `Bearer ${GITHUB_TOKEN}`,
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "Cloudflare-Worker-Trigger"
        },
        body: JSON.stringify({
          ref: "main" 
        })
      }
    );

    if (response.ok) {
      console.log("GitHub Action triggered successfully!");
    } else {
      const error = await response.text();
      console.error("Failed to trigger GitHub Action:", error);
      // You can throw an error here if you want Cloudflare to log a failure
      throw new Error(`GitHub API returned ${response.status}: ${error}`);
    }
  },

  // Optional: Allow manual testing by visiting the Worker URL in a browser
  async fetch(request, env, ctx) {
    return new Response("Cloudflare Worker is running. This worker is designed to be triggered by a Cron Schedule.");
  }
};
