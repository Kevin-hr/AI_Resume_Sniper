# � Product Requirement Document (PRD): AI Resume Sniper

> **Version**: 1.1 (Refined)
> **Status**: Development
> **Owner**: Digital Life Kha'Zix
> **Type**: Automation Asset (SaaS)

## 1. Product Overview (产品概览)

### 1.1 Vision (愿景)
To become the standard "Pre-Flight Check" for job seekers, providing a professional, automated, and unbiased HRBP-grade resume audit in under 60 seconds.

### 1.2 Core Value Proposition (核心价值)
*   **For Users**: Pass ATS filters and survive the "6-second HR scan".
*   **For Owner**: A fully automated, high-margin asset with zero marginal cost of replication.

### 1.3 Success Metrics (KPIs) - MVP
*   **Conversion Rate**: Visitor to Upload > 15%.
*   **Paid Conversion**: Free Report to Full Unlock > 5%.
*   **NPS**: User Satisfaction Score > 8/10.

---

## 2. User Stories (用户故事)

| ID | Persona | Trigger | Action | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| US-01 | **Desperate Job Seeker** | Receiving 0 interviews | Uploads Resume + JD | Receives a "Brutal Truth" score and realizes *why* they failed. |
| US-02 | **Career Switcher** | Unsure of transferable skills | Requests STAR Rewrite | Sees their past experience reframed into target role language. |
| US-03 | **Product Owner** | System runs automatically | Checks Dashboard | Sees revenue generated while sleeping. |

---

## 3. Functional Specifications (功能规格)

### 3.1 Core Workflow (The Engine)
1.  **Input Ingestion**: Parse PDF/Text Resume and JD Text.
2.  **Gap Analysis**: Compare Resume entities vs. JD requirements (Semantic Matching).
3.  **Prompt Engineering**: Inject "Senior HRBP" Persona context.
4.  **Report Generation**: Render Markdown report with quantitative scoring.

### 3.2 Data Models (Type Definitions)
*Adhering to "Abstract First" principle.*

```typescript
// Core Analysis Request
interface AnalysisRequest {
  resumeContent: string;
  jobDescription: string;
  mode: 'STRICT_HR' | 'CAREER_COACH';
}

// The Generated Report Structure
interface SniperReport {
  meta: {
    timestamp: number;
    modelUsed: string; // e.g., "DeepSeek-V3"
  };
  scores: {
    total: number; // 0-100
    keywordMatch: number; // ATS Impact
    impactScore: number; // STAR Quality
  };
  redFlags: string[]; // Critical issues to fix immediately
  starRewrites: {
    originalText: string;
    improvedText: string; // STAR format with metrics
    reasoning: string;
  }[];
  actionPlan: string[]; // Top 3 quick wins
}
```

---

## 4. Technical Architecture (技术架构)

### 4.1 Directory Structure
*Standardized project layout for easy replication.*

```text
AI_Resume_Sniper/
├── docs/
│   └── 01_Product_Requirement_Document.md   # This file
├── src/
│   ├── resume_sniper.py                     # Core Logic (The Kernel)
│   └── web_ui.py                            # Streamlit Interface (The Shell)
├── data/
│   ├── sample_resume_A.md                   # Test Input
│   ├── sample_jd_A.md                       # Test Input
│   └── sample_report_A.md                   # Golden Output
└── tests/
    └── integration_test.py                  # Verification Script
```

### 4.2 Tech Stack
*   **Frontend**: Streamlit (MVP) -> Next.js (V2)
*   **Backend**: Python (FastAPI/Streamlit runtime)
*   **AI Engine**: DeepSeek-V3 (via OpenAI-compatible API)
    *   *Base URL*: `https://api.deepseek.com`
    *   *Model*: `deepseek-chat`
    *   *Temperature*: 0.7 (Balanced creativity/precision)
*   **Infrastructure**: Localhost -> Streamlit Cloud / Vercel

### 4.3 Security & Privacy
*   **Data Retention**: No storage of user resumes in MVP (Stateless).
*   **API Security**: Environment variable management for API Keys.

---

## 5. Go-to-Market Strategy (GTM)

### 5.1 Pricing Strategy (3-Tier Ladder)
*   **Tier 1: Free Audit (Hook)**
    *   *Deliverable*: Overall Score + 1 Red Flag.
    *   *Goal*: Establish authority and create "Gap".
*   **Tier 2: Core Unlock (¥9.9)**
    *   *Deliverable*: Full Report (All Red Flags + Quick Fixes).
    *   *Goal*: Low-friction monetization.
*   **Tier 3: Premium Rewrite (¥19.9)**
    *   *Deliverable*: Everything in Tier 2 + **STAR Rewrites** + Interview Prediction.
    *   *Goal*: High-value asset delivery.

### 5.2 Content Strategy (Traffic)
*   **Channel**: Video Number / Bilibili.
*   **Content Type**: "Resume Rescue" Series (Short_Dopamine).
*   **Hook**: "I fixed this 30k resume in 10 seconds using AI."

---

## 6. Action Plan (执行计划)

- [x] **Kernel**: Develop `resume_sniper.py` (Completed).
- [x] **Interface**: Build `app.py` Web UI (Completed).
- [ ] **Deployment**: Deploy to public URL.
- [ ] **Payment**: Integrate payment gateway (WeChat/Alipay or Virtual Credits).

