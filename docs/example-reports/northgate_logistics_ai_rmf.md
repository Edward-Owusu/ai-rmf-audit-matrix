# AI RMF audit: Northgate Logistics (fictional)

Assessed 2026-09-30 | Generated 2026-10-07 18:17 UTC | ai_rmf 0.1.0

- Overall maturity: **94 / 100 (Managed)**
- AI systems: **4** (0 high, 2 medium, 2 low risk; 3 from vendors; 1 generative)
- Gaps: **1** (0 critical, 0 high, 0 medium, 1 low)

## Maturity by function

| Function | Practices | Systems | Score | Level |
|---|---|---|---|---|
| Govern | 95 | 100 | **98** | Managed |
| Map | 100 | 86 | **93** | Managed |
| Measure | 86 | 100 | **93** | Managed |
| Manage | 86 | 100 | **93** | Managed |

## AI system inventory

| System | Vendor | Risk tier | Checks passed | Gaps |
|---|---|---|---|---|
| Driver safety scoring | SafeFleet | Medium | 8 of 8 | 0 |
| Shipment status assistant | AssistIQ | Medium | 9 of 9 | 0 |
| Invoice data extraction | DocuRead | Low | 2 of 3 | 1 |
| Route optimization | internal | Low | 2 of 2 | 0 |

## Gaps

- **LOW** Invoice data extraction (Low): Purpose and limits not documented. Intended purpose, known limits, and out-of-scope uses are not documented. Fix: Document the intended purpose, users, inputs, known limitations, and uses that are not allowed. _(MAP 1.1, MAP 2.2)_

## Program practices

| ID | Function | AI RMF | Practice | Answer |
|---|---|---|---|---|
| G-01 | Govern | GOVERN 1.1 | Legal and regulatory requirements that apply to the organization's use of AI have been identified. | yes |
| G-02 | Govern | GOVERN 1.2 | An approved AI use policy sets out acceptable uses, prohibited uses, and approval requirements. | yes |
| G-03 | Govern | GOVERN 1.6 | An inventory of AI systems, including AI features in vendor products, is maintained. | yes |
| G-04 | Govern | GOVERN 2.1 | Roles and accountability for AI risk are assigned, with a named executive owner. | yes |
| G-05 | Govern | GOVERN 2.2 | Staff who use or oversee AI are trained on the policy and on AI risks. | partial |
| G-06 | Govern | GOVERN 6.1 | Purchases of AI products and AI features are reviewed for risk before use. | yes |
| P-01 | Map | MAP 1.1 | The intended purpose, users, and context of each AI system are documented. | yes |
| P-02 | Map | MAP 5.1 | Impacts on individuals and the organization are assessed before an AI system is deployed. | yes |
| P-03 | Map | MAP 3.5 | Human oversight is defined for AI systems that affect people or decisions. | yes |
| P-04 | Map | MAP 4.1 | Risks from third-party data, models, and software are identified. | yes |
| S-01 | Measure | MEASURE 2.3 | Accuracy and performance are tested before deployment against defined criteria. | yes |
| S-02 | Measure | MEASURE 2.11 | Systems that affect people are evaluated for harmful bias. | partial |
| S-03 | Measure | MEASURE 2.10 | Privacy risks, including use of personal data by AI vendors, are evaluated. | yes |
| S-04 | Measure | MEASURE 2.4 | AI systems are monitored in production for errors, drift, and misuse. | yes |
| N-01 | Manage | MANAGE 1.3 | Identified AI risks have documented responses and owners. | yes |
| N-02 | Manage | MANAGE 2.4 | There is a way to override, pause, or switch off an AI system if it behaves unexpectedly. | yes |
| N-03 | Manage | MANAGE 4.3 | AI incidents and errors are reported, tracked, and communicated to affected parties. | yes |
| N-04 | Manage | MANAGE 3.1 | Third-party AI products are monitored for changes and new risks after purchase. | partial |

_This report scores the answers and inventory supplied against the NIST AI Risk Management Framework (AI RMF 1.0) and the Generative AI Profile (NIST AI 600-1). It is a self-assessment aid, not a certification or legal opinion. The AI RMF is voluntary; laws that apply to specific AI uses, such as lending, hiring, and consumer protection rules, should be reviewed with counsel._
