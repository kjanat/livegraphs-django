import bleach
from bleach.css_sanitizer import CSSSanitizer
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test the HTML sanitizer with CSS Sanitizer"

    def handle(self, *args, **options):  # noqa: ARG002
        # Create a test HTML string with various style attributes
        test_html = """
        <div style="color: red; background-color: yellow; transform: rotate(30deg);">
            <p style="font-size: 16px; margin: 10px;">
                This is a <span style="font-weight: bold; color: blue;">styled</span> paragraph.
            </p>
            <script>alert('XSS attack');</script>
            <a href="javascript:alert('Evil');" style="text-decoration: none;">Dangerous Link</a>
            <img src="x" onerror="alert('XSS')" style="border: 1px solid red;">
        </div>
        """

        # Create CSS sanitizer with allowed properties
        css_sanitizer = CSSSanitizer(
            allowed_css_properties=[
                "color",
                "background-color",
                "font-family",
                "font-size",
                "font-weight",
                "font-style",
                "text-decoration",
                "text-align",
                "margin",
                "margin-left",
                "margin-right",
                "margin-top",
                "margin-bottom",
                "padding",
                "padding-left",
                "padding-right",
                "padding-top",
                "padding-bottom",
                "border",
                "border-radius",
                "width",
                "height",
                "line-height",
            ]
        )

        # Clean the HTML
        cleaned_html = bleach.clean(
            test_html,
            tags=[
                "b",
                "i",
                "u",
                "em",
                "strong",
                "a",
                "br",
                "p",
                "ul",
                "ol",
                "li",
                "span",
                "div",
                "pre",
                "code",
                "blockquote",
            ],
            attributes={
                "a": ["href", "title", "target"],
                "span": ["style", "class"],
                "div": ["style", "class"],
                "p": ["style", "class"],
                "pre": ["style", "class"],
            },
            css_sanitizer=css_sanitizer,
            strip=True,
        )

        # Print the results
        self.stdout.write(self.style.SUCCESS("Original HTML:"))
        self.stdout.write(test_html)
        self.stdout.write("\n\n")
        self.stdout.write(self.style.SUCCESS("Cleaned HTML:"))
        self.stdout.write(cleaned_html)
        self.stdout.write("\n\n")

        # Check if unsafe attributes and styles were removed
        self.stdout.write(self.style.SUCCESS("Security Checks:"))

        if "script" not in cleaned_html:
            self.stdout.write(self.style.SUCCESS("✓ Script tags removed"))
        else:
            self.stdout.write(self.style.ERROR("✗ Script tags found"))

        if "javascript:" not in cleaned_html:
            self.stdout.write(self.style.SUCCESS("✓ JavaScript URLs removed"))
        else:
            self.stdout.write(self.style.ERROR("✗ JavaScript URLs found"))

        if "onerror" not in cleaned_html:
            self.stdout.write(self.style.SUCCESS("✓ Event handlers removed"))
        else:
            self.stdout.write(self.style.ERROR("✗ Event handlers found"))

        if "transform" not in cleaned_html:
            self.stdout.write(self.style.SUCCESS("✓ Unsafe CSS properties removed"))
        else:
            self.stdout.write(self.style.ERROR("✗ Unsafe CSS properties found"))

        if "img" not in cleaned_html:
            self.stdout.write(self.style.SUCCESS("✓ Unsupported tags removed"))
        else:
            self.stdout.write(self.style.ERROR("✗ Unsupported tags found"))
