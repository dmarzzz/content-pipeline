---
title: "Neural Computers: Exploring a New Machine Form from I/O Traces"
date: 2026-04-11
kind: research_trace
tldr: >
  Neural Computers (arXiv 2604.06425) propose neural networks that replace conventional computers by learning executable dynamics from I/O traces. The prototype renders terminals visually (pwd, date work) but fails at symbolic computation (2+2 is unreliable). The key insight: a neural substrate is differentiable, interpolable, and trainable by demonstration, properties silicon doesn't have. These are theoretical consequences, not demonstrated capabilities. The hard barrier is Tier 2 (computational correctness), which may require architectures that don't exist yet. The lead author estimates ~3 years and 10T-1000T parameters.
key_findings:
  - "Neural Computers are distinct from agents (which control real computers) and world models (which predict alongside real systems). The paper explicitly rejects both framings. NCs are organized around 'runtime' where capabilities enter the learned latent state directly."
  - "The model lineage is Wan2.1 -> SkyReels-V2 -> Matrix-Game-2 -> Neural Computer. Matrix-Game-2 IS a surgically-modified Wan2.1 (not two separate models composed). The Wan2.1 credit in the NC README is transitive."
  - "110 hours of supervised (Claude-driven) GUI data outperformed ~1,400 hours of random synthetic data. Data quality dominates data quantity for NC training. This is the paper's strongest empirical contribution."
  - "The 'wrong bet' quote ('asking current DiT-based video models to carry stable reasoning may simply be the wrong bet') comes from lead author Mingchen Zhuge's personal blog essay, not the multi-author paper. The blog carries a disclaimer that views represent Zhuge alone."
  - "'You can't take the gradient of bash' is our original framing, not from the paper. The differentiability angle is a logical inference from the neural substrate, not a claim the authors make. The paper's framing is about 'runtime' and 'machine forms,' not calculus."
citations:
  - url: https://arxiv.org/abs/2604.06425
    title: "Neural Computers"
  - url: https://metauto.ai/neuralcomputer/
    title: "Neural Computer: A New Machine Form Is Emerging"
  - url: https://github.com/metauto-ai/NeuralComputer
    title: "NeuralComputer data pipeline"
  - url: https://github.com/SkyworkAI/Matrix-Game
    title: "Matrix-Game (includes MG2 and MG3)"
  - url: https://arxiv.org/abs/2508.13009
    title: "Matrix-Game-2"
  - url: https://huggingface.co/Skywork/Matrix-Game-2.0
    title: "Matrix-Game-2.0 model card (MIT license)"
  - url: https://huggingface.co/Skywork/Matrix-Game-3.0
    title: "Matrix-Game-3.0 model card"
  - url: https://github.com/SkyworkAI/Matrix-Game/blob/main/Matrix-Game-2/wan/modules/action_module.py
    title: "ActionModule source code"
  - url: https://github.com/guandeh17/Self-Forcing
    title: "Self-Forcing (NeurIPS 2025)"
  - url: https://gamengen.github.io/
    title: "GameNGen (neural DOOM, Google 2024)"
  - url: https://oasis-model.github.io/
    title: "Oasis (neural Minecraft, Decart 2024)"
  - url: https://diamond-wm.github.io/
    title: "DIAMOND (diffusion Atari, NeurIPS 2024)"
  - url: https://deepmind.google/models/genie/
    title: "Genie 3 (DeepMind, Jan 2026)"
  - url: https://arxiv.org/abs/2507.08800
    title: "NeuralOS (Waterloo, Jul 2025)"
  - url: https://huggingface.co/spaces/dn6/matrix-game-2
    title: "Matrix-Game-2 HF Space (free demo)"
claims:
  - id: claim-nc-definition
    text: "A Neural Computer is a neural network that replaces a conventional computer rather than controlling one."
    confidence: 0.95
  - id: claim-not-world-model
    text: "The NC paper explicitly rejects the world-model framing."
    confidence: 0.95
  - id: claim-model-lineage
    text: "The NC model lineage is Wan2.1 -> SkyReels-V2 -> Matrix-Game-2 -> Neural Computer. MG2 IS a modified Wan2.1, not a separate model."
    confidence: 0.95
  - id: claim-action-conditioning
    text: "Matrix-Game-2 uses per-frame keyboard (cross-attention) and mouse (self-attention) conditioning in all 30 DiT blocks, with keyboard_dim_in as a config integer."
    confidence: 0.95
  - id: claim-symbolic-failure
    text: "The NC prototype fails at symbolic computation, including two-digit addition."
    confidence: 0.95
  - id: claim-supervised-data
    text: "110 hours of supervised (Claude-driven) GUI data outperformed ~1,400 hours of random synthetic data."
    confidence: 0.95
  - id: claim-wrong-bet
    text: "The 'wrong bet' quote comes from Zhuge's personal blog essay, not the multi-author paper."
    confidence: 0.9
  - id: claim-gradient-of-bash
    text: "'You can't take the gradient of bash' is our original framing, not from the paper. The differentiability angle is a logical inference from the neural substrate."
    confidence: 1.0
critique:
  verdict: "The research session successfully mapped the NC concept, architecture, and landscape. The biggest risk is that several of our speculative framings (differentiability, Kolmogorov complexity, Von Neumann dissolution) were projections not grounded in the paper. We caught and corrected this when we read the actual paper, but the 'gradient of bash' framing persisted as the blog title despite being our inference, not the authors' claim. This is disclosed in the blog post and in this trace."
  gaps:
    - "Did not read the NC paper in full — relied on web_fetch summaries and the blog post. Some claims about paper content are second-hand."
    - "Did not verify whether the NC team plans to rebase on Matrix-Game-3 (which has memory mechanisms NCs need)."
    - "Did not investigate the Google Generative OS approach in depth (LLM generating HTML, different paradigm)."
    - "The 10T-1000T parameter estimate was not independently verified — it's the lead author's personal speculation."
  errors:
    - "Timeline estimates (3 years, 10T-1000T params) are author aspiration, not empirically grounded. We flag this but could have emphasized it more."
    - "The 'wrong bet' attribution was initially incorrect (attributed to 'the authors' plural rather than Zhuge's solo essay). Fixed during vulnerability audit."
metadata:
  kind: research_trace
  id: "trace-20260411-002"
  trace_id: "session-20260411-neural-computers"
  schema_version: "0.1"
---

## Research question

Explore the metauto-ai/NeuralComputer repo and the Neural Computer concept. Understand the paper, the model lineage, the adjacent landscape, and produce a blog post with structured agent context for the agentic age.

## Synthesis

Neural Computers (NCs) are neural networks that replace conventional computers rather than controlling them. The forward pass is the clock tick; the latent state unifies memory, computation, and I/O. Trained on video recordings of computers being used, NCs learn to predict the next frame given current state and user input.

The NC prototype is built on Wan2.1 -> Matrix-Game-2 (1.8B params, action-conditioned causal DiT with ActionModules in all 30 blocks). Simple terminal commands render correctly; symbolic computation fails. The paper is a position paper with prototype validation, not an empirical breakthrough.

The tech tree has five tiers: Tier 0 (demonstrated foundations), Tier 1 (visual fidelity, partially demonstrated via MG3 for games), Tier 2 (computational correctness, the hard barrier), Tier 3 (CNC programmability conditions), Tiers 4-5 (speculative emergent properties and paradigm implications).

The 'gradient of bash' framing is our original contribution: conventional computers are discrete and non-differentiable; a neural substrate is continuous and differentiable by construction. This is technically true but not a claim in the paper, and no one has demonstrated backpropagation through an NC.

The blog post format — human layer for judgment, agent layer for verification — mirrors the NC concept: the human section is the 'rendered frame,' the agent section is the 'latent state.' New substrates need new coordination protocols.

