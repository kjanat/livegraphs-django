# Prettier for Django Templates

This project uses Prettier with the `prettier-plugin-django-annotations` plugin to format HTML templates with Django template syntax.

## Setup

The project is already configured with Prettier integration in pre-commit hooks. The configuration includes:

1. `.prettierrc` - Configuration file with Django HTML support
2. `.prettierignore` - Files to exclude from formatting
3. Pre-commit hook for automatic formatting on commits

### Manual Installation

To use Prettier locally (outside of pre-commit hooks), you'll need to install the dependencies:

```bash
# Using npm
npm install

# Or install just the required packages
npm install --save-dev prettier prettier-plugin-django-annotations
```

## Usage

### With Pre-commit

Prettier will automatically run as part of the pre-commit hooks when you commit changes.

To manually run the pre-commit hooks on all files:

```bash
pre-commit run prettier --all-files
```

### Using npm Scripts

The package.json includes npm scripts for formatting:

```bash
# Format all static files
npm run format

# Check formatting without modifying files
npm run format:check
```

### Command Line

You can also run Prettier directly:

```bash
# Format a specific file
npx prettier --write path/to/template.html

# Format all HTML files
npx prettier --write "dashboard_project/templates/**/*.html"
```

## VSCode Integration

For VSCode users, install the Prettier extension and add these settings to your `.vscode/settings.json`:

```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[html]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "prettier.requireConfig": true
}
```

## Ignoring Parts of Templates

If you need to prevent Prettier from formatting a section of your template:

```html
{# prettier-ignore #}
<div>This section will not be formatted by Prettier.</div>

<!-- prettier-ignore -->
<div>
    This works too.
</div>
```

## Django Template Support

The `prettier-plugin-django-annotations` plugin provides special handling for Django templates, including:

- Proper formatting of Django template tags (`{% %}`)
- Support for Django template comments (`{# #}`)
- Preservation of Django template variable output (`{{ }}`)
- Special handling for Django template syntax inside HTML attributes
