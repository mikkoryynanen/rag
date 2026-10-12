# Developer-in-control agentic coding: session learnings

Written 2026-10-12. Self-contained handoff for a new session: what the source video says, what its
commenters suggest, the workflow proposed from both, and how the material was fetched.

## Source

- Video: The PrimeTime (ThePrimeagen), "It's not just you", https://www.youtube.com/watch?v=FlWII9xFabo
- Published 12 Oct 2026, about 18.5 minutes, about 15,800 views and 119 comments when read.
- Format: he reacts to replies to a post asking what people struggle with most in AI-assisted
  software engineering.
- Read for this document: the full transcript and all 87 top-level comments. Reply threads were
  not expanded.

## The questions this session set out to answer

1. How do we build an agentic code generation system where the developer stays in control and
   understands the generated code?
2. How do we minimise AI verbosity?
3. Do the video's comments contain solutions?

Short answers: the video gives one real method for (1), none for (2) (he asks viewers for a fix),
and the comments give several fixes for (2) and a few for (1), but no complete system.

## What the video says

### Ownership and understanding (his one concrete method)

Build it twice.

1. Think about the shape of the system, then let the AI build a throwaway version fast. Iterate
   until it works. Accept that it has too much code and too many tests. The point is learning
   what the system actually needs.
2. Then design version 2 deliberately: the components, the structure of each, the data and
   database shapes, the tests. Have the AI build against that design, while understanding
   everything that goes in.

His check is line count, not as a goal but as evidence: same features, more thought, far less
code. His current project went from about 100,000 lines to an expected 25,000 to 30,000.

He frames this as the old prototype-then-real-build habit, done with AI. Use slop to explore,
never to ship.

### Verbosity (unsolved in the video)

- He told the model "no narrative" and got narrative about there being no narrative.
- Long output costs real time: hundreds of words where one sentence would do.
- Caveman-style prompting shortens output but makes it unreadable.
- He explicitly asks for a fix.

### No pushback

The AI never says a suggestion is poor and should be discussed first. It returns a
thousand-line PR done exactly as asked. This hurts most when the developer does not know the
codebase, and juniors never get to see what good looks like.

### Test bloat and CI

Every feature request produces more end-to-end tests. They accumulate into thousands of slow,
flaky tests. A change that touches a hundred tests should alarm you. The developer has to
decide what is being tested and trim.

### Context switching

Agents are both faster and slower than a person: 10 to 20 minute waits tempt you to start
another task. He manages one to two concurrent tasks; at three or four he loses track. Chat
and messages during a wait are fine; a second feature is not.

### Hype and juniors

- Ignore "do X or you won't make it". How agents are used changes completely year to year.
- Juniors are expected to move at senior speed without the understanding. His advice: keep
  building technical knowledge by hand, and be the person who decides the tests, layout and
  trade-offs, not a proxy typing someone's words into a text box.

## What the comments offer

Like counts are low across the board (the video was hours old), so treat these as untested
suggestions, not consensus.

### Verbosity fixes

| Fix | Detail |
|---|---|
| Positive format instruction | Say "output a list only" instead of "no narrative". Negation plants the concept. |
| Output contract | Require a fixed JSON shape with one `comments` field where prose is allowed. The commenter reports recent models hold the shape reliably. |
| TL;DR first | Rule that every reply starts with a summary; read the rest only when needed. |
| "For a human" | Ask for the report "for a human" or in "human register". One commenter's theory: models are trained to be verbose when reporting to other agents. |
| Succinct suffix | Put "Be very succinct" at the end of the system prompt. |
| Word cap | Ask for the explanation in simple language in under 50 words. |
| Diagrams | Render technical documents as diagrams, with the text in toggleable captions. |
| Two-pass "minimalism" skill | See below. |

One dissent: a commenter argues LLMs are narrative by construction and this cannot be fully
prompted away.

### The "minimalism" skill a commenter pasted

A full skill definition. Its structure, paraphrased:

- **First pass, write short and plain from the start:** lead with the point, short sentences,
  bullets for parallel items, concrete nouns and numbers, everyday words, no filler openers, no
  hedging stacks, active voice.
- **Shape by question type:** yes/no gets the word plus one line of why; "where is X" gets
  `path:line`; "what changed" gets a bullet per change; "A or B" gets the recommendation first
  and the deciding trade-off.
- **Second pass, mandatory condensing:** re-read and ask of each sentence whether it can go or
  shrink without losing meaning. Cut redundancy, filler, restatements, lists of absences, and
  extra examples.
- **Must stay:** load-bearing distinctions and edge cases, exact identifiers, numbers and error
  strings, the one fact the reader came for, warnings and bad news.
- **Goal:** density, not blind brevity. If the short version says less, it is too short.

### Understanding and ownership fixes

- **Planted bugs** (most-liked substantive comment): ask the AI to introduce bugs in a part of
  the system you do not know, then find and fix them by hand using the code and docs.
- **Design doc first:** give the agent a structured design doc with specifics, rules,
  constraints and paths, not "build me an app".
- **Prototype high, rewrite low:** prototype in Python to settle the API and data shapes, then
  have the agent rewrite in C or Rust.

### Other observations from the comments

- Product specs written with AI went from a 10 to 15 minute read to two hours.
- Agents over-engineer simple tasks, and leak inner-monologue into code comments and docs.
- Several people independently report that three concurrent agent tasks is too many.
- One counter-example to "no pushback": a model did push back, and its recommended best
  practice turned out to be wrong when checked against the docs. Pushback needs verifying too.
- Run agents sandboxed, especially in auto-approve mode on security-sensitive code.
- One commenter says they built their own "AI coding manager" but gives no details.

## Proposed workflow

No new system is needed. This is a set of gates on top of an existing coding agent.

| # | Gate | What it does | Addresses |
|---|---|---|---|
| 1 | Spike, then design | Agent builds a throwaway version on a branch. The developer then writes the design: components, interfaces, schema, test list. The agent only fills in bodies against it. | Ownership |
| 2 | Objections before code | Agent must list what it disagrees with and one alternative before writing anything, then waits. | No pushback |
| 3 | Small steps | Cap each step at a readable size (starting point: 200 changed lines), then stop for review. | Thousand-line PRs |
| 4 | Developer owns the test list | Agent may not add tests, especially end-to-end ones, without asking. | Test bloat |
| 5 | Fixed report shape | Every report: one-line verdict, files changed, risks, questions. Anything else only on request. | Verbosity |
| 6 | Comprehension check | Before merging, the developer explains the diff back, or does the planted-bug exercise on unfamiliar parts. | Understanding |
| 7 | Line count as a check | Compare the real build to the spike. If it is not much smaller, the design step was skipped. | Ownership |
| 8 | Concurrency limit | One feature task at a time, two at most. | Context switching |

The 200-line cap and the two-task limit are starting values, not measured ones.

## State of this setup (as of this session)

- The `superpowers` plugin already covers gates 1 and 2 through its brainstorming and
  plan-writing skills.
- The `ponytail` plugin already covers the terse-output half of gate 5 and the
  smallest-change habit.
- Not covered anywhere: the step-size cap (3), the test rule (4), the report shape (5), the
  comprehension check (6).
- This repo (`C:\Projects\ai\rag`) has no `CLAUDE.md`. The missing gates were proposed as about
  ten lines in a new one. **Not yet written.**

### Draft `CLAUDE.md` lines (not applied)

```markdown
# Working rules
- Before writing code, list your objections to the request and one alternative. Wait for my answer.
- Build against the design I give you. If there is none, ask for one or propose one and wait.
- Stop for review after about 200 changed lines. Do not continue to the next step unprompted.
- Do not add or change tests beyond the ones I listed. Ask first, especially for end-to-end tests.
- Report in this shape only: one-line verdict, files changed, risks, questions for me.
- Put the answer first. Format instructions are positive: "a list of X", never "no Y".
- Keep exact identifiers, numbers, error strings and bad news. Cut everything else you can.
- Before I merge, ask me to explain the change back in two sentences.
```

## How the video was fetched (for repeating this on another video)

YouTube had flagged this network as bot traffic, which blocked every unauthenticated route.

Failed:
- Direct page fetch: redirected to a Google "unusual traffic" page.
- `yt-dlp` (installed in a throwaway venv, with five different client types): "Sign in to
  confirm you're not a bot".
- Third-party transcript sites and Invidious/Piped mirrors: 403, 502, or blocked upstream.

Worked:
- The oEmbed endpoint returned the title and channel even while blocked:
  `https://www.youtube.com/oembed?url=<video url>&format=json`
- The Claude in Chrome extension, after the user ticked the CAPTCHA by hand (the agent may not
  solve CAPTCHAs).

Details that cost time in the browser:
- Page variables such as `ytInitialPlayerResponse` are not visible to injected scripts, and
  re-fetching the page HTML returned no caption tracks. Use the UI: expand the description,
  click "Show transcript", and read the transcript engagement panel's text.
- Script results are truncated to roughly 1,000 characters. To extract long text, put it in an
  `<article>` element, hide `ytd-app`, and use the page-text tool, which returns the whole
  thing.
- `innerHTML` assignment is blocked on YouTube (Trusted Types). Build elements with
  `createElement` and `textContent`.
- Comments load 20 at a time and only when the last loaded comment is near the viewport.
  Scrolling to the page bottom overshoots, because the sidebar is longer than the comment
  list. Scroll the last `ytd-comment-thread-renderer` into view, nudge down, wait, repeat until
  the count stops growing.
- The comment count in the header includes replies (119 here against 87 threads).

## Not done

- Reply threads were not read.
- None of the commenters' fixes were tested.
- The `CLAUDE.md` above is a draft and was not created.
- The proposed workflow has not been tried on this repo.
