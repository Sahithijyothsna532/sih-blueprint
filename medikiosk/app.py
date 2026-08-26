"""MediKiosk: clinical history acquisition and physician review assistant."""

import os
import sys
from pathlib import Path
from typing import Optional

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from ai_engine import apply_answer, extract_document, extract_initial_history, next_question
from schemas import ClinicalHistory, DocumentExtraction, Medication


st.set_page_config(page_title="MediKiosk", page_icon="+", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink:#173042; --muted:#647883; --teal:#087f82; --mint:#e6f5f0; --coral:#ed765f; --cream:#f7f5ef; --line:#d9e5e1; }
html, body, [class*="css"] { font-family:'DM Sans', sans-serif; color:var(--ink); }
.stApp { background:var(--cream); }
h1,h2,h3 { font-family:'Space Grotesk', sans-serif; letter-spacing:0; }
.hero { background:#173042; color:#f8f6ef; padding:2.2rem 2.4rem; border-radius:4px; margin-bottom:1.4rem; position:relative; overflow:hidden; }
.hero:after { content:''; position:absolute; width:220px; height:220px; border:1px solid #82d6c3; border-radius:50%; right:-45px; top:-100px; opacity:.55; }
.eyebrow { color:#82d6c3; text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; }
.hero h1 { font-size:2.8rem; margin:.3rem 0; color:#fff; }
.hero p { color:#d9e9e5; max-width:650px; margin:0; }
.metric { border-top:3px solid var(--teal); padding:.7rem 0; }
.metric strong { display:block; font:700 1.7rem 'Space Grotesk'; }
.metric span { color:var(--muted); font-size:.85rem; }
.panel { border:1px solid var(--line); background:#fff; padding:1.2rem 1.3rem; border-radius:4px; margin-bottom:1rem; }
.question { background:var(--mint); border-left:4px solid var(--teal); padding:1.1rem 1.3rem; font:600 1.25rem 'Space Grotesk'; margin:1rem 0; }
.chip { display:inline-block; background:#eef3f1; padding:.35rem .65rem; margin:.2rem .2rem 0 0; border-radius:20px; font-size:.82rem; }
.alert { background:#fff0eb; border-left:4px solid var(--coral); padding:.8rem 1rem; color:#8c3e2f; }
.small { color:var(--muted); font-size:.86rem; }
div[data-testid="stMetricValue"] { color:var(--teal); }
.stButton>button[kind="primary"] { background:var(--teal); border-color:var(--teal); }
</style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {"history": None, "document": None, "conversation": [], "started": False, "mode": "General Clinical"}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def list_value(value):
    if not value:
        return '<span class="small">Not provided</span>'
    return " ".join(f'<span class="chip">{item}</span>' for item in value)


def render_summary(history: ClinicalHistory, document: Optional[DocumentExtraction]):
    st.markdown("### Structured clinical history")
    left, right = st.columns(2)
    with left:
        st.markdown(f"**Chief complaint**  \n{history.chief_complaint}")
        st.markdown(f"**Onset / duration**  \n{history.onset} · {history.duration}")
        st.markdown(f"**Severity**  \n{history.severity}")
        st.markdown(f"**Aggravating factors**  \n{list_value(history.aggravating_factors)}", unsafe_allow_html=True)
        st.markdown(f"**Associated symptoms**  \n{list_value(history.associated_symptoms)}", unsafe_allow_html=True)
    with right:
        st.markdown(f"**Radiation**  \n{history.radiation}")
        st.markdown(f"**Past history**  \n{list_value(history.past_history)}", unsafe_allow_html=True)
        st.markdown(f"**Medications**  \n{list_value([m.name + ' · ' + m.dose for m in history.medications])}", unsafe_allow_html=True)
        st.markdown(f"**Allergies**  \n{history.allergies}")
    if history.red_flags:
        for flag in history.red_flags:
            st.markdown(f'<div class="alert">⚠ {flag}</div>', unsafe_allow_html=True)
    if document:
        st.markdown("#### Document evidence")
        st.caption(f"{document.source} · {document.document_date} · Physician verification required")
        st.write("Diagnoses:", ", ".join(document.diagnoses) or "Not provided")
        st.write("Investigations:", ", ".join(document.investigations) or "Not provided")
        st.write("Medications:", ", ".join(m.name + " " + m.dose for m in document.medications) or "Not provided")


def patient_view():
    st.markdown('<div class="hero"><div class="eyebrow">Patient intake · Demo patient MK-2048</div><h1>Tell us what brings you in.</h1><p>MediKiosk listens for the facts your clinician needs, then keeps the doctor in control of interpretation.</p></div>', unsafe_allow_html=True)
    mode = st.radio("History mode", ["General Clinical", "Ayurveda / AYUSH"], horizontal=True, index=0 if st.session_state.mode == "General Clinical" else 1)
    st.session_state.mode = mode
    if not st.session_state.started:
        st.markdown('<div class="panel"><span class="eyebrow">Start in your own words</span><h3>What is bothering you today?</h3></div>', unsafe_allow_html=True)
        statement = st.text_area("Patient statement", placeholder="Example: I have had chest pain since yesterday evening. It gets worse when I walk.", label_visibility="collapsed", height=110)
        if st.button("Begin intake", type="primary", use_container_width=True) and statement.strip():
            st.session_state.history = extract_initial_history(statement, mode.startswith("Ayur"))
            st.session_state.conversation = [("Patient", statement)]
            st.session_state.started = True
            st.rerun()
        st.info("Demo note: Gemini is optional. Without an API key, MediKiosk uses a transparent local prototype extractor.")
        return

    history = st.session_state.history
    question = next_question(history, mode.startswith("Ayur"))
    progress = min(100, int(len(history.answers) / 6 * 100))
    st.progress(progress, text=f"Intake progress · {len(history.answers)} details captured")
    if question:
        key, prompt = question
        st.markdown(f'<div class="question">{prompt}</div>', unsafe_allow_html=True)
        answer = st.text_input("Your answer", key=f"answer_{key}_{len(history.answers)}", label_visibility="collapsed")
        if st.button("Save answer", type="primary") and answer.strip():
            if mode.startswith("Ayur"):
                history.ayush[key] = answer
            else:
                apply_answer(history, key, answer)
            st.session_state.conversation.append(("Patient", answer))
            st.rerun()
    else:
        st.success("History captured. It is ready for physician review.")
    with st.expander("View captured facts"):
        render_summary(history, st.session_state.document)
    if st.button("Start over"):
        for key in ("history", "document", "conversation"):
            st.session_state[key] = None if key != "conversation" else []
        st.session_state.started = False
        st.rerun()


def documents_view():
    st.markdown("## Document intelligence")
    st.caption("Turn a previous prescription or report into evidence for the physician. Extracted facts remain marked for verification.")
    uploaded = st.file_uploader("Upload a document", type=["txt", "md", "pdf", "png", "jpg", "jpeg"])
    if uploaded and st.button("Extract document", type="primary"):
        if uploaded.type.startswith("text") or uploaded.name.endswith((".txt", ".md")):
            content = uploaded.getvalue().decode("utf-8", errors="ignore")
        else:
            content = "Uploaded medical document containing prescription details."
        st.session_state.document = extract_document(content, uploaded.name)
        st.success("Document structured. Physician verification is required.")
    if st.session_state.document:
        document = st.session_state.document
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(f"### {document.source}")
        st.markdown(f"**DOCUMENT DATE**  \n{document.document_date}")
        st.markdown(f"**DIAGNOSES**  \n{list_value(document.diagnoses)}", unsafe_allow_html=True)
        st.markdown(f"**MEDICATIONS**  \n{list_value([m.name + ' — ' + m.dose + ' — ' + m.frequency for m in document.medications])}", unsafe_allow_html=True)
        st.markdown(f"**INVESTIGATIONS**  \n{list_value(document.investigations)}", unsafe_allow_html=True)
        st.markdown('<div class="alert">⚠ Physician verification required before use in care.</div></div>', unsafe_allow_html=True)


def doctor_view():
    st.markdown("## Physician review")
    st.caption("A concise, editable handoff from patient conversation and document evidence.")
    if not st.session_state.history:
        st.warning("Complete a patient intake first, or use the Patient tab to load the demo flow.")
        return
    history = st.session_state.history
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    render_summary(history, st.session_state.document)
    st.divider()
    c1, c2 = st.columns([1, 1])
    with c1:
        st.checkbox("I have reviewed the extracted facts", key="reviewed")
    with c2:
        st.button("Confirm clinical history", type="primary", use_container_width=True, disabled=not st.session_state.get("reviewed", False))
    st.markdown('</div>', unsafe_allow_html=True)
    with st.expander("Patient conversation"):
        for speaker, text in st.session_state.conversation:
            st.write(f"**{speaker}:** {text}")


init_state()
with st.sidebar:
    st.markdown("# + MediKiosk")
    st.caption("Clinical history acquisition assistant")
    page = st.radio("Workspace", ["Patient intake", "Documents", "Doctor review"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Demo patient**")
    st.markdown("MK-2048 · New consultation")
    st.markdown('<div class="small">Facts are extracted, not diagnosed. The physician remains responsible for interpretation.</div>', unsafe_allow_html=True)

if page == "Patient intake":
    patient_view()
elif page == "Documents":
    documents_view()
else:
    doctor_view()
