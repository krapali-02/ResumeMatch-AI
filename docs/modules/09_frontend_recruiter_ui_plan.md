# Module 09: Frontend Recruiter Workspace & UI/UX Implementation Plan

> **Module ID:** `MOD-09`  
> **Component:** Recruiter Web Application & Interactive Decision-Support UI  
> **Status:** Pending Implementation  
> **Traced Requirements:** SRS §8 (UI Requirements), §8.1 to §8.5, FR-JOB-03, FR-MATCH-05 to 07, FR-EVID-01 to 05, AC-01 to 07  

---

## 1. Module Overview & Purpose

Module 09 delivers a **React (TypeScript + Vite)** single-page application engineered to provide recruiters with an intuitive interface. It emphasizes transparent decision-support: displaying ranked candidates, component score breakdowns, granular matched/missing skill evidence, live resume previews, and pipeline transition tools without ever obscuring the underlying data.

---

## 2. Key Pages & Component Architecture

```
frontend/src/
├── pages/
│   ├── LoginPage.tsx             # Recruiter authentication & password reset
│   ├── DashboardPage.tsx         # Active jobs, candidate counts, recent match activity
│   ├── JobCreatePage.tsx         # Job Wizard: raw text entry & requirement tag editor
│   ├── JobDetailPage.tsx         # Single job view with candidate pool & match launcher
│   ├── CandidateRankingPage.tsx  # Ranked candidate cards, score meters, filter drawer
│   └── CandidateProfilePage.tsx  # Full candidate details, resume preview, notes timeline
├── components/
│   ├── common/
│   │   ├── Navbar.tsx            # Navigation, active user badge, logout
│   │   ├── ScoreMeter.tsx        # Visual circular/bar score component (0-100%)
│   │   ├── Badge.tsx             # Skill tag (green for matched, amber for missing)
│   │   └── Modal.tsx             # Accessible dialog container
│   ├── jobs/
│   │   ├── RequirementEditor.tsx # Interactive drag/toggle tag editor (Required vs Preferred)
│   │   └── WeightSlider.tsx      # Weight adjustment controls for ranking formula
│   ├── matching/
│   │   ├── CandidateCard.tsx     # Compact summary card with composite score & badges
│   │   ├── FilterSidebar.tsx     # Multi-facet filter (min score, exp, skills)
│   │   └── ScoreBreakdown.tsx    # Bar breakdown (Semantic, Skill, Experience, Education)
│   └── candidate/
│       ├── EvidenceInspector.tsx # Deep-dive modal showing supporting resume snippets
│       ├── ResumeViewer.tsx      # In-browser PDF/DOCX renderer (via iframe / PDF.js)
│       └── StatusDropdown.tsx    # Recruiter pipeline action (Shortlist, Hold, Reject)
```

---

## 3. UI/UX Design System & Ethical Safeguards

### 3.1 Ethical Score Representation
- **No False Certainty:** The composite score is styled as a "Fit Index", accompanied by an explicit advisory label:
  > *"AI scores assist human prioritization and do not represent a probability of hiring or definitive suitability."*
- **Color Coding:**
  - High match ($\ge 80\%$): Indigo / Emerald (`#10B981`)
  - Moderate match ($60\% - 79\%$): Blue / Slate (`#3B82F6`)
  - Low match ($< 60\%$): Amber (`#F59E0B`) — *Note: never colored alarming red, to avoid negative bias.*
- **Missing Information Badge:**
  - Labeled with neutral gray *"Not Mentioned"* rather than *"Deficient"* or *"Failed"* (AC-06).

---

## 4. Step-by-Step Implementation Tasks

- [ ] **Task 9.1:** Initialize React 18+ Vite project with TypeScript, Tailwind CSS, Lucide icons, and React Router v6.
- [ ] **Task 9.2:** Implement `AuthContext` and Axios interceptor for JWT storage and silent token refresh.
- [ ] **Task 9.3:** Build `DashboardPage.tsx` with high-level KPI cards (Active Jobs, Candidates Evaluated, Shortlisted).
- [ ] **Task 9.4:** Build `JobCreatePage.tsx` featuring raw JD input text area and the interactive `RequirementEditor` component (AC-01).
- [ ] **Task 9.5:** Build batch resume upload component with drag-and-drop, individual upload progress bars, and batch status polling (AC-02).
- [ ] **Task 9.6:** Build `CandidateRankingPage.tsx` with score sorting, dynamic filtering, and candidate comparison cards (AC-05).
- [ ] **Task 9.7:** Build `EvidenceInspector.tsx` displaying side-by-side view: matched skills with highlighted resume snippets and in-browser PDF viewer (FR-EVID-01, FR-EVID-04).
- [ ] **Task 9.8:** Integrate recruiter pipeline actions (Shortlist, Add Notes, Hold) with instantaneous UI optimistic updates.

---

## 5. Verification & Acceptance Checklist

- [ ] Recruiter can easily create a job and reclassify skills between Required and Preferred (AC-01).
- [ ] Batch resume uploads display progress and isolate failed files cleanly (AC-02, AC-08).
- [ ] Candidate card displays overall score and transparent component breakdown (AC-05).
- [ ] Clicking on any candidate opens the Evidence Inspector and resume viewer (FR-EVID-04).
- [ ] Low-scoring candidates remain fully accessible and editable (AC-07).
