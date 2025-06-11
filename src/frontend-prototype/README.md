# GTD Frontend Prototype

Modern, responsive frontend for the GTD (Getting Things Done) productivity system built with Next.js 14, React, TypeScript, and Tailwind CSS.

## 🚀 Features

### ✨ Core GTD Functionality
- **Quick Capture**: Instant task/project entry with keyboard shortcuts
- **Dashboard Overview**: Real-time productivity metrics and insights  
- **Today's Focus**: Prioritized task list for the current day
- **Weekly Planning**: Project scheduling and review system
- **Inbox Processing**: GTD workflow for organizing captured items
- **Smart Categorization**: Field-based organization system

### 🎨 Modern UI/UX
- **Dark/Light Mode**: System-aware theme switching
- **Responsive Design**: Mobile-first approach with desktop optimization
- **Accessibility**: WCAG compliant with keyboard navigation
- **Smooth Animations**: Framer Motion powered transitions
- **Progressive Web App**: Offline support and mobile installation

### ⚡ Performance & Developer Experience
- **Next.js 14**: App Router with React Server Components
- **TypeScript**: Full type safety and autocomplete
- **React Query**: Optimized data fetching and caching
- **Tailwind CSS**: Utility-first styling with custom design system
- **Hot Reload**: Instant development feedback

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Custom CSS Variables
- **State Management**: React Query (TanStack Query)
- **Forms**: React Hook Form + Zod validation
- **UI Components**: Headless UI + Radix UI primitives
- **Icons**: Heroicons
- **Animations**: Framer Motion
- **HTTP Client**: Axios with interceptors
- **Development**: ESLint, Prettier, TypeScript

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router pages
├── components/
│   ├── ui/                # Reusable UI components
│   ├── layout/            # Layout components
│   ├── gtd/               # GTD-specific components
│   └── providers/         # Context providers
├── lib/
│   ├── api.ts             # API client configuration
│   └── utils.ts           # Utility functions
├── types/
│   └── index.ts           # TypeScript type definitions
├── styles/
│   └── globals.css        # Global styles and CSS variables
├── hooks/                 # Custom React hooks
└── utils/                 # Helper utilities
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Running GTD Backend API

### Installation

1. **Clone and navigate to frontend**
   ```bash
   cd src/frontend-prototype
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env.local
   ```
   Edit `.env.local` with your backend API URL

4. **Start development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open in browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🔧 Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking

# Testing
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Generate coverage report
```

### Code Style

- **ESLint**: Enforces code quality and consistency
- **Prettier**: Automatic code formatting
- **TypeScript**: Strict type checking enabled
- **Tailwind**: Utility-first CSS with custom design tokens

## 🎨 Design System

### Color Palette
- **Primary**: Blue gradient (#0ea5e9 to #3b82f6)
- **GTD Contexts**: 
  - Inbox: Orange (#f59e0b)
  - Today: Red (#ef4444) 
  - Week: Blue (#3b82f6)
  - Projects: Green (#10b981)
  - Waiting: Gray (#6b7280)
  - Completed: Green (#22c55e)

### Typography
- **Font**: Inter (UI), Fira Code (monospace)
- **Scale**: Responsive typography with clamp()
- **Hierarchy**: Semantic heading levels

### Spacing & Layout
- **Grid**: CSS Grid and Flexbox
- **Breakpoints**: Mobile-first responsive design
- **Spacing**: Consistent 4px base unit

## 🔌 API Integration

### Backend Connectivity
- **Base URL**: Configurable via environment variables
- **Authentication**: JWT token with auto-refresh
- **Error Handling**: Centralized error management with toast notifications
- **Caching**: React Query for intelligent data caching
- **Optimistic Updates**: Immediate UI feedback

### Endpoints Used
- `GET /health` - Health check
- `GET /api/dashboard/stats` - Dashboard metrics  
- `GET /api/tasks/today` - Today's tasks
- `GET /api/projects/weekly` - Weekly projects
- `POST /api/quick-add` - Quick capture
- And more...

## 📱 PWA Features

### Offline Support
- Service Worker for caching
- Offline task creation and sync
- Background sync when connection restored

### Mobile Experience  
- Install prompt for home screen
- Full-screen mobile app experience
- Touch-optimized interactions
- Safe area handling for notched devices

## ♿ Accessibility

### WCAG Compliance
- Semantic HTML structure
- ARIA labels and descriptions
- Keyboard navigation support
- Screen reader optimization
- High contrast mode support

### Keyboard Shortcuts
- `Ctrl/Cmd + Enter`: Quick add
- `Escape`: Close modals/forms
- `Tab/Shift+Tab`: Navigation
- Arrow keys: List navigation

## 🚀 Deployment

### Build for Production
```bash
npm run build
npm run start
```

### Environment Variables
```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### Recommended Hosting
- **Vercel**: Optimal for Next.js (zero-config)
- **Netlify**: Great for static exports
- **Docker**: Containerized deployment
- **AWS/GCP/Azure**: Cloud platform deployment

## 📈 Performance

### Optimizations
- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Built-in bundle analyzer
- **Lazy Loading**: Component and route lazy loading
- **Caching**: React Query and HTTP caching

### Metrics
- **Core Web Vitals**: Optimized for performance scores
- **Lighthouse**: Regular performance auditing
- **Bundle Size**: Monitored and optimized

## 🤝 Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Include unit tests for components
4. Update documentation for API changes
5. Test accessibility compliance

## 📄 License

This project is part of the GTD system implementation.

---

**Built with ❤️ using modern web technologies for maximum productivity and user experience.**