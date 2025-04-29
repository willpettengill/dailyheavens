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

## Project Notes & Learnings

### API Interaction
- The frontend communicates with backend services (Birth Chart on port 8001, Interpretation on port 8002) via a Next.js API route (`/api/birth-chart`).
- This route acts as a proxy, fetching data from both backend services and combining them into a single response for the frontend.
- User birth data submitted on the home page (`app/page.tsx`) is sent to this API route.
- Successful responses are stored in `localStorage` (`birthChartData`, `userEmail`) to persist the data.
- The Dashboard page (`app/dashboard/page.tsx`) first checks `localStorage` for data. If none is found, it fetches default user data (currently hardcoded for `wwpettengill@gmail.com`).

### Frontend Errors & Fixes
- A `TypeError: Cannot read properties of undefined (reading 'map')` occurred specifically when switching to the "Interpretation" tab on the dashboard.
- **Cause:** Although the `interpretation.aspects` data was present in the initial API response, accessing it during the re-render triggered by the tab switch failed. This was likely due to temporary undefined states during rendering or potentially malformed aspect objects within the array.
- **Fix:** Implemented defensive programming in `app/dashboard/page.tsx`:
    - Added optional chaining (`?.`) and default values (`|| {}`, `|| []`) when destructuring data from the API response.
    - Added stricter checks within the `.filter()` method for the `aspects` array to ensure each aspect object is valid and has the required properties (`planet1`, `planet2`, `type`, `interpretation`) before mapping.
    - Added optional chaining and fallback values (`?? 'N/A'`, `?? 'No interpretation available'`) within the `.map()` method when accessing aspect properties for display.
- **Note:** While the frontend error is resolved, the underlying `interpretation` data structure from the backend API could be improved for consistency (e.g., ensuring all aspects always have a valid `type` and `interpretation`).

### Tailwind CSS v4 Configuration (Summary)
- **Correct Setup:**
    - Uses `@tailwindcss/postcss` plugin in `postcss.config.mjs`.
    - Uses `@import "tailwindcss";` in `app/globals.css`.
    - Requires a `tailwind.config.js` (or `.ts`, `.cjs`) file at the project root for basic configuration (content paths, theme extensions, plugins). Even a minimal config is needed for v4 compatibility.
    - Follows ShadCN UI guidelines for CSS variables (`hsl()` format) and theme structure (`@theme inline`) in `globals.css`.
    - `components.json` should reference the CSS file and base color.
- **Incorrect Setup / Common Issues:**
    - Missing `tailwind.config.js` file caused build errors.
    - Using old `@tailwind` directives instead of `@import "tailwindcss"`.
    - Incorrect CSS variable formats (e.g., using `oklch()` without proper setup) or misplaced `:root` / `.dark` selectors in `globals.css`.
    - Incompatible Tailwind version (v4) with configurations expecting v3 features (like specific package exports) led to errors like `Package path ./components is not exported`.

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

## Vercel Deployment Notes

- **Python Runtime:** Due to the `flatlib` dependency (specifically `pyswisseph`), this project requires the **Python 3.9** runtime on Vercel.
- **Node.js Version:** To ensure the correct build image with Python 3.9 is used, set the **Node.js Version** to **18.x** in the Vercel Project Settings (General tab).
