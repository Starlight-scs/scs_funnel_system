

## What It Is

StoryFunnels is a campaign funnel platform that transforms static landing pages into guided, video-driven user experiences. Rather than presenting every visitor with the same generic content, the system routes users into tailored paths based on who they are and what they need — capturing qualified leads with meaningful context before the first conversation ever happens.

The platform sits at the intersection of video production and lead qualification, making it a natural extension for Starlight Creative Studios. Video is not decorative here — it is the functional engine of the intake system.

---

## The Core Problem It Solves

Traditional landing pages treat all visitors the same. A law firm, a financial advisory firm, or any multi-audience business ends up with a generic form fill and a phone number — no context, no qualification, no direction. The business then spends time on the phone doing intake work that the platform could have already handled.

StoryFunnels changes that by letting users self-identify, watch messaging tailored to their situation, and complete a structured assessment or CTA before any human interaction begins.

---

## How It Works

### The Admin Side

An admin logs into the platform and creates a **Campaign** — the top-level container for the entire funnel experience. Within that campaign, the admin:

- Sets the campaign name and slug
- Uploads a primary intro video
- Defines 3–5 **Branches**, each representing a specific audience type or user situation
- For each branch, configures a **Call to Action** (schedule a call, download a guide, start an assessment, etc.)
- Optionally builds a short **Assessment** of 5–6 questions to qualify leads before the first conversation

### The User Side

A visitor lands on the campaign page, watches the intro video, and sees a set of identity-based selection cards. They click the one that matches their situation. They are taken to a branch page with:

- A video speaking directly to their situation
- Messaging tailored to their emotional state and intent
- A clear next step (CTA)
- An optional assessment that helps them understand their own situation while giving the business structured intake data

When the user submits, the admin receives not just a name and phone number — but a lead with context: which path they took, what they said in the assessment, and what action they completed.

---

## Financial Advisor Use Case

This platform maps directly to the multi-audience recruiting and client acquisition challenge facing financial advisors at the management level. Instead of asking "what problem do you have?", the entry question becomes "who are you, and what are you looking for?"

### Campaign Entry

- Intro video: Vision of the firm, culture, growth, impact
- Headline: "There's a place for you here — let's find it."
- Selection cards leading into 4 branches

### Branch 1 — Career Changers

- Label: "Looking for a new career?"
- Video: Why people transition into advising, what the opportunity looks like
- Messaging: No prior experience required, training and mentorship, income potential, autonomy
- CTA: Take Career Fit Assessment
- Assessment: Current profession, income goals, comfort with client relationships, desire for autonomy, long-term goals
- Lead Tag: `career_changer_lead`

### Branch 2 — Interns and Early Talent

- Label: "Student or recent graduate?"
- Video: What it's like to start here, learning environment, growth track
- Messaging: Mentorship, exposure, path to becoming an advisor
- CTA: Apply for Internship or Download Program Overview
- Lead Tag: `intern_candidate`

### Branch 3 — Experienced Advisors

- Label: "Already an advisor?"
- Video: Why advisors make lateral moves, platform advantages, culture
- Messaging: Better support, improved payout structure, freedom, growth
- CTA: Schedule a Confidential Conversation
- Assessment (optional): Years of experience, current firm satisfaction, pain points
- Lead Tag: `advisor_recruit`

### Branch 4 — Potential Clients

- Label: "Looking for financial guidance?"
- Video: Trust, planning, long-term partnership
- Messaging: You don't have to figure this out alone
- CTA: Schedule a Consultation or Take Financial Health Assessment
- Assessment (optional): Financial goals, income range, current challenges
- Lead Tag: `client_lead`

---

## Full Tech Stack

### Frontend

|Layer|Technology|Purpose|
|---|---|---|
|Framework|Next.js (App Router)|Page routing, SSR/SSG, API consumption|
|Styling|Tailwind CSS|Utility-first responsive design|
|UI Components|shadcn/ui|Pre-built, accessible component library|
|Video Playback|Native HTML5 / React Player|Branch and intro video rendering|
|Form Handling|React Hook Form + Zod|Assessment and lead submission forms|
|State Management|React Context or Zustand|Branch selection state, funnel progress|
|HTTP Client|Axios or native Fetch|API calls to Django backend|

**Key Pages and Routes**

- `/[campaign]` — Campaign landing page with intro video and branch selection cards
- `/[campaign]/[branch]` — Branch-specific page with video, messaging, and CTA
- `/[campaign]/[branch]/assessment` — Multi-step assessment flow
- `/[campaign]/[branch]/success` — Submission confirmation page

**shadcn/ui Components in Use**

- `Card` — Branch selection cards on the campaign landing page
- `Button` — CTA triggers and form submissions
- `Progress` — Assessment step progress indicator
- `RadioGroup` / `Checkbox` — Multiple choice assessment questions
- `Input` / `Textarea` — Lead capture form fields
- `Dialog` — Confirmation modals
- `Badge` — Audience type labels in admin views

---

### Backend

|Layer|Technology|Purpose|
|---|---|---|
|Framework|Django 4.x|Core application logic and admin|
|API Layer|Django REST Framework|RESTful API serving the Next.js frontend|
|Database|PostgreSQL|Relational data storage|
|Admin UI|Django Admin|Campaign, branch, and lead management|
|Media Storage|Django + cloud storage (S3 or equivalent)|Video and file uploads|
|Auth|Django Auth + DRF Token Auth|Admin authentication|
|CORS|django-cors-headers|Allows Next.js frontend to consume API|

---

### Infrastructure

|Layer|Technology|Purpose|
|---|---|---|
|Frontend Hosting|Vercel|Next.js deployment and edge delivery|
|Backend Hosting|Railway, Render, or VPS|Django + Gunicorn deployment|
|Database Hosting|Supabase Postgres or Railway|Managed PostgreSQL|
|Media Storage|UploadThing|Video and asset uploads from the frontend|
|Environment Config|`.env.local` (frontend) / `.env` (backend)|Secrets and API keys|

---

### Development Tooling

|Tool|Purpose|
|---|---|
|TypeScript|Type safety across the Next.js frontend|
|ESLint + Prettier|Code formatting and linting|
|Black + Flake8|Python formatting and linting|
|Postman or Bruno|API testing during development|

---

## Backend Architecture (Django)

The platform is built on Django + Django REST Framework with a PostgreSQL database. Django Admin serves as the initial control center for campaign and content management. The frontend is Next.js, consuming a clean REST API.

### Core Models

|Model|Purpose|
|---|---|
|Campaign|Top-level funnel container|
|Branch|Audience-specific path within a campaign|
|CTA|Call to action per branch (type + config)|
|Assessment|Optional qualification questionnaire per branch|
|AssessmentQuestion|Individual questions tied to an assessment|
|LeadSubmission|Captured user data including campaign, branch, and CTA type|
|AssessmentResponse|User answers tied to a specific submission|

### Key Field: `audience_type`

Each Branch includes an `audience_type` field that enables segmentation, analytics, and CRM routing:

- `career_changer`
- `intern`
- `advisor`
- `client`

### API Endpoints (MVP)

- `GET /api/campaigns/:slug/` — Returns campaign + branches
- `GET /api/branches/:slug/` — Returns branch detail, CTA, and assessment
- `POST /api/leads/` — Submits a lead
- `POST /api/assessments/submit/` — Submits assessment responses

---

## Video Strategy

Each video is not standalone content — it is a directional tool inside the funnel. Every video follows a five-part framework:

1. **Acknowledge** — Show the viewer their situation is understood
2. **Normalize** — Remove fear or uncertainty
3. **Reframe** — Introduce a new perspective on their situation
4. **Position** — Explain how the firm supports them
5. **Invite** — Issue a clear, confident next step

### Production Specs

- Entry video: 60–90 seconds
- Branch videos: 45–75 seconds
- Style: Direct-to-camera, conversational, structured authenticity
- Support: Light B-roll, real environments, human interaction

---

## MVP Scope

- One campaign
- Up to 4 branches
- One CTA per branch
- Linear assessments only (no conditional branching yet)
- Lead capture and storage
- Django Admin as management UI

---

## Business Case for Starlight Creative Studios

This platform creates a productized offering that extends beyond single-engagement video production. The value proposition becomes:

> "We don't just create videos — we build systems that convert them into qualified leads."

StoryFunnels is repeatable across industries:

- Law firms (clients vs. referrals vs. recruits)
- Healthcare (patients vs. staff vs. partners)
- Real estate (buyers vs. sellers vs. agents)
- Financial services (clients vs. advisors vs. interns)

This positions Starlight Creative Studios not just as a production company but as a creative technology firm offering a recurring, scalable product.

---

## Future Expansion

- Multi-campaign dashboard
- Funnel analytics and conversion reporting
- A/B testing by branch
- CRM integrations (Salesforce, HubSpot)
- Email and SMS automation post-submission
- AI-driven personalization and recommendations
- Multi-tenant platform (Starlight OS)

---

## Strategic Summary

StoryFunnels turns storytelling into guided intake. It transforms video from passive content into a structured decision system — one that identifies the viewer, speaks to their situation, and moves them toward a meaningful next step before any human interaction is required.

For a financial advisory firm, it is both a recruiting engine and a client acquisition tool, unified inside a single campaign.

For Starlight Creative Studios, it is a productized platform with recurring revenue potential, built on existing strengths in video production and software development.