# Selection audit — 2026-10-12

This records why CounterSignal was chosen, not proof of product-market fit. Original pages were read on 2026-10-12. Reddit pages only showed relative age at the time; their month is approximate.

## User need and limits

| Source | Date/channel | Direct observation | Supports / does not support |
| --- | --- | --- | --- |
| [HN validation-tool discussion](https://news.ycombinator.com/item?id=44881440) | 2025-08-12 / Hacker News | Multiple independent commenters gave the tool absurd ideas and questioned repeated positive scores or unsupported projections. | Need for auditability; not willingness to install CounterSignal. |
| [Reddit hands-on comparison](https://www.reddit.com/r/Startup_Ideas/comments/1vhkcut/i_tested_ai_idea_validators_so_you_dont_have_to/) | ~2026-08 / Reddit | User tested several validators and called out absent economics and willingness-to-pay data. The author also built a competing tool. | Repeated skepticism; not an unbiased accuracy study. |
| [Reddit workflow discussion](https://www.reddit.com/r/SaaS/comments/1v8xx4e/how_do_you_use_ai_to_validate_startup_ideas/) | ~2026-08 / Reddit | Different commenters describe reading original posts, clustering complaints and checking whether the same pain repeats across sources. | Concrete manual workaround; not proof it should become software. |
| [Reddit competitor hand-check](https://www.reddit.com/r/EntrepreneurRideAlong/comments/1vnjfam/i_webchecked_133_validated_startup_ideas_from_a/) | ~2026-08 / Reddit | Author says manual competitor checks changed their view of AI-scored ideas. The sample numbers are self-reported. | Competition as separate evidence dimension; not a general market prevalence statistic. |

Attention signal: the problem appears in the August 2025 HN thread and multiple 2026 Reddit discussions, while idea-validation products continue to be offered. This indicates category attention only, not CounterSignal demand or likely virality.

## Alternatives and a narrow difference

- [IdeaOne](https://ideaone.dev/) searches six sources from a plain-English idea and returns a cited BUILD / VALIDATE MORE / DON'T BUILD report. At the access date: account required for the first free report; $3 single report, $12 for five, $19/month unlimited. It already admits insufficient evidence, so a new tool cannot claim to invent citations or caution. Independent customer reviews were not located in the search window.
- [Preuve](https://preuve.ai/idea-validation/) offers a free scan and a $59 full founder report across 60+ claimed sources, with competitor mapping and a numeric verdict. Its own page presents positive testimonials; [Trustpilot](https://uk.trustpilot.com/review/preuve.ai) has public reviews. Those are not a controlled benchmark.
- [Reddit Demand Validator](https://github.com/SevenAILab/reddit-demand-validator) is an MIT-licensed, no-key Reddit research Skill with first-hand quotes, counter-signals and falsification prompts. CounterSignal does not duplicate that search process; it takes a small curated multi-channel packet and performs local model-assisted overlap review.
- [RigorGraph](https://github.com/f0909172434/rigorgraph) is a broader local evidence-graph/audit framework. CounterSignal is narrower and requires no graph setup.

Differentiator to test with users: a researcher's own source packet stays local, the tool suggests semantic overlap without turning it into an invented “unique demand” count, and the output emphasizes missing evidence instead of a verdict. This is a workflow hypothesis. A spreadsheet or a careful human may be more useful.

## Other ideas considered

| Idea | User / frequency and existing workaround | Smallest loop and distribution hypothesis | Why not today |
| --- | --- | --- | --- |
| Coding-agent test-integrity audit | Developers before merging; manual test diff and mutation tools | Flag weakened tests in CI; share as checks | [mutagate](https://github.com/keyboardsamurai/mutagate) and [rewardhackwatch](https://github.com/aerosta/rewardhackwatch) overlap. |
| Agent-loop watchdog | Long-running agent users; manual stop/restart | Detect repeated tool/result cycles; plugin | [heartbeat](https://github.com/matantsach/heartbeat) and [agentfdr](https://github.com/kamihork/agentfdr) overlap. |
| Meeting carry-forward | Teams at recurring meetings; hand-copy tasks | Bring unresolved tasks to next agenda; template | [Fellow](https://help.fellow.ai/en/articles/3945044-carry-incomplete-items-forward) already does it. |
| Meeting action-item provenance | Hosts after each meeting; manual replay | Quote-linked tasks; team handoff | [meeting-summarizer](https://github.com/CompileWithG/meeting-summarizer) and [Meeting Action Extractor](https://github.com/minhal-coding/ai-meeting-action-extractor) do it. |
| Teacher worksheet review | Teachers each lesson; manual check | Flag likely duplicate/off-topic items; share review | Needs human-labeled cases and review-time test before public trust claims. |
| Local-model setup diagnosis | Beginners at setup; forum search | Explain likely configuration failure; docs | Insufficient independent demand evidence; may be a documentation issue. |
| Idea competitor-density map | Makers per idea; manual web search | Classify direct/adjacent alternatives; report | IdeaOne/Preuve already search competitors; no distinct wedge yet. |
| AI-code diff coach | Coding-agent users per change; read diff/ask agent | Line-anchored teaching; GitHub share | [AhaDiff](https://github.com/AGI-is-going-to-arrive/ahadiff) already provides lessons and quiz. |

Reference roles: [Knowledge Work Plugins](https://github.com/anthropics/knowledge-work-plugins) (Apache-2.0) informed task-to-output scoping; [Agency Agents](https://github.com/msitarzewski/agency-agents) (MIT) informed product/research/reality checks; the newly discovered [Reddit Demand Validator](https://github.com/SevenAILab/reddit-demand-validator) (MIT) and RigorGraph informed the competitor boundary. No code or prompt text was copied from them.
