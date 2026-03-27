# Indicator-Theory Alignment Audit

> **Date**: 2026-03-26
> **Purpose**: Assess how well each of the 6 indicators in this study follows the ORIGINAL theoretical framework's intended meaning and measurement method.
> **Method**: Comparison of original source methodology against this study's operationalization, based on published literature and the study's own method.md documentation.

---

## 1. ACW (Adaptive Capacity Wheel)

**Original Source**: Gupta, J. et al. (2010). "The Adaptive Capacity Wheel." *Environmental Science & Policy*, 13(6), 459-471.

### What Gupta Intended

1. **Scoring**: -2 to +2 per criterion, based on **expert judgment** with structured research protocols. Gupta specified five steps: preparing, collecting data, analyzing, interpreting, and presenting. Data collection involved **questionnaires to senior experts/managers** and **document analysis** of the specific institution being assessed.
2. **Aggregation**: Gupta explicitly warned that "the criteria are **not additive** in the sense that values given to each criterion can be simply added." Aggregation loses detail and should "never" be used "without the separate Adaptive Capacity Wheels backing such an aggregation."
3. **Domain**: Designed for **climate change adaptation** institutional assessment. Application to general government adaptive capacity requires construct validity justification.
4. **Unit of analysis**: A single institution or governance arrangement, assessed through direct engagement with that institution's actors and documents.

### What This Study Does

1. **Scoring**: Uses a **proxy-mapping protocol** that derives ACW criterion scores from pre-existing datasets (WGI, EGDI, DGI, INST scores, Lowi ratios, TIDE codes, policy lag data, presidential speeches). No expert panel was consulted; no questionnaires were administered to government officials.
2. **Aggregation**: Computes a **single ACW total score** per government (e.g., Moon +16, Yoon -4) and uses these for **ranking** presidents. Although the study notes the total is "supplementary," the score appears in the final results table and sensitivity analysis.
3. **Domain**: Extended from climate adaptation to **general government adaptive capacity** across 6 presidential administrations.
4. **Unit of analysis**: Entire presidential administrations (5-year terms), compared cross-temporally.

### Gap Assessment

| Aspect | Original Intent | This Study's Use | Gap | Severity |
|--------|----------------|-----------------|-----|----------|
| Scoring method | Expert panels + questionnaires + document analysis of assessed institution | Proxy mapping from secondary indicators (WGI, EGDI, laws, speeches) | No direct institutional assessment; scores are derived from other indicators, creating circular dependency | **HIGH** |
| Aggregation | "Criteria are NOT additive"; aggregate only with individual wheels backing | Single total score per president used for ranking | Directly contradicts Gupta's explicit warning | **HIGH** |
| Comparison use | Single institution deep-dive | Cross-temporal comparison of 6 governments | Gupta did not design ACW for comparative ranking of political leaders | **MEDIUM** |
| Domain | Climate change adaptation institutions | General government adaptive capacity | Legitimate extension (precedent exists) but requires construct validity argument | **LOW** |
| Inter-coder reliability | Required structured protocol with multiple coders | Single researcher + AI validation (Layer 3) | AI validation is post-hoc, not independent parallel coding | **MEDIUM** |

### Circular Dependency Problem

The ACW scores in this study are **derived from the other 5 indicators** (WGI feeds into Le2/A1, INST feeds into Lc3/A3/V3, Lowi feeds into V3, TIDE feeds into V4/Le3, Policy Lag feeds into A2/Lc1). This means ACW is not an independent measure but a **weighted composite of the other indicators**. Gupta intended ACW to be scored directly from institutional evidence, not reconstructed from other metrics.

---

## 2. T/I/D/E Attribution

**Theoretical Inspiration**: Streeck & Thelen (2005) *Beyond Continuity*; Pierson (2004) *Politics in Time*; Mahoney & Thelen (2010) *Explaining Institutional Change*

### What the Original Theorists Intended

1. **Nature**: Streeck & Thelen's typology (displacement, layering, drift, conversion) was developed as a **qualitative, interpretive framework** for understanding gradual institutional change in advanced political economies. It was designed to be applied through **diachronic within-case studies**, analyzing processes and mechanisms in specific policy areas.
2. **Drift**: Defined as erosion of institutional arrangements through **failure to actively maintain and adjust** them to changing conditions. Often the product of "deliberate political strategy of non-decision." It is a **processual concept**, not a countable event.
3. **Layering**: A process of progressive growth of new elements among traditional arrangements, understood as cumulative transformation -- not a discrete, countable action.
4. **Quantification**: Neither Streeck & Thelen nor Mahoney & Thelen intended their typology to be used for **quantitative coding with arithmetic operations** (e.g., Net = I - I- - D). The framework is inherently **qualitative and process-oriented**.

### What This Study Does

1. **Codes individual actions** as T, I, I-, D, or E (adding "E" for external -- not in Streeck/Thelen)
2. **Counts items** per category and computes **Net = I - I- - D** as a cardinal score
3. Uses Net scores for **cross-presidential ranking** (Moon +15 > Roh +7 > Yoon +1)
4. Treats each coded item as having **equal weight** (one law = one crisis response = one index change)

### Gap Assessment

| Aspect | Original Intent | This Study's Use | Gap | Severity |
|--------|----------------|-----------------|-----|----------|
| Scoring method | Qualitative process tracing within specific policy domains | Quantitative counting of discrete coded items | Transforms an interpretive framework into a counting exercise | **HIGH** |
| Aggregation | No aggregation intended; each mode describes a process | Arithmetic Net = I - I- - D used for ranking | "Net" has no theoretical basis in Streeck/Thelen | **HIGH** |
| Equal weighting | Not applicable (no counting) | Every item weighted equally (a law = a crisis = an index change) | One landmark legislation counts the same as one WGI data point | **HIGH** |
| Drift concept | A process of institutional erosion over time | Coded as discrete events (e.g., "MERS 14-day delay") | Conflates an event (slow crisis response) with institutional drift | **MEDIUM** |
| T/I distinction | Layering is gradual addition of new elements alongside old | Coded as binary I (new) vs T (inherited) | Oversimplifies; a law can be both inherited framework AND new contribution | **MEDIUM** |
| Comparison use | Within-case process analysis | Cross-case quantitative comparison | Violates the interpretive epistemology of the original framework | **HIGH** |

### Fundamental Problem

The T/I/D/E framework commits a **category error**: it takes a qualitative typology of *processes* and converts it into a quantitative count of *events*. The "Net" score has no theoretical grounding -- there is no reason why one "I" should cancel one "I-" or one "D." Different institutional changes have vastly different magnitudes, and the theory provides no basis for treating them as interchangeable units.

---

## 3. INST (Institutional Adaptive Mechanisms)

**Original Source**: Argyris, C. & Schon, D.A. (1978). *Organizational Learning: A Theory of Action Perspective*.

### What Argyris & Schon Intended

1. **Level of analysis**: **Individual and organizational** learning within specific organizations. The theory describes how individuals detect and correct errors, and how this learning becomes embedded in organizational memory.
2. **Measurement**: Argyris intended observation of **actual behavioral patterns** -- the gap between "espoused theory" (what organizations say they do) and "theory-in-use" (what they actually do). This requires **ethnographic observation, interviews, and action research**, not document review.
3. **Single/double-loop distinction**: A distinction in the **process** of learning (are governing variables questioned?), not in the **existence** of formal institutions. A law can exist without any learning occurring; learning can occur without a law.
4. **Scale**: Individual --> organization. Argyris himself noted the **aggregation problem**: how individual learning transfers to organizational learning is poorly understood. Extending this to **government-level** comparison across administrations is a further leap.
5. **Recent critique**: A 2023 systematic review in *European Management Review* found that double-loop learning has had only "superficial impact" in practice, partly because of the difficulty of operationalization.

### What This Study Does

1. **Operationalizes as 4 dimensions** (D1: Policy Feedback, D2: Policy Experimentation, D3: Citizen Participation, D4: AI/Digital Governance) scored 0-2
2. **Scores based on law existence**: 0 = no law, 1 = law exists but limited, 2 = law with systematic operation
3. **Equates legal existence with learning**: If a law mandating feedback exists, score = 2 regardless of whether feedback actually occurs
4. **Cross-government comparison**: Compares 6 presidential administrations on a /8 scale

### Gap Assessment

| Aspect | Original Intent | This Study's Use | Gap | Severity |
|--------|----------------|-----------------|-----|----------|
| Scoring method | Ethnographic observation of actual behavioral patterns (espoused vs. theory-in-use) | Binary/ordinal based on law existence | Law existence ≠ learning occurrence. Park Geun-hye scores D1=2 despite governance collapse | **HIGH** |
| Unit of analysis | Organizations and their members | Entire presidential administrations | Massive scale leap with no aggregation theory | **HIGH** |
| Single vs. double-loop | Process distinction: are governing variables questioned? | Mapped to policy experimentation (D2) as proxy | Policy experimentation laws may exist without double-loop learning occurring | **MEDIUM** |
| Comparison | Not designed for cross-organization comparison | 6 governments ranked on /8 scale | Argyris did not intend comparative ranking | **MEDIUM** |
| Espoused vs. theory-in-use | Core distinction of the framework | Not assessed -- only formal institutions counted | Misses the entire point: the gap between formal rules and actual practice | **HIGH** |

### The "Law Existence = Learning" Fallacy

The most severe problem: Argyris's central insight is that organizations have **espoused theories** (formal rules, laws, stated procedures) that systematically differ from their **theories-in-use** (actual behavioral patterns). This study scores INST based on espoused theory alone (does the law exist?), completely ignoring theory-in-use. The study itself acknowledges this: "법 존재가 법 작동을 보장하지 않는다" (law existence does not guarantee law operation) -- yet scores as if it does.

---

## 4. Lowi Policy Typology

**Original Source**: Lowi, T.J. (1972). "Four Systems of Policy, Politics, and Choice." *Public Administration Review*, 32(4), 298-310.

### What Lowi Intended

1. **Classification basis**: Policies classified by the **type of coercion** involved along two axes:
   - Likelihood of coercion (immediate vs. remote)
   - Applicability of coercion (individual conduct vs. environment of conduct)
2. **Unit**: Lowi specified that "the reader should substitute 'statute' for 'policy'" -- classification should be based on the **actual legal content** and coercive mechanism of the policy, not its name or declared intent.
3. **Purpose**: To predict the **political dynamics** that different policy types generate ("policy determines politics"), not to measure government quality or adaptiveness.
4. **Known limitation**: "Most public decisions cannot be framed within a single type." Lowi himself acknowledged boundary ambiguity.

### What This Study Does

1. **Classifies 595 국정과제 (national tasks)** into Lowi's 4 types
2. **Classification basis**: Primarily by **task name/title**, not by analysis of the coercive mechanism embedded in the policy
3. **Adds "adaptive tool" overlay**: Uses Schneider & Ingram (1990) policy tools framework to identify "adaptive" tasks based on keyword presence (broad) or governance mechanism (strict)
4. **Purpose**: To calculate "adaptive tool ratio" per government as a measure of governance quality

### Gap Assessment

| Aspect | Original Intent | This Study's Use | Gap | Severity |
|--------|----------------|-----------------|-----|----------|
| Classification basis | Type of coercion (content of statute) | Task name/title (과제명) | Title may not reflect actual coercive mechanism; "AI 3대 강국" could be distributive, regulatory, or constituent depending on implementation | **HIGH** |
| Purpose | Predict political dynamics | Measure adaptive governance quality | Lowi did not design his typology as a quality metric | **MEDIUM** |
| "Adaptive" category | Does not exist in Lowi | Added via Schneider & Ingram overlay | Legitimate extension but creates a hybrid framework that is neither pure Lowi nor pure Schneider & Ingram | **MEDIUM** |
| Single classification | Lowi acknowledged boundary ambiguity | Forces single classification per task | Known limitation, handled reasonably (primary type) | **LOW** |
| Unit equivalence | Statutes with analyzed coercive content | 국정과제 of varying granularity (Roh: 12 tasks vs. Park: 140 tasks) | Vastly different granularity across governments makes ratio comparison problematic | **HIGH** |

### The Title-Based Classification Problem

The study classifies policies by their declared name, not by analyzing the actual coercive mechanism. For example, "반도체AI배터리 등 미래전략산업 초격차 확보" is classified as distributive based on the title suggesting investment/subsidy, but without examining the actual policy instruments (which might include regulation, tax incentives, or structural reform), the classification is unreliable. Lowi explicitly warned that classification must be based on the statute's content, not its declared purpose.

The strict review (lowi_strict_review.md) partially addresses this for the "adaptive" subcategory by examining actual governance mechanisms, which is a significant improvement. But the base Lowi classification of all 595 tasks remains title-driven.

---

## 5. WGI (World Governance Indicators)

**Original Source**: Kaufmann, D., Kraay, A., & Mastruzzi, M. (2010). "The Worldwide Governance Indicators: Methodology and Analytical Issues." World Bank Policy Research Working Paper No. 5430.

### What Kaufmann & Kraay Intended

1. **Purpose**: A **high-level, cross-country snapshot** of governance perceptions. Useful for "broad cross-country comparisons and for evaluating broad trends over time."
2. **Nature**: **Perception-based** composite from 35 data sources (household surveys, firm surveys, expert assessments). Measures perceptions, not objective governance quality.
3. **Margins of error**: All scores come with **standard errors**. Small changes that fall within the confidence interval should not be interpreted as meaningful. Kaufmann & Kraay explicitly warn against "over-interpreting small differences between countries and over time."
4. **Attribution**: WGI is a **country-level aggregate**. The creators never intended it for attributing governance quality to **specific political leaders**. No mechanism in WGI isolates the effect of one president from structural trends, institutional inheritance, or global factors.
5. **Time comparison**: Permitted but with caution. Over-time comparability in the original WGI depended on changes in the global average being small.

### What This Study Does

1. **Detrends** WGI GE.EST using a linear trend (+0.026/year) and attributes the **residual to individual presidents** (e.g., Roh +0.308, Moon +0.233, Park -0.060)
2. Uses these residuals as evidence of presidential **contribution** to governance effectiveness
3. Feeds WGI-derived scores into multiple ACW criteria (Le2, A1, Lc1, etc.)

### Gap Assessment

| Aspect | Original Intent | This Study's Use | Gap | Severity |
|--------|----------------|-----------------|-----|----------|
| Attribution | Country-level aggregate; not for leader attribution | Residuals attributed to specific presidents | Directly contradicts intended use | **HIGH** |
| Margins of error | Must consider confidence intervals; avoid over-interpreting small differences | Differences as small as 0.030 (Yoon) treated as meaningful "net contribution" | Most inter-presidential differences likely fall within WGI's margin of error | **HIGH** |
| Perception vs. reality | Measures perceptions of governance, not objective governance quality | Treated as evidence of actual governance effectiveness | Perception lag and halo effects are uncontrolled | **MEDIUM** |
| Detrending | No provision in original methodology for detrending to isolate leader effects | Linear detrending with R²=0.73 | Methodologically creative but without theoretical basis in WGI literature | **MEDIUM** |
| Time series | Permitted with caution and confidence intervals | Used as primary evidence of governance trajectory | Appropriately labeled "exploratory" but still used in ACW scoring | **LOW** |

### The Attribution Problem

The study's own final_results.md acknowledges: "WGI = 인식 지표, 시차 효과 존재. 인과 귀속의 주증거로 부적절" (WGI = perception indicator, lag effects exist, inappropriate as main evidence for causal attribution). This is correct. However, the WGI data still feeds into ACW scoring across multiple criteria, meaning it influences the final comparative assessment despite this disclaimer.

---

## 6. Policy Lag

**Original Source**: Friedman, M. (1960). *A Program for Monetary Stability*; Friedman (1961). "The Lag in Effect of Monetary Policy." *Journal of Political Economy*, 69, 447-466.

### What Friedman Intended

1. **Domain**: Exclusively **monetary policy**. Friedman argued that monetary policy effects operate with "long and variable" lags (4-29 months), making fine-tuning unreliable.
2. **Purpose**: To argue **against** discretionary policy intervention. Friedman's point was that lags make it impossible to fine-tune the economy, so rules-based policy is preferable to discretionary intervention.
3. **Type of lag**: **Outside lag** (policy action --> effect on economy). Friedman was NOT measuring government response speed; he was measuring how long it takes for a policy, once enacted, to affect the economy.
4. **Comparative use**: Not designed for comparing governments' crisis response performance. Friedman's interest was in the structure of monetary transmission mechanisms, not in evaluating leadership quality.

### What This Study Does

1. Measures **inside lag** (crisis event --> government response), which is the opposite of Friedman's outside lag
2. Converts to a measure of **government response speed** (days to first response, days to structural response)
3. Uses it for **cross-presidential comparison** of crisis management ability
4. Links it to OECD "Government Agility" framework (a separate, much more recent concept)

### Gap Assessment

| Aspect | Original Intent | This Study's Use | Gap | Severity |
|--------|----------------|-----------------|-----|----------|
| Type of lag | Outside lag (policy --> effect) | Inside lag (crisis --> response) | Measures fundamentally different concept | **HIGH** |
| Domain | Monetary policy transmission | Crisis response across all domains (pandemic, financial, safety) | Complete domain shift | **HIGH** |
| Purpose | Argue against fine-tuning; show intervention is unreliable | Evaluate and rank government response quality | Friedman would argue the metric itself is misleading (speed ≠ quality) | **MEDIUM** |
| Comparison | Not comparative across governments | Cross-presidential ranking by response days | No theoretical basis in Friedman for this comparison | **MEDIUM** |
| Crisis heterogeneity | N/A (single policy domain) | 7 crises of vastly different types and scales | Cannot compare pandemic response days to financial crisis response days | **MEDIUM** |

### The Inside/Outside Lag Confusion

The study cites Friedman as the theoretical foundation but measures the opposite concept. Friedman's "policy lag" is the delay from policy enactment to economic effect. This study measures the delay from crisis occurrence to policy enactment. The OECD "Government Agility" framework (2021) is a much more appropriate theoretical basis for what this study actually measures, and the study does reference it -- but Friedman remains listed as the primary theoretical origin in method.md.

---

## Overall Assessment

### Alignment Summary

| Indicator | Alignment | Key Issue |
|-----------|-----------|-----------|
| **ACW** | SEVERE misalignment | Proxy mapping instead of expert assessment; additive scoring despite explicit warning; circular dependency with other indicators |
| **T/I/D/E** | SEVERE misalignment | Qualitative process typology converted to quantitative counting with arithmetic; "Net" has no theoretical basis |
| **INST** | SEVERE misalignment | Law existence used as proxy for organizational learning; ignores espoused vs. theory-in-use distinction that is the core of Argyris's framework |
| **Lowi** | MODERATE misalignment | Title-based classification instead of coercion analysis; granularity non-equivalence; but STRICT review partially corrects |
| **WGI** | MODERATE misalignment | Attribution to presidents contradicts intended use; margins of error not respected; but appropriately labeled "exploratory" |
| **Policy Lag** | MODERATE misalignment | Measures inside lag while citing outside lag theory; but OECD framework provides adequate alternative grounding |

### Severity Classification

**SEVERE (3 indicators: ACW, T/I/D/E, INST)**:
These three indicators have fundamental operationalization problems that go against explicit warnings or core principles of the original frameworks. The results they produce cannot be straightforwardly interpreted through the lens of the theories they claim to apply.

**MODERATE (3 indicators: Lowi, WGI, Policy Lag)**:
These indicators have meaningful gaps between original theory and application, but the study partially acknowledges or mitigates these gaps. With appropriate caveats and methodological adjustments, the results retain some interpretive value.

---

## Recommendations

### For ACW (SEVERE)

1. **Stop computing total scores**. Gupta explicitly says criteria are not additive. Report only the dimensional wheel profiles.
2. **Acknowledge circular dependency**. ACW is not an independent indicator -- it is a weighted composite of the other 5 indicators. Either score ACW independently (through expert assessment) or redefine it transparently as a "summary composite."
3. **If maintaining proxy approach**: Rename it (e.g., "Adaptive Capacity Profile" or "Composite Adaptive Index") to avoid claiming Gupta-ACW methodology when the actual method is proxy mapping.

### For T/I/D/E (SEVERE)

1. **Abandon the "Net" score**. There is no theoretical basis for I - I- - D arithmetic. Different institutional changes have vastly different magnitudes.
2. **Use qualitatively**. Present T/I/D/E as a narrative typology describing the nature of institutional change under each president, not as a quantitative ranking tool.
3. **If quantification desired**: Develop an explicit weighting scheme with theoretical justification (e.g., weight by institutional impact magnitude) and acknowledge this as a novel methodological contribution, not an application of Streeck/Thelen.

### For INST (SEVERE)

1. **Rename the framework**. This is not Argyris & Schon's organizational learning -- it is a "Legal Infrastructure Index" measuring the formal existence of adaptive governance laws. Call it what it is.
2. **Add a practice dimension**. For at least some laws, assess whether they are actually implemented (e.g., did the Government Performance Evaluation system actually produce policy changes?). Even a rough assessment would address the espoused/actual gap.
3. **Acknowledge the D1 ceiling effect**. All 6 governments score D1=2 because the same law exists throughout. This is a measurement artifact of law-existence scoring, not evidence that all governments learned equally.

### For Lowi (MODERATE)

1. **For the STRICT adaptive classification**: Already well-handled. The distinction between keyword-based (broad) and mechanism-based (strict) is methodologically sound.
2. **For the base 4-type classification**: Acknowledge that title-based coding is a pragmatic compromise, not Lowi's intended method. Ideally, a sample of tasks should be coded by actual policy content to validate the title-based approach.
3. **Address granularity**: Roh's 12 tasks vs. Park's 140 tasks makes ratio comparison unreliable. Consider normalizing by policy domain rather than raw count.

### For WGI (MODERATE)

1. **Report confidence intervals**. Kaufmann & Kraay provide standard errors for every estimate. Show which inter-presidential differences exceed the margin of error.
2. **Stop attributing residuals to presidents**. Or at minimum, label this as "residual after trend removal" rather than "net contribution" (순기여→추세제거 잔차로 변경 완료), which implies causal attribution.
3. **Maintain "exploratory supplementary" framing** and ensure WGI-derived scores do not dominate ACW criteria scoring.

### For Policy Lag (MODERATE)

1. **Reground in OECD Government Agility framework** rather than Friedman. The study already references OECD (2021) -- make this the primary theoretical basis.
2. **Acknowledge heterogeneity explicitly**. A table comparing crisis type, scale, and institutional context should accompany any lag comparison.
3. **Already being redesigned** (per separate agent). Ensure the redesign addresses these theory-alignment issues.

---

## Cross-Cutting Issue: Cascading Dependency

The most systemic problem is not any single indicator's misalignment but the **cascading dependency** among them:

```
WGI --> feeds into ACW (Le2, A1, Lc1, Lc2)
INST --> feeds into ACW (Lc3, A3, V3, V4)
Lowi --> feeds into ACW (V3)
TIDE --> feeds into ACW (V4, Le3)
Policy Lag --> feeds into ACW (A2, Lc1, A4)
```

This means:
- ACW is not an independent 6th indicator -- it is a **derivative** of the other 5
- Errors in any source indicator propagate into ACW
- The "triangulation" claim (5 independent methods converging) is overstated because the methods are not independent

**Recommendation**: Either (a) score ACW independently through expert assessment, making it truly independent, or (b) acknowledge ACW as a summary composite and drop the claim of methodological triangulation for ACW specifically.

---

## Sources

### ACW
- [Gupta et al. 2010 - Original Paper (PDF)](https://repub.eur.nl/pub/20798/ESP13_2010_459.pdf)
- [Gupta et al. 2010 - Semantic Scholar](https://www.semanticscholar.org/paper/The-Adaptive-Capacity-Wheel:-a-method-to-assess-the-Gupta-Termeer/65404a7632d4968efba32838c415622e719a06a1)

### T/I/D/E
- [Streeck & Thelen 2005 - Beyond Continuity](https://www.mpifg.de/821262/2005-01-wz-streeck-thelen)
- [Mahoney & Thelen 2010 - A Theory of Gradual Institutional Change](https://www.researchgate.net/publication/50368550_A_Theory_of_Gradual_Institutional_Change)

### INST
- [Argyris 1977 - Double Loop Learning in Organizations (HBR)](https://hbr.org/1977/09/double-loop-learning-in-organizations)
- [Double-loop learning - Wikipedia](https://en.wikipedia.org/wiki/Double-loop-learning)
- [2023 Systematic Review - Revitalizing Double-Loop Learning](https://onlinelibrary.wiley.com/doi/10.1111/emre.12615)

### Lowi
- [Lowi 1972 - Four Systems of Policy, Politics, and Choice (PDF)](https://perguntasaopo.wordpress.com/wp-content/uploads/2012/02/lowi_1972_four-systems-of-policy-politics-and-choice.pdf)
- [From Policy Typologies to Policy Feedback](https://www.ippapublicpolicy.org/file/paper/1433922143.pdf)

### WGI
- [Kaufmann, Kraay & Mastruzzi 2010 - WGI Methodology (PDF)](https://documents1.worldbank.org/curated/en/630421468336563314/pdf/WPS5430.pdf)
- [WGI 2025 Methodology Revision](https://www.worldbank.org/content/dam/sites/govindicators/doc/The%20Worldwide%20Governance%20Indicators%202025%20Methodology%20Revision.pdf)
- [WGI: Answering the Critics](https://openknowledge.worldbank.org/server/api/core/bitstreams/acb720f6-846e-5fa3-8ca7-67c65b3ece1a/content)

### Policy Lag
- [Friedman 1961 - The Lag in Effect of Monetary Policy](https://ideas.repec.org/a/ucp/jpolec/v69y1961p447.html)
- [Milton Friedman's "long and variable lag" - Marketplace](https://www.marketplace.org/story/2023/07/24/milton-friedmans-long-and-variable-lag-explained)
- [Long and Variable Lags - St. Louis Fed](https://www.stlouisfed.org/publications/regional-economist/2023/may/examining-long-variable-lags-monetary-policy)
