# User Management & Authentication Strategy

This document defines the strategy for all aspects of the user lifecycle, from anonymous visitors to authenticated power users. It covers authentication, profiles, session management, and the operational processes for handling the "long tail" of user issues.

---

## 0. The Anonymous Experience: The Public Research Playground

Before a user commits to signing up, they must experience the magic.

### A. The Landing Page Experience

When a user visits `ariadne.ai`:
1. **Immediate Value:** A prominent search box in the center of the screen with the text: "Ask me anything. No login required."
2. **Example Queries:** Three compelling, clickable examples:
   - "What are the ethical implications of AI in healthcare?"
   - "Latest developments in quantum computing"
   - "How does the human microbiome affect mental health?"
3. **Live Demo:** Clicking an example or typing a query immediately triggers a research session *without* requiring authentication.

### B. The Anonymous Query Limitations

To prevent abuse while providing value:
- **Rate Limiting:** Anonymous users can run **3 queries per IP address per day**
- **Feature Subset:** They get:
  - ✅ A full, synthesized Tapestry with citations
  - ✅ A glimpse of The Loom (with only the nodes relevant to their query)
  - ❌ No memory (nothing is saved)
  - ❌ No editing or export
- **Progressive Disclosure:** After the 3rd query, a modal appears: "You've used your free queries for today. Create an account to unlock unlimited research, personal memory, and advanced features."

### C. The "Share a Public Tapestry" Feature

A user who has created a Tapestry can click "Share -> Get Public Link."
- This generates a unique, read-only URL: `ariadne.ai/t/abc123xyz`
- Anyone with the link can view the Tapestry, even without an account
- The viewer sees a "Researched with Ariadne" footer with a "Try Ariadne Free" CTA
- **Use Case:** Academics can share their literature reviews, analysts can share market reports

This creates a **viral loop**: Great content shared publicly drives new signups.

---

## 1. User States & Progression

We will design a seamless funnel that allows users to experience value before committing to an account, and then progressively unlocks features as they engage.

| State | Description | Access Level | Goal |
|---|---|---|---|
| **Anonymous** | A visitor who has not signed up. | Can view public Tapestries. Can run 1-3 demo queries. | Experience value, convert to signup |
| **Registered (Explorer Tier)** | User has signed up for a free account. | Full access to core research, memory, and The Loom. | Engage deeply, upgrade to paid |
| **Authenticated (Researcher Tier)** | User has a paid subscription. | Unlimited queries, advanced features, priority support. | Retain and expand usage |
| **Team Member** | User is part of a paid team plan. | Access to Shared Looms and collaboration features. | Build organizational adoption |

---

## 2. Authentication & Authorization (AuthN/AuthZ)

We will use a modern, token-based authentication system.

### A. Technology Stack
*   **Backend:** `python-jose` for JWT (JSON Web Token) handling.
*   **Frontend:** `Auth0` or `Clerk` as a managed authentication provider. This abstracts away the complexity of social logins, passwordless login, MFA, and security compliance.
*   **Database:** User credentials and profile data stored in our PostgreSQL operational DB.

### B. The Login Flow
1.  **User clicks "Login/Sign Up."** They are redirected to the Auth0/Clerk hosted login page.
2.  **User authenticates.** They can use Google, GitHub, or magic link via email.
3.  **Token Exchange.** Auth provider redirects back to our app with a temporary `code`. Our backend exchanges this code for a valid JWT.
4.  **Frontend Receives Token.** The JWT is stored securely (e.g., in `httpOnly` cookies). This token is sent with every subsequent API request.
5.  **Session Validation.** The backend validates the JWT on every request to a protected route.

### C. Authorization (Permissions)
We will implement a Role-Based Access Control (RBAC) system.
*   **Roles:** `explorer`, `researcher`, `team_member`, `team_admin`.
*   **Permissions:** A liste.g., ` of granular actions (can_run_query`, `can_create_shared_loom`, `can_manage_team_users`).
*   **Middleware:** A FastAPI middleware will check the user's role from the JWT token and validate if they have the required permission for a given API endpoint.

---

## 3. The User Profile

The user profile is their control panel for managing their identity and preferences.

| UI Element | Function | Interaction |
|---|---|---|
| **Profile Picture & Name** | Displays user's identity. | Clicking "Edit" allows them to upload a new picture or change their name. |
| **Email & Password Management** | Manages credentials. | "Change Password" and "Manage Social Logins" buttons. |
| **Subscription Status** | Shows current plan (Explorer, Researcher, Team) and billing cycle. | "Upgrade Plan" button links to the billing page. |
| **Persona Selection** | Allows user to change their behavioral persona. | Changing persona will trigger a "re-weighting" of their learning model, with a confirmation: "This will change how I prioritize sources. Are you sure?" |
| **API Keys** | For "Team" users. | Allows generation of API keys for programmatic access to Ariadne. |
| **Data & Privacy** | Links to the data retention and deletion policy. | "Download My Data" and "Delete My Account" buttons. |

---

## 4. Session Management & Resilience

A user's session must be seamless and resilient to interruptions.

*   **JWT Expiration:** JWTs will have a short expiration (e.g., 1 hour). The frontend will use a "refresh token" (a long-lived token stored securely) to silently get a new JWT in the background before the old one expires. The user should never be logged out unexpectedly.
*   **Concurrent Sessions:** A user can be logged in on multiple devices (laptop, phone). Each device gets its own JWT. The profile page will show "Active Sessions" with an option to "Log out from all other devices."
*   **Offline Detection:** The frontend will detect network loss. It will display a "You're offline" banner and continue to serve from the local cache (for offline-first features). When the connection returns, it will re-sync.

---

## 5. The "Long Tail" of User Issues: The Support Funnel

We will create a structured support system to handle the dozens of small but critical issues that arise.

### A. The In-App Help Hub
A searchable, context-aware help system.
*   **Contextual Help:** If a user is on the "Tapestry Export" page and clicks "Help," the help hub defaults to showing articles about exporting.
*   **Interactive Walkthroughs:** For new features, a guided tour can be started to show the user where to click.
*   **Video Tutorials:** Short, embedded videos for complex workflows like "Creating a Shared Loom."

### B. Categorization & Triage
All user-reported issues will be categorized to ensure they reach the right team.

| Category | Examples | Triage Path |
|---|---|---|
| **Bug Report** | "The Loom is not loading." "Export failed." | -> Engineering Team (via GitHub Issues) |
| **Billing Question** | "I was charged twice." "How do I cancel?" | -> Finance/Admin Team (via Intercom/Email) |
| **Feature Request** | "I wish you could export to PowerPoint." | -> Product Manager (via Canny/Productboard) |
| **Account Help** | "I can't log in." "I forgot my password." | -> Support Team (via Intercom/Email) |

### C. The "Copy for Every Question" Principle
Our support documentation will be written so that a user can copy-paste a question and find an immediate answer, reducing the need for human contact.

---

## 6. Analytics & Privacy

We need to understand user behavior without compromising privacy.

*   **Event-Based Analytics:** We will track events, not users.
    *   **Good:** `User performed a search`, `User created a Tapestry`, `User exported a report`.
    *   **Bad:** `User spent 15 minutes on the CRISPR page`. (This is PII and too invasive).
*   **Anonymous by Default:** All analytics data will be aggregated and anonymized by default. We will have a clear, one-click opt-out for all analytics in the user profile.
*   **Self-Hosted Option:** For "Team" and enterprise customers, we will offer the option to use a version of Ariadne with all third-party analytics and tracking completely disabled.

## 7. Database Schema

### User Table (PostgreSQL)
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    profile_picture_url TEXT,
    persona VARCHAR(50) DEFAULT 'academic',
    subscription_tier VARCHAR(50) DEFAULT 'explorer',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

### Session Table (PostgreSQL)
```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    jwt_token_hash VARCHAR(255),
    device_info JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

### Indexes for Performance
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
