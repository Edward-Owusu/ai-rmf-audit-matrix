# Input reference

An assessment folder holds two files. Copy `samples/template/` to start.

## assessment.json

```json
{
  "organization": "Your organization",
  "assessment_date": "2026-09-30",
  "answers": { "G-01": "yes", "G-02": "partial", "P-02": "no" }
}
```

| Field | Notes |
|---|---|
| `organization` | Name shown on the report |
| `assessment_date` | Date of the assessment (YYYY-MM-DD); impact assessments older than 365 days before this date are flagged |
| `answers` | `yes`, `partial`, or `no` for each practice ID below; missing answers count as `no` |

### Practices

| ID | Function | AI RMF | Practice |
|---|---|---|---|
| G-01 | Govern | GOVERN 1.1 | Legal and regulatory requirements that apply to the organization's use of AI have been identified. |
| G-02 | Govern | GOVERN 1.2 | An approved AI use policy sets out acceptable uses, prohibited uses, and approval requirements. |
| G-03 | Govern | GOVERN 1.6 | An inventory of AI systems, including AI features in vendor products, is maintained. |
| G-04 | Govern | GOVERN 2.1 | Roles and accountability for AI risk are assigned, with a named executive owner. |
| G-05 | Govern | GOVERN 2.2 | Staff who use or oversee AI are trained on the policy and on AI risks. |
| G-06 | Govern | GOVERN 6.1 | Purchases of AI products and AI features are reviewed for risk before use. |
| P-01 | Map | MAP 1.1 | The intended purpose, users, and context of each AI system are documented. |
| P-02 | Map | MAP 5.1 | Impacts on individuals and the organization are assessed before an AI system is deployed. |
| P-03 | Map | MAP 3.5 | Human oversight is defined for AI systems that affect people or decisions. |
| P-04 | Map | MAP 4.1 | Risks from third-party data, models, and software are identified. |
| S-01 | Measure | MEASURE 2.3 | Accuracy and performance are tested before deployment against defined criteria. |
| S-02 | Measure | MEASURE 2.11 | Systems that affect people are evaluated for harmful bias. |
| S-03 | Measure | MEASURE 2.10 | Privacy risks, including use of personal data by AI vendors, are evaluated. |
| S-04 | Measure | MEASURE 2.4 | AI systems are monitored in production for errors, drift, and misuse. |
| N-01 | Manage | MANAGE 1.3 | Identified AI risks have documented responses and owners. |
| N-02 | Manage | MANAGE 2.4 | There is a way to override, pause, or switch off an AI system if it behaves unexpectedly. |
| N-03 | Manage | MANAGE 4.3 | AI incidents and errors are reported, tracked, and communicated to affected parties. |
| N-04 | Manage | MANAGE 3.1 | Third-party AI products are monitored for changes and new risks after purchase. |

## ai_systems.csv

One row per AI system. List vendor products with AI features switched on (chatbots, transcription, writing assistants, screening tools), not only systems built in-house.

| Column | Required | Values | Meaning |
|---|---|---|---|
| `system` | Yes | text | Unique name |
| `owner` | | text | Accountable business owner; blank is a gap |
| `vendor` | Yes | `internal` or vendor name | Who supplies the AI |
| `use_case` | | text | What the system does |
| `decision_impact` | Yes | `none`, `advisory`, `consequential` | Whether it informs (`advisory`) or makes or drives (`consequential`) decisions about people |
| `data_sensitivity` | Yes | `none`, `internal`, `personal`, `sensitive` | Most sensitive data it processes; `sensitive` covers financial, health, biometric, and similar data |
| `generative` | | true/false | Generates text, images, code, or audio |
| `customer_facing` | | true/false | Customers or the public interact with it or receive its output |
| `human_review` | | true/false | A person reviews outputs before they take effect or reach customers |
| `impact_assessment_date` | | YYYY-MM-DD | Date of the latest impact assessment |
| `bias_tested` | | true/false | Evaluated for harmful bias across affected groups |
| `monitoring` | | true/false | Monitored in production for errors, drift, or misuse |
| `vendor_reviewed` | | true/false | Vendor's AI practices, data handling, and terms reviewed |
| `incident_process` | | true/false | Errors and harms involving the system can be reported and handled |
| `documented` | | true/false | Purpose, limits, and out-of-scope uses are documented |
| `user_disclosure` | | true/false | People are told they are interacting with AI |
| `data_use_restricted` | | true/false | Contract or settings stop the vendor from training on your data |

`true` also accepts yes, y, or 1; blank counts as false.
