# Prettier for Django/Jinja Templates

This project uses Prettier with the `prettier-plugin-jinja-template` plugin to format HTML templates with Django/Jinja syntax.

## Setup

To use Prettier with your Django templates, you'll need to install Prettier and the Jinja template plugin:

```bash
# Using npm
npm install --save-dev prettier prettier-plugin-jinja-template

# Or using yarn
yarn add --dev prettier prettier-plugin-jinja-template
```

## Usage

Once installed, you can format your Django templates using:

```bash
# Format a specific file
npx prettier --write path/to/template.html

# Format all HTML files
npx prettier --write "**/*.html"
```

### Without install

If you don't want to install the plugin, you can use the following command:

```bash
npx prettier --plugin=prettier-plugin-jinja-template --parser=jinja-template --write **/*.html
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
<div>
    This section will not be formatted
    by Prettier.
</div>

<!-- prettier-ignore -->
<div>
    This works too.
</div>
```
