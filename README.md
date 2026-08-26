Patient talks → AI asks relevant questions → documents are scanned → AI creates a structured clinical history → doctor reviews it.

Recommended AI stack for MediKiosk

For a hackathon, I'd use this:

Component	Recommended	Cost for prototype
🧠 LLM / reasoning	Gemini API	Free tier
🎤 Speech-to-text	Bhashini / AI4Bharat or Gemini audio	Free/low-cost depending on API
🔊 Text-to-speech	Bhashini	Free/low-cost
📄 Document OCR	Google Gemini vision/document input initially	Free tier
🩺 Clinical structuring	Gemini + strict JSON schema	Free tier
🗄️ Database	Supabase	Free tier
🌐 Frontend	React / Next.js	Free
🚀 Deployment	Vercel	Free tier
🔐 Authentication	Supabase Auth	Free tier

The important part is that you don't need a separate AI model for every feature.

Use Gemini as the "brain"

For example:

Patient
   │
   ├── 🎤 Voice
   │
   ├── 👆 Touch
   │
   └── 📄 Medical documents
             │
             ▼
       Your Backend
             │
             ▼
        Gemini API
             │
      ┌──────┴──────┐
      ▼             ▼
 History         Documents
 Extraction      Extraction
      │             │
      └──────┬──────┘
             ▼
     Structured Patient
          History
             │
             ▼
       Doctor Dashboard

The killer demo

Don't just make a chatbot.

Make the judges see the before vs after.

Patient screen

Welcome 🙏

"What brings you to the hospital today?"

Patient says in Telugu/Hindi/English:

"I've had chest pain since yesterday evening. It gets worse when I walk."

Your AI extracts:

{
  "chief_complaint": "Chest pain",
  "onset": "Yesterday evening",
  "duration": "1 day",
  "aggravating_factors": ["Walking"],
  "severity": null,
  "radiation": null,
  "associated_symptoms": []
}


Then AI asks:

"Does the pain spread to your left arm, shoulder, jaw, or back?"

Patient answers.

The AI dynamically decides the next question.

That's much more impressive than simply having ChatGPT answer questions.

Your most important feature: Adaptive History Engine

This should be the centerpiece of your presentation.

Don't hard-code:

Question 1
Question 2
Question 3
Question 4
...


Instead:

Chief Complaint
       ↓
Clinical Ontology
       ↓
Determine missing information
       ↓
Generate next appropriate question
       ↓
Patient answer
       ↓
Update structured history
       ↓
Determine next question


For example:

Patient: "I have abdominal pain."

                    ↓

AI detects:
Abdominal pain
                    ↓

Ask → Location?
                    ↓
Ask → Onset?
                    ↓
Ask → Character?
                    ↓
Ask → Severity?
                    ↓
Ask → Relation to food?
                    ↓
Ask → Vomiting?
                    ↓
Ask → Bowel changes?
                    ↓
Ask → Fever?


Whereas if the patient says:

"I have a headache."

You follow a completely different pathway.

Don't let the LLM freely diagnose

This is very important for your hackathon architecture and presentation.

Your AI should be presented as:

Clinical history acquisition and summarization assistant

not:

❌ AI doctor
❌ Autonomous diagnosis system

The LLM should extract and organize what the patient says, while the physician remains responsible for interpretation.

For example:

Patient says:
"I take a tablet for BP every morning."

AI:

Medication:
- Indication: Hypertension
- Drug name: UNKNOWN
- Dose: UNKNOWN
- Frequency: Once daily


Don't let the AI invent the drug.

Similarly:

Patient says:
"My sugar was 240."

AI:

Investigation:
- Test: Blood glucose [exact test unspecified]
- Reported value: 240
- Unit: Not provided
- Source: Patient-reported
- Verification: Required


That kind of uncertainty preservation will make your project look much more medically responsible.

Document AI

For the hackathon, make a screen like:

Upload previous prescription

📄 prescription.jpg

Then show:

DOCUMENT DATE
12 Aug 2026

DIAGNOSES
• Hypertension
• Type 2 diabetes

MEDICATIONS
• Metformin — 500 mg — twice daily
• Amlodipine — 5 mg — once daily

INVESTIGATIONS
• HbA1c — 8.2%

SOURCE
Previous hospital prescription

⚠️ Physician verification required


Then your system puts it into:

PATIENT TIMELINE

2024 ───── 2025 ───── 2026
  │          │           │
Diagnosis   Surgery     Current
                       consultation


That visual timeline could be excellent for the demo.

Doctor dashboard

This is where you demonstrate the actual value.

Instead of the doctor receiving:

Patient enters
↓
Doctor asks 30 questions
↓
Doctor reads papers
↓
Doctor types notes


they see:

┌───────────────────────────────────────────┐
│ PATIENT SUMMARY                            │
├───────────────────────────────────────────┤
│ Chief Complaint                           │
│ Chest pain × 1 day                        │
│                                           │
│ HPI                                       │
│ • Started yesterday evening               │
│ • Worse with walking                      │
│ • Radiation: Denied                       │
│ • Dyspnoea: Present                       │
│                                           │
│ Past History                              │
│ • Hypertension                            │
│                                           │
│ Medications                               │
│ • Amlodipine 5 mg OD [from document]      │
│                                           │
│ Allergies                                 │
│ • No known allergies reported             │
│                                           │
│ ⚠️ RED FLAG                               │
│ Chest pain + dyspnoea                     │
│ Priority triage recommended               │
│                                           │
│ [ EDIT ] [ CONFIRM ]                      │
└───────────────────────────────────────────┘


The doctor can then edit/confirm everything.

For AYUSH — this can differentiate you

Since the organizers specifically mention AYUSH, don't ignore it.

Add an "Ayurveda Mode" toggle:

☑ General Clinical History

☐ Ayurveda / AYUSH History


Then your AI switches to the appropriate questionnaire.

For example:

AYUSH HISTORY

Prakriti
Vikriti
Sara
Samhanana
Pramana
Satmya
Sattva
Ahara Shakti
Vyayama Shakti
Vaya

Ahara
Vihara
Nidana


This gives you a strong answer to:

"Why isn't this just another generic medical chatbot?"

Your answer:

Because MediKiosk is a structured clinical intake system designed around Indian hospital workflows and supports both conventional and AYUSH history-taking.

What I would NOT build for the hackathon

Don't spend your limited time implementing all of these:

Full ABDM production integration
Real hospital HIS integration
Aadhaar authentication
Production-grade FHIR infrastructure
Every Indian language
Perfect handwritten OCR
Full medical diagnosis
Real patient deployment
Complex EMR infrastructure

Instead, mock the integrations.

For example:

ABHA
1234-5678-9012

Consent:
✓ History collection
✓ Document processing
✓ Physician sharing

FHIR Export
[ Generate FHIR Bundle ]


You can demonstrate the concept without needing a live hospital system.

Your MVP architecture

I'd build:

                ┌─────────────────┐
                │   React / Next  │
                │   Patient UI    │
                └────────┬────────┘
                         │
                 REST / WebSocket
                         │
                         ▼
                ┌─────────────────┐
                │ Node.js / Python│
                │    Backend      │
                └────────┬────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Gemini API      Speech API      OCR/Doc AI
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                ┌─────────────────┐
                │ Clinical Schema │
                │    / JSON       │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │   Supabase DB   │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │ Doctor Dashboard│
                └─────────────────┘

One thing I'd change in your original proposal

Your problem statement says:

"ABHA ID or Aadhaar details"

For your prototype, don't make Aadhaar a core requirement. Keep identity/consent modular and use a mock ABHA/demo patient identifier. This reduces privacy/security complexity and keeps the demo focused on your actual innovation.

If I were building this for the hackathon

I'd prioritize these 5 features:

🎤 Multilingual voice conversation
🧠 Adaptive clinical questioning
📄 Prescription/report upload + extraction
🩺 Structured physician summary + red-flag highlighting
🌿 AYUSH history mode

And I'd make the entire patient flow take 2–3 minutes in the demo.

The winning moment is when the judge sees:

Patient speaks naturally → AI conducts the right history → old documents become structured data → doctor instantly receives a clean clinical summary.

That demonstrates the actual solution rather than just demonstrating an LLM.

If you tell me your team size + hackathon duration (e.g. 24h/36h/48h) + whether you're using React/Flutter/etc., I can map out exactly what to build hour-by-hour and which free APIs to use.
