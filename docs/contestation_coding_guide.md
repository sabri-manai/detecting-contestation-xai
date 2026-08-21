# Contestation Coding Guide (XAI-FUNGI Feasibility Audit)

**Scope.** Code the audited candidate episodes in
`outputs/02_translation_and_feasibility_audit/tables/feasibility_review_sample.csv`.

Two coders use this guide:

- the **primary annotator**, working from the English translation
  (NLLB-produced) with ±4 speaker-tagged turns of context, who codes the full
  audited sample;
- a **second, Polish-speaking coder**, working from the original Polish with a
  shorter, untagged context window, who independently double-codes a
  36-episode subset for reliability.

Both coders' labels are reconciled by adjudication into the final labels; see
the paper's Method section for the full reliability procedure and numbers.

---

## 1. What you are coding

Each row is one candidate utterance (`text_pl`) shown with ±4 utterances of
surrounding context (`context_pl`), each context line tagged `INT:` (interviewer)
or `P:` (participant); the `speaker` column says who said the target line. The
English (`text_en` / `context_en`) is a translation of the Polish; if the two
ever conflict, the Polish wins.

**Unit of analysis — code the target line as the head of a short episode.**
Use the context to *understand* the target, then decide:

- Code **`yes`** when the target line is *part of* the contestation move — it
  starts it, is its core, or runs straight into the next line or two of the
  *same participant's* continuing thought (the unit is "an utterance **or short
  contiguous sequence**").
- Code **`no`** when the target itself is neutral and the only pushback in the
  window is a *separate, unrelated* move, or is the **interviewer's** line
  (grey `speaker` rows are usually the task question → `no`).

The test: *would you point to the target line (± its immediate continuation) as
where the pushback is?* Do **not** code `yes` merely because some unrelated later
line in the ±4 window contains a challenge — context windows overlap, so that
would inflate everything. If you spot a genuine contestation the filter missed
sitting in the context, note it in `notes` but leave the target `no`.

Fill these columns; leave the four structure fields blank when
`is_contestation = no`:

| column | values |
|---|---|
| `is_contestation` | `yes` / `no` |
| `presence` | `explicit` / `implicit` / `ambiguous` |
| `target` | `prediction` / `reasoning` / `evidence` / `input data` / `explanation representation` / `system competence` |
| `interaction_act` | `request for justification` / `direct challenge` / `correction` / `alternative proposal` / `counterexample` / `rejection` / `request to acknowledge uncertainty` |
| `grounds` | `domain knowledge` / `technical knowledge` / `prior experience` / `internal inconsistency` / `missing evidence` / `data-quality concern` / `causal implausibility` / `presentation ambiguity` |
| `expected_response` | `justify` / `revise` / `incorporate correction` / `provide additional information` / `acknowledge uncertainty` / `expose conflicting evidence` / `defer to human expertise` |
| `notes` | free text; required whenever you code `ambiguous` or hesitate |

Pick the **single best** category per dimension. Use `ambiguous` sparingly and
say why in `notes`. These five dimensions are exactly the paper's contestation
taxonomy table.

---

## 2. Definition

> **Contestation** = an explicit or implicit challenge to an AI system's
> conclusion, reasoning, evidence, explanation, or epistemic authority that
> calls for justification, correction, reconsideration, or acknowledgment of
> uncertainty.

**The core test.** Is the participant **disputing what the system asserts or
does** — versus merely **not understanding it**, expressing a feeling, or
commenting on how it looks? Only the first is contestation.

---

## 3. Boundary rules (these decide most disagreements)

1. **Criticism of the representation** → *not* contestation **unless** the
   participant claims the representation *obstructs or prevents* correctly
   interpreting the output; a stated preference with no interpretive
   consequence is not enough.
   *"The font is too small / the colours clash"* → **no**.
   *"This bar can't be right — cap shape should dominate here"* → **yes**.
2. **Expressed personal uncertainty** → *not* contestation **unless** it demands
   that the system acknowledge uncertainty too.
   *"I'm not sure I follow this"* → **no**.
   *"The model shouldn't be this confident on this example"* → **yes**
   (`request to acknowledge uncertainty`).
3. **Hypothetical reasoning** → *not* contestation **unless** it functions as a
   counterexample against the system.
   *"What if the cap were larger…"* (exploratory) → **no**.
   *"But a young specimen also has this feature, so that rule fails"* → **yes**
   (`counterexample`).
4. **Task-question artifacts** → the utterance is the *interviewer's task
   question* being posed or read back (check `speaker` / the context), not the
   participant's own challenge → **no**.

**Also code `no` for:**
- **Incomprehension** — *"I don't understand this axis / these two look the
  same"* (a comprehension problem, not a dispute).
- **General affect** without a challenge — frustration, boredom, interest.

---

## 4. Worked examples (real episodes from the sample)

**POSITIVE — `PK_DE_07:125` (DE, Counterfactual).**
PL: *"…to moim zdaniem jest zupełnie bez sensu, co to AI przewiduje."*
EN: *"…in my opinion it makes absolutely no sense what the AI predicts."*
→ `is_contestation=yes`, `presence=explicit`, `target=prediction`,
`interaction_act=rejection`, `grounds=causal implausibility`,
`expected_response=justify`. *A direct, grounded rejection of the output.*

**NEGATIVE (incomprehension) — `PK_DE_03:64` (DE, Counterfactual).**
PL: *"…nie, nie rozumiem, bo tu są dwie obserwacje, one są dokładnie takie same,
chyba, prawie."*
EN: *"…I don't understand, because here are two observations, they're exactly the
same, I think, almost."*
→ Boundary case: not grasping the artifact is not the same as disputing it,
but context matters — with a wider window this episode continues into a clear
direct challenge from the same participant (see the paper's reliability
discussion for the full worked example).

**NEGATIVE (task-question artifact) — `PK_DE_08:83` (DE, Anchor).**
PL: *"Czy jesteś w stanie zidentyfikować, jak zmienia się pewność modelu…"*
→ `is_contestation=no`. *This is the task question, not a participant challenge.
Matched by the filter on question vocabulary.*

---

## 5. Procedure

1. **Candidate identification.** A bilingual lexicon of challenge markers flags
   candidate episodes from the full transcript set, favoring recall over
   precision.
2. **Feasibility audit.** A stratified sample (by participant group ×
   explanation format) is drawn from the flagged candidates and coded in full
   by the primary annotator, from the English translation.
3. **Reliability subset.** A second, Polish-speaking coder independently
   double-codes a 36-episode subset of that sample, from the original Polish,
   checking the machine translation's fidelity against it before coding.
4. **Adjudication.** Presence disagreements between the two coders are
   adjudicated by returning to the full context window and this codebook;
   adjudicated labels are the ones reported throughout the paper.
5. **Gate read.** From the adjudicated labels: count genuine contestation
   episodes, check diversity across the group × format grid, and report the
   confirmation proportion.
