# AI RMF audit: Lakeview Community Bank (fictional)

Assessed 2026-09-30 | Generated 2026-10-07 18:17 UTC | ai_rmf 0.1.0

- Overall maturity: **30 / 100 (Developing)**
- AI systems: **7** (2 high, 4 medium, 1 low risk; 6 from vendors; 4 generative)
- Gaps: **33** (1 critical, 16 high, 11 medium, 5 low)

## Maturity by function

| Function | Practices | Systems | Score | Level |
|---|---|---|---|---|
| Govern | 10 | 86 | **48** | Developing |
| Map | 25 | 31 | **28** | Developing |
| Measure | 21 | 29 | **25** | Developing |
| Manage | 14 | 21 | **18** | Initial |

## AI system inventory

| System | Vendor | Risk tier | Checks passed | Gaps |
|---|---|---|---|---|
| Resume screening tool | TalentSift | High | 0 of 8 | 8 |
| Loan pre-qualification model | internal | High | 5 of 8 | 3 |
| Customer service chatbot | HelpBot Cloud | Medium | 1 of 9 | 8 |
| Marketing copy generator | WriteWell AI | Medium | 2 of 8 | 6 |
| Meeting transcription | NoteStream | Medium | 1 of 7 | 6 |
| Fraud alert scoring | FinGuard | Medium | 8 of 8 | 0 |
| Code assistant | CodePilot | Low | 1 of 3 | 2 |

## Gaps

- **CRITICAL** Resume screening tool (High): Decisions about people made without human review. Makes consequential decisions about people with no human review before they take effect. Fix: Require a person to review and be able to override the AI output before it affects anyone. _(MAP 3.5, MANAGE 2.4; GAI: Human-AI Configuration)_
- **HIGH** Loan pre-qualification model (High): No impact assessment. Impact assessment is 837 days old (last 2024-06-15). Fix: Assess who the system affects, how, and what could go wrong, and record the decision to deploy. _(MAP 5.1, MAP 1.1)_
- **HIGH** Loan pre-qualification model (High): Not evaluated for harmful bias. Uses personal data to inform decisions but has not been tested for harmful bias. Fix: Test outcomes across relevant groups before use and periodically after; ask the vendor for its bias testing evidence. _(MEASURE 2.11; GAI: Harmful Bias and Homogenization)_
- **HIGH** Resume screening tool (High): No accountable owner. No named owner is accountable for this system. Fix: Name a business owner who is accountable for the system's use, risks, and outcomes. _(GOVERN 2.1)_
- **HIGH** Resume screening tool (High): No impact assessment. High-risk system with no impact assessment on file. Fix: Assess who the system affects, how, and what could go wrong, and record the decision to deploy. _(MAP 5.1, MAP 1.1)_
- **HIGH** Resume screening tool (High): Not evaluated for harmful bias. Uses personal data to inform decisions but has not been tested for harmful bias. Fix: Test outcomes across relevant groups before use and periodically after; ask the vendor for its bias testing evidence. _(MEASURE 2.11; GAI: Harmful Bias and Homogenization)_
- **HIGH** Resume screening tool (High): Vendor AI not reviewed. Supplied by TalentSift; no AI risk review of the vendor. Fix: Review the vendor's AI documentation, data handling, and security terms before and after deployment. _(GOVERN 6.1, MANAGE 3.1; GAI: Value Chain and Component Integration)_
- **HIGH** Customer service chatbot (Medium): No impact assessment. Medium-risk system with no impact assessment on file. Fix: Assess who the system affects, how, and what could go wrong, and record the decision to deploy. _(MAP 5.1, MAP 1.1)_
- **HIGH** Customer service chatbot (Medium): Vendor AI not reviewed. Supplied by HelpBot Cloud; no AI risk review of the vendor. Fix: Review the vendor's AI documentation, data handling, and security terms before and after deployment. _(GOVERN 6.1, MANAGE 3.1; GAI: Value Chain and Component Integration)_
- **HIGH** Customer service chatbot (Medium): Vendor may use your data to train its models. HelpBot Cloud terms do not stop it from using your personal data to train its models. Fix: Use an enterprise agreement or setting that prohibits training on your data, or keep personal data out of the tool. _(MEASURE 2.10, MAP 4.1; GAI: Data Privacy, Information Security)_
- **HIGH** Customer service chatbot (Medium): Generative output reaches customers without review. Generated content reaches customers without human review. Fix: Limit the system to approved sources, add guardrails, and route sensitive or uncertain answers to a person. _(MEASURE 2.5, MANAGE 2.4; GAI: Confabulation, Information Integrity)_
- **HIGH** Marketing copy generator (Medium): No impact assessment. Medium-risk system with no impact assessment on file. Fix: Assess who the system affects, how, and what could go wrong, and record the decision to deploy. _(MAP 5.1, MAP 1.1)_
- **HIGH** Marketing copy generator (Medium): Generative output reaches customers without review. Generated content reaches customers without human review. Fix: Limit the system to approved sources, add guardrails, and route sensitive or uncertain answers to a person. _(MEASURE 2.5, MANAGE 2.4; GAI: Confabulation, Information Integrity)_
- **HIGH** Meeting transcription (Medium): No impact assessment. Medium-risk system with no impact assessment on file. Fix: Assess who the system affects, how, and what could go wrong, and record the decision to deploy. _(MAP 5.1, MAP 1.1)_
- **HIGH** Meeting transcription (Medium): Vendor AI not reviewed. Supplied by NoteStream; no AI risk review of the vendor. Fix: Review the vendor's AI documentation, data handling, and security terms before and after deployment. _(GOVERN 6.1, MANAGE 3.1; GAI: Value Chain and Component Integration)_
- **HIGH** Meeting transcription (Medium): Vendor may use your data to train its models. NoteStream terms do not stop it from using your personal data to train its models. Fix: Use an enterprise agreement or setting that prohibits training on your data, or keep personal data out of the tool. _(MEASURE 2.10, MAP 4.1; GAI: Data Privacy, Information Security)_
- **HIGH** Code assistant (Low): Vendor AI not reviewed. Supplied by CodePilot; no AI risk review of the vendor. Fix: Review the vendor's AI documentation, data handling, and security terms before and after deployment. _(GOVERN 6.1, MANAGE 3.1; GAI: Value Chain and Component Integration)_
- **MEDIUM** Loan pre-qualification model (High): No AI incident process. No process for reporting and handling incidents involving this system. Fix: Define how AI errors and harms are reported, investigated, and communicated, and who can pause the system. _(MANAGE 4.3)_
- **MEDIUM** Resume screening tool (High): Not monitored in production. Not monitored in production for errors, drift, or misuse. Fix: Define what good performance looks like and review errors, complaints, and drift on a schedule. _(MEASURE 2.4, MANAGE 4.1)_
- **MEDIUM** Resume screening tool (High): No AI incident process. No process for reporting and handling incidents involving this system. Fix: Define how AI errors and harms are reported, investigated, and communicated, and who can pause the system. _(MANAGE 4.3)_
- **MEDIUM** Customer service chatbot (Medium): Not monitored in production. Not monitored in production for errors, drift, or misuse. Fix: Define what good performance looks like and review errors, complaints, and drift on a schedule. _(MEASURE 2.4, MANAGE 4.1)_
- **MEDIUM** Customer service chatbot (Medium): People are not told they are interacting with AI. Customers are not told they are interacting with AI. Fix: Tell customers and users when they are interacting with AI or receiving AI-generated content. _(MEASURE 2.8; GAI: Human-AI Configuration)_
- **MEDIUM** Customer service chatbot (Medium): No AI incident process. No process for reporting and handling incidents involving this system. Fix: Define how AI errors and harms are reported, investigated, and communicated, and who can pause the system. _(MANAGE 4.3)_
- **MEDIUM** Marketing copy generator (Medium): Not monitored in production. Not monitored in production for errors, drift, or misuse. Fix: Define what good performance looks like and review errors, complaints, and drift on a schedule. _(MEASURE 2.4, MANAGE 4.1)_
- **MEDIUM** Marketing copy generator (Medium): People are not told they are interacting with AI. Customers are not told they are interacting with AI. Fix: Tell customers and users when they are interacting with AI or receiving AI-generated content. _(MEASURE 2.8; GAI: Human-AI Configuration)_
- **MEDIUM** Marketing copy generator (Medium): No AI incident process. No process for reporting and handling incidents involving this system. Fix: Define how AI errors and harms are reported, investigated, and communicated, and who can pause the system. _(MANAGE 4.3)_
- **MEDIUM** Meeting transcription (Medium): Not monitored in production. Not monitored in production for errors, drift, or misuse. Fix: Define what good performance looks like and review errors, complaints, and drift on a schedule. _(MEASURE 2.4, MANAGE 4.1)_
- **MEDIUM** Meeting transcription (Medium): No AI incident process. No process for reporting and handling incidents involving this system. Fix: Define how AI errors and harms are reported, investigated, and communicated, and who can pause the system. _(MANAGE 4.3)_
- **LOW** Resume screening tool (High): Purpose and limits not documented. Intended purpose, known limits, and out-of-scope uses are not documented. Fix: Document the intended purpose, users, inputs, known limitations, and uses that are not allowed. _(MAP 1.1, MAP 2.2)_
- **LOW** Customer service chatbot (Medium): Purpose and limits not documented. Intended purpose, known limits, and out-of-scope uses are not documented. Fix: Document the intended purpose, users, inputs, known limitations, and uses that are not allowed. _(MAP 1.1, MAP 2.2)_
- **LOW** Marketing copy generator (Medium): Purpose and limits not documented. Intended purpose, known limits, and out-of-scope uses are not documented. Fix: Document the intended purpose, users, inputs, known limitations, and uses that are not allowed. _(MAP 1.1, MAP 2.2)_
- **LOW** Meeting transcription (Medium): Purpose and limits not documented. Intended purpose, known limits, and out-of-scope uses are not documented. Fix: Document the intended purpose, users, inputs, known limitations, and uses that are not allowed. _(MAP 1.1, MAP 2.2)_
- **LOW** Code assistant (Low): Purpose and limits not documented. Intended purpose, known limits, and out-of-scope uses are not documented. Fix: Document the intended purpose, users, inputs, known limitations, and uses that are not allowed. _(MAP 1.1, MAP 2.2)_

## Program practices

| ID | Function | AI RMF | Practice | Answer |
|---|---|---|---|---|
| G-01 | Govern | GOVERN 1.1 | Legal and regulatory requirements that apply to the organization's use of AI have been identified. | partial |
| G-02 | Govern | GOVERN 1.2 | An approved AI use policy sets out acceptable uses, prohibited uses, and approval requirements. | no |
| G-03 | Govern | GOVERN 1.6 | An inventory of AI systems, including AI features in vendor products, is maintained. | no |
| G-04 | Govern | GOVERN 2.1 | Roles and accountability for AI risk are assigned, with a named executive owner. | no |
| G-05 | Govern | GOVERN 2.2 | Staff who use or oversee AI are trained on the policy and on AI risks. | partial |
| G-06 | Govern | GOVERN 6.1 | Purchases of AI products and AI features are reviewed for risk before use. | no |
| P-01 | Map | MAP 1.1 | The intended purpose, users, and context of each AI system are documented. | partial |
| P-02 | Map | MAP 5.1 | Impacts on individuals and the organization are assessed before an AI system is deployed. | no |
| P-03 | Map | MAP 3.5 | Human oversight is defined for AI systems that affect people or decisions. | partial |
| P-04 | Map | MAP 4.1 | Risks from third-party data, models, and software are identified. | no |
| S-01 | Measure | MEASURE 2.3 | Accuracy and performance are tested before deployment against defined criteria. | partial |
| S-02 | Measure | MEASURE 2.11 | Systems that affect people are evaluated for harmful bias. | no |
| S-03 | Measure | MEASURE 2.10 | Privacy risks, including use of personal data by AI vendors, are evaluated. | partial |
| S-04 | Measure | MEASURE 2.4 | AI systems are monitored in production for errors, drift, and misuse. | no |
| N-01 | Manage | MANAGE 1.3 | Identified AI risks have documented responses and owners. | no |
| N-02 | Manage | MANAGE 2.4 | There is a way to override, pause, or switch off an AI system if it behaves unexpectedly. | partial |
| N-03 | Manage | MANAGE 4.3 | AI incidents and errors are reported, tracked, and communicated to affected parties. | no |
| N-04 | Manage | MANAGE 3.1 | Third-party AI products are monitored for changes and new risks after purchase. | no |

_This report scores the answers and inventory supplied against the NIST AI Risk Management Framework (AI RMF 1.0) and the Generative AI Profile (NIST AI 600-1). It is a self-assessment aid, not a certification or legal opinion. The AI RMF is voluntary; laws that apply to specific AI uses, such as lending, hiring, and consumer protection rules, should be reviewed with counsel._
