This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Tailwind CSS v4 Configuration

This project uses Tailwind CSS v4 with the following setup:

### PostCSS Configuration
```js
// postcss.config.mjs
const config = {
  plugins: ["@tailwindcss/postcss"],
};

export default config;
```

### CSS Configuration
The project uses the new Tailwind v4 import syntax in `app/globals.css`:
```css
@import "tailwindcss";
```

### Important Notes
- We use the CSS-first approach introduced in Tailwind v4
- Theme configuration is done using `@theme inline` in globals.css
- Dark mode is configured using `@custom-variant dark`
- No JavaScript-based Tailwind config is needed
- The project uses ShadCN UI components which are compatible with Tailwind v4

### Troubleshooting
If you encounter styling issues:
1. Ensure you're using `@import "tailwindcss"` instead of the old `@tailwind` directives
2. Check that `@tailwindcss/postcss` is the only Tailwind-related PostCSS plugin
3. Make sure your theme variables are defined within `@theme inline`
4. For component styles, use CSS variables (e.g., `var(--color-primary)`) instead of direct color values

### Browser Support
Tailwind CSS v4 requires modern browsers:
- Safari 16.4+
- Chrome 111+
- Firefox 128+

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
