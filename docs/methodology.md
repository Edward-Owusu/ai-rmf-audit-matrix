# Methodology

The AI RMF Audit Matrix looks at AI risk management from two directions:

1. **The program.** Eighteen plain-language practices, grouped under the four functions of the NIST AI Risk Management Framework (Govern, Map, Measure, Manage), ask whether the organization has the policies, roles, and processes the framework expects.
2. **The systems.** An inventory of every AI system in use, whether built in-house or switched on inside a vendor product, is risk-tiered and tested against eleven system-level checks.

A policy that exists on paper but is not applied to the systems actually in use scores lower than one that is, which is the point of combining the two.

## Risk tiers

Each system is placed in one tier, using the inventory fields `decision_impact`, `data_sensitivity`, and `customer_facing`:

| Tier | Rule |
|---|---|
| **High** | Makes or drives **consequential** decisions about people (credit, employment, housing, insurance, access to services), **or** handles **sensitive** data and faces customers |
| **Medium** | Handles personal or sensitive data, faces customers, or **advises** a human decision maker |
| **Low** | Everything else, such as internal productivity tools that use no personal data |

The tiers follow the AI RMF emphasis on context and impact (MAP 1 and MAP 5) and are deliberately simple so that a small organization can apply them without a specialist.

## System checks

| Check | Applies to | Gap when | Severity | AI RMF | GAI risk (NIST AI 600-1) |
|---|---|---|---|---|---|
| SYS-01 No accountable owner | All systems | `owner` is blank | High | GOVERN 2.1 | |
| SYS-02 No impact assessment | Medium and High | No assessment date, or older than 365 days | High | MAP 5.1, MAP 1.1 | |
| SYS-03 Decisions about people made without human review | Advisory or consequential decisions | `human_review` is false | Critical (consequential), High (advisory) | MAP 3.5, MANAGE 2.4 | Human-AI Configuration |
| SYS-04 Not evaluated for harmful bias | Decisions using personal or sensitive data | `bias_tested` is false | High | MEASURE 2.11 | Harmful Bias and Homogenization |
| SYS-05 Not monitored in production | Medium and High | `monitoring` is false | Medium | MEASURE 2.4, MANAGE 4.1 | |
| SYS-06 Vendor AI not reviewed | Vendor-supplied | `vendor_reviewed` is false | High | GOVERN 6.1, MANAGE 3.1 | Value Chain and Component Integration |
| SYS-07 Vendor may use your data to train its models | Vendor generative AI with personal or sensitive data | `data_use_restricted` is false | High | MEASURE 2.10, MAP 4.1 | Data Privacy, Information Security |
| SYS-08 People are not told they are interacting with AI | Customer-facing | `user_disclosure` is false | Medium | MEASURE 2.8 | Human-AI Configuration |
| SYS-09 Generative output reaches customers without review | Generative and customer-facing | `human_review` is false | High | MEASURE 2.5, MANAGE 2.4 | Confabulation, Information Integrity |
| SYS-10 No AI incident process | Medium and High | `incident_process` is false | Medium | MANAGE 4.3 | |
| SYS-11 Purpose and limits not documented | All systems | `documented` is false | Low | MAP 1.1, MAP 2.2 | |

Each check is assigned to the AI RMF function it most directly evidences. The rule set lives in `src/ai_rmf/data/checks.json` and the logic in `src/ai_rmf/engine.py`.

## Function scores

For each function:

- **Practice score** = weighted share of that function's practices answered *yes* (1 point) or *partial* (0.5 points); unanswered counts as *no*. Practices that underpin the rest of the program carry weight 2; supporting practices carry weight 1.
- **System score** = share of applicable system checks for that function that the inventory meets.
- **Function score** = 0.5 × practice score + 0.5 × system score. If no checks for the function apply to any system, the function score is the practice score alone.

The **overall score** is the average of the four function scores.

| Score | Maturity level | Meaning |
|---|---|---|
| 0–24 | Initial | AI is used without a recognizable risk management approach |
| 25–49 | Developing | Some practices exist but are inconsistent or not applied to all systems |
| 50–74 | Defined | Practices are documented and mostly applied |
| 75–100 | Managed | Practices are applied consistently and evidenced across the inventory |

## The audit matrix

The matrix places every AI system (rows, sorted by risk tier and number of gaps) against every check (columns, grouped by function). Each cell is met, a gap coloured by severity, or not applicable. It shows at a glance whether gaps cluster in one system (a system problem) or run down one column (a program problem).

## Limitations

- The tool scores what it is told. Answers and inventory fields should be supported by evidence, such as a policy document, a vendor contract clause, or a bias test report.
- The AI RMF is voluntary and does not prescribe controls; the checks are one reasonable reading of its outcomes for smaller organizations, not an official NIST mapping.
- Specific AI uses are also governed by sector laws and regulations (for example, fair lending, equal employment, consumer protection, and state AI laws). The tool does not assess legal compliance.
- The maturity levels are a simplified scale for this tool and are not the AI RMF implementation tiers.
