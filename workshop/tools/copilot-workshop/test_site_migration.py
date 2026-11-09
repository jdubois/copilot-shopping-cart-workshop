"""Guard the standalone deployment contract and template-copy behavior."""
from pathlib import Path
import re
import unittest

SITE = Path(__file__).resolve().parents[2]
REPO = SITE.parent


class SiteMigrationTests(unittest.TestCase):
    def test_exact_chapter_routes_and_project_prefix(self):
        chapters = list(SITE.glob("*.md"))
        self.assertEqual(len(chapters), 17)
        for chapter in chapters:
            with self.subTest(chapter=chapter.name):
                source = chapter.read_text()
                slug = "" if chapter.stem == "index" else chapter.stem + "/"
                self.assertIn(f"permalink: /{slug}\n", source)
                self.assertNotIn("/workshops/copilot-app/", source)
                self.assertNotIn("jdubois/copilot-shopping-cart-workshop", source)
        config = (SITE / "_config.yml").read_text()
        self.assertIn('baseurl: "/github-copilot-app-java-workshop"', config)
        self.assertIn('url: "https://www.julien-dubois.com"', config)
        self.assertFalse((SITE / "CNAME").exists())

    def test_canonical_pages_is_gated_without_changing_learner_java_ci(self):
        workflow = (REPO / ".github/workflows/workshop-pages.yml").read_text()
        self.assertIn("if: github.repository == 'jdubois/github-copilot-app-java-workshop'", workflow)
        self.assertIn("github.event_name != 'pull_request' && github.ref == 'refs/heads/main'", workflow)
        self.assertIn("needs: build", workflow)
        self.assertIn("actions/deploy-pages@", workflow)
        self.assertIn("check-site.py --remote", workflow)
        self.assertIn("test-site.mjs", workflow)
        java = (REPO / ".github/workflows/test.yml").read_text()
        tests = java.split("  tests:", 1)[1].split("  reference-contracts:", 1)[0]
        self.assertNotIn("if:", tests.split("      - uses: actions/upload-artifact", 1)[0])
        self.assertIn("./mvnw -q test", tests)

    def test_readme_is_a_short_canonical_entry_point(self):
        readme = (REPO / "README.md").read_text()
        self.assertLessEqual(len(readme.splitlines()), 15)
        self.assertIn("https://www.julien-dubois.com/github-copilot-app-java-workshop/", readme)
        self.assertNotIn("```", readme)
        setup = (SITE / "setup.md").read_text()
        self.assertIn("https://github.com/jdubois/github-copilot-app-java-workshop", setup)
        self.assertIn("your new `cart-workshop` repository", setup)
        self.assertIn("Do not select the template owner's repository", setup)

    def test_theme_assets_are_prefixed_and_main_site_navigation_is_external(self):
        layout = (SITE / "_layouts/default.html").read_text()
        consent = (SITE / "_includes/analytics-consent.html").read_text()
        self.assertFalse(re.search(r'(?:href|src)="/(?!/)', layout + consent))
        nav = (SITE / "_includes/copilot-workshop-nav.html").read_text()
        self.assertIn('href="https://www.julien-dubois.com/conferences"', nav)
        for asset in ["/css/main.css", "/css/consent.css", "/js/main.js", "/favicon.ico"]:
            self.assertIn("'" + asset + "' | relative_url", layout)
        self.assertIn("'/js/analytics.js' | relative_url", consent)
        analytics = (SITE / "js/analytics.js").read_text()
        self.assertIn("var GA_ID = 'G-92TRR0HJMQ';", analytics)
        self.assertIn("var KEY = 'jdubois-analytics-consent';", analytics)


if __name__ == "__main__":
    unittest.main()
