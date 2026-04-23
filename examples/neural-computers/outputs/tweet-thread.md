## Twitter Thread Draft

**Tweet 1 (hook):**
What if the AI didn't use the computer? What if the AI *was* the computer?

Neural Computers: no CPU, no OS, no bash. A neural network that learned what computation looks like by watching thousands of hours of terminal sessions.

The forward pass is the clock tick.

**Tweet 2 (the distinction):**
The distinction matters.

Agent: LLM observes screen → decides what to click → sends action to a REAL computer

Neural Computer: you press a key → the neural network generates the next frame of what the terminal would show

One controls a computer. The other replaced it.

**Tweet 3 (what works):**
The prototype (arxiv 2604.06425) renders terminals that pass a quick glance. Correct fonts, ANSI colors, cursor behavior.

Simple commands work: pwd, date, whoami.

Two-digit addition? Falls apart.

The gap between LOOKING like a computer and BEING one is the entire research problem.

**Tweet 4 (why it matters):**
Why care if it barely computes?

A neural substrate has properties silicon doesn't:
- Differentiable (you can't take the gradient of bash)
- Interpolable ("halfway between two programs" = a point in latent space)
- Trainable (show it behavior instead of writing code)

These aren't improvements. They're new operations.

**Tweet 5 (the hard barrier):**
The lead author is blunt: "asking current DiT-based video models to carry stable reasoning may simply be the wrong bet."

It can fake a terminal. It can't do 2+2 reliably.

Bridging that gap may need architectures that don't exist yet. Estimated: ~3 years, up to 1000T parameters.

**Tweet 6 (the form):**
This post was written agentically. I steered, an agent researched.

The post has two layers: a human layer (my voice, my judgment) and an agent layer (structured research trace with confidence annotations, provenance, uncertainty).

New substrates need new coordination protocols. This is one embryo of one.

**Tweet 7 (the parallel):**
The parallel isn't lost on me: Neural Computers train on I/O traces, recordings of computers being used.

This blog post is an I/O trace of a human-agent research session. Human section = the rendered frame. Agent section = the latent state.

The form mirrors the content.

**Tweet 8 (CTA):**
Full post: human take on Neural Computers, structured agent context block underneath, and a five-tier tech tree from what's been demonstrated to what's speculative.

Written for you and your agent: [LINK]

---
