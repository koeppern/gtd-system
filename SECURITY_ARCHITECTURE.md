# Security Architecture - GTD Project

## 🔒 Core Security Principles

### **RULE #1: Frontend never communicates directly with Python Backend**

```
❌ FORBIDDEN:
Frontend → Python Backend (Direct)

✅ REQUIRED:
Frontend → Next.js API Routes → Python Backend
```

### **RULE #2: All credentials are server-side only**

- **NO** API keys, secrets, or tokens in client-side code
- **NO** environment variables exposed to browser
- **ALL** authentication handled server-side in Next.js API routes

### **RULE #3: Next.js API Routes as Security Proxy**

Every backend request must go through a Next.js API route that:
1. Handles authentication server-side
2. Validates user permissions
3. Adds necessary credentials
4. Proxies to Python backend
5. Sanitizes response before sending to client

## 📁 Project Structure

```
src/frontend/
├── src/app/api/              # Next.js API Routes (Server-Side)
│   ├── dashboard/stats/      # Dashboard proxy
│   ├── projects/            # Projects proxy
│   ├── tasks/               # Tasks proxy
│   └── auth/                # Authentication
├── src/lib/
│   ├── api.ts               # Client-side API (calls Next.js routes only)
│   └── backend-client.ts    # Server-side Python backend client
└── src/components/          # React components (client-side)
```

## 🔐 Implementation Examples

### ✅ Correct: Next.js API Route (Server-Side)

```typescript
// src/app/api/dashboard/stats/route.ts
import { backendApi } from '@/lib/backend-client';

export async function GET(request: NextRequest) {
  // Server-side authentication
  const session = await getServerSession(request);
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Fetch from Python backend with credentials
  const stats = await backendApi.dashboard.getStats(session.user.id);
  
  return NextResponse.json(stats);
}
```

### ✅ Correct: Client-Side API Call

```typescript
// Frontend component
const { data: stats } = useQuery({
  queryKey: ['dashboard', 'stats'],
  queryFn: () => api.dashboard.getStats(), // Calls Next.js API route
});
```

### ❌ FORBIDDEN: Direct Backend Call

```typescript
// NEVER DO THIS:
const response = await fetch('http://backend:8000/api/dashboard/stats');
```

## 🌐 Environment Variables

### Client-Side (.env.local)
```bash
# ONLY public variables, no secrets
NEXT_PUBLIC_APP_NAME=GTD
NEXT_PUBLIC_VERSION=1.0.0
```

### Server-Side (.env.local)
```bash
# Backend configuration (server-only)
BACKEND_URL=http://localhost:8000
BACKEND_SERVICE_KEY=secret-key-for-backend-auth
DEFAULT_USER_ID=00000000-0000-0000-0000-000000000001

# Database credentials (server-only)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-secret-key

# Authentication (server-only)
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

## 🔒 Authentication Flow

```
1. User logs in → Next.js handles auth → Session stored server-side
2. Client makes request → Next.js API route
3. API route validates session → Extracts user ID
4. API route calls Python backend with server credentials + user context
5. Response sanitized and returned to client
```

## 🚫 What NEVER appears in browser

- Database connection strings
- API keys or service tokens  
- Backend URLs or internal endpoints
- User credentials or session tokens
- Internal service communications

## ✅ What's safe for browser

- Public configuration (app name, version)
- Sanitized API responses
- Client-side routing
- UI state and preferences

## 🛡️ Security Checklist

- [ ] All API calls go through Next.js API routes
- [ ] No direct Python backend communication from client
- [ ] All credentials stored server-side only
- [ ] Environment variables properly scoped
- [ ] Authentication handled server-side
- [ ] Responses sanitized before client delivery
- [ ] No secrets in client-side code or network requests

## 🔧 Development Guidelines

### For Cursor AI / Development

When implementing new features:

1. **Always create Next.js API route first** (`src/app/api/...`)
2. **Handle auth and credentials server-side**
3. **Use `backend-client.ts` for Python backend calls**
4. **Update `api.ts` for client-side interface**
5. **Never expose backend URLs to client**

### Code Review Checklist

- ❌ Check for direct backend URLs in client code
- ❌ Check for credentials in client-side variables
- ❌ Check for environment variables with secrets in client
- ✅ Verify all API calls go through Next.js routes
- ✅ Verify server-side authentication
- ✅ Verify credential isolation

---

**Remember: If it touches the Python backend, it must go through a Next.js API route!**