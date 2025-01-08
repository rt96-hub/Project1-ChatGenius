# Frontend Public Directory Documentation

## Overview
The `/frontend/public` directory contains static assets used throughout the ChatGenius application, primarily consisting of SVG icons and logos. These assets are directly accessible and used in various components of the application.

## Files

### 1. next.svg
- **Purpose**: Next.js framework logo
- **Usage**: Displayed on the homepage as the main framework identifier
- **Implementation**: Used in `src/app/page.tsx` with Next.js Image component
- **Properties**:
  - Dimensions: 180x38 pixels
  - Priority loading enabled
  - Dark mode support with invert class

### 2. vercel.svg
- **Purpose**: Vercel platform logo
- **Usage**: Used in the deployment section of the homepage
- **Implementation**: Implemented in `src/app/page.tsx` within the deployment link
- **Properties**:
  - Dimensions: 20x20 pixels
  - Dark mode support with invert class
  - Used alongside "Deploy now" text in button

### 3. file.svg
- **Purpose**: Documentation icon
- **Usage**: Used in the footer section for the "Learn" link
- **Implementation**: Implemented in `src/app/page.tsx` footer section
- **Properties**:
  - Dimensions: 16x16 pixels
  - Decorative (aria-hidden)
  - Used alongside "Learn" text

### 4. window.svg
- **Purpose**: Examples icon
- **Usage**: Used in the footer section for the "Examples" link
- **Implementation**: Implemented in `src/app/page.tsx` footer section
- **Properties**:
  - Dimensions: 16x16 pixels
  - Decorative (aria-hidden)
  - Used alongside "Examples" text

### 5. globe.svg
- **Purpose**: Website navigation icon
- **Usage**: Used in the footer section for the "Go to nextjs.org" link
- **Implementation**: Implemented in `src/app/page.tsx` footer section
- **Properties**:
  - Dimensions: 16x16 pixels
  - Decorative (aria-hidden)
  - Used alongside "Go to nextjs.org →" text

## Usage in Components

### Homepage Implementation (`src/app/page.tsx`)
All icons are implemented using Next.js's Image component for optimal performance and loading. Example:

```typescript
<Image
  className="dark:invert"
  src="/next.svg"
  alt="Next.js logo"
  width={180}
  height={38}
  priority
/>
```

### Dark Mode Support
- All icons support dark mode through the `dark:invert` Tailwind CSS class
- This ensures proper visibility in both light and dark themes

### Accessibility
- All decorative icons use `aria-hidden` attribute
- Proper alt text provided for meaningful images
- Icons used in links are accompanied by descriptive text

## Best Practices
1. Always use the Next.js Image component for optimal performance
2. Include appropriate alt text for accessibility
3. Implement dark mode support where needed
4. Maintain consistent dimensions for similar icon types
5. Use SVG format for scalability and quality

## Related Components
These assets are primarily used in:
- Homepage (`src/app/page.tsx`)
- Layout components
- Navigation elements
- Footer sections 