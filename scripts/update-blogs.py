import requests
import re
from datetime import datetime

# Configuration
HOSTNAME = "gobinda.info.np"
README_PATH = "README.md"
MAX_POSTS = 5  # Number of posts to display

GRAPHQL_QUERY = """
query GetPublicationPosts($host: String!, $first: Int!, $after: String) {
  publication(host: $host) {
    posts(first: $first, after: $after) {
      edges {
        node {
          title
          slug
          brief
          publishedAt
        }
        cursor
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""


def fetch_posts():
    """Fetch posts using Hashnode's GraphQL API"""
    variables = {
        "host": HOSTNAME,
        "first": MAX_POSTS
    }

    response = requests.post(
        "https://gql.hashnode.com",
        json={"query": GRAPHQL_QUERY, "variables": variables},
        headers={"Content-Type": "application/json"}
    )

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}")

    data = response.json()
    print(data)
    if "errors" in data:
        errors = "\n".join([e["message"] for e in data["errors"]])
        raise Exception(f"GraphQL errors:\n{errors}")

    return [edge["node"] for edge in data["data"]["publication"]["posts"]["edges"]]


def update_readme(posts):
    """Update README with latest posts"""
    # Generate markdown content
    posts_md = []
    for post in posts:
        date = datetime.fromisoformat(post["publishedAt"].replace("Z", "+00:00"))
        formatted_date = date.strftime("%b %d, %Y")
        post_url = f"https://{HOSTNAME}/{post['slug']}"
        posts_md.append(f"- [{post['title']}]({post_url}) - {formatted_date}\n  \n  {post['brief']}")

    # Read current README
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Update blog section
    blog_content = "\n".join(posts_md)
    replacement = (
        "<!-- BLOG_START -->\n"
        f"{blog_content}\n"
        "<!-- BLOG_END -->"
    )

    updated_content = re.sub(
        r"<!-- BLOG_START -->.*<!-- BLOG_END -->",
        replacement,
        content,
        flags=re.DOTALL
    )

    # Debug: Verify substitution
    print("=== Updated Content ===")
    print(updated_content[:500])  # Print first 500 characters to verify

    # Write updated README
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)


if __name__ == "__main__":
    try:
        posts = fetch_posts()
        if posts:
            update_readme(posts)
            print("Successfully updated README!")
        else:
            print("No posts found")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
