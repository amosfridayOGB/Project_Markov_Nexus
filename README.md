# Project Markov Nexus: Algorithmic Multi-Touch Attribution Engine

🕸️ **Predictive State-Transition Modeling & Channel Removal Effect Kernel**

---

## 📊 System Overview

![Markov Nexus Dashboard Preview](assets/nexus_preview.png)

---

## 📈 Executive Abstract

In high-density digital customer acquisition funnels, static heuristic attribution models (First-Touch, Last-Touch, Linear) misjudge channel performance by evaluating touchpoints in isolation. **Project Markov Nexus** resolves this systemic analytical error by modeling the customer journey as a discrete-time first-order Markov Chain. 

By mapping sequential user paths into a dynamic transition probability network, the system calculates the exact stochastic dependencies between ad groups. It introduces a predictive algorithmic framework that measures the **Removal Effect** of individual channels, determining the absolute drop in net conversions if a specific platform undergoes a programmatic blackout.

---

## 🔬 Mathematical Framework

The system maps customer journeys across a finite state space:

$$S = \{\text{START}, \text{meta\_awareness}, \text{meta\_conversion}, \text{whatsapp\_trigger}, \text{CONVERSION}, \text{DROP\_OFF}\}$$

The core matrix kernel calculates the transition probability $P_{ij}$, which defines the likelihood of a user transitioning from state $i$ to state $j$:

$$P_{ij} = P(X_{t+1} = j \mid X_t = i) = \frac{C_{ij}}{\sum_{k \in S} C_{ik}}$$

Where:
* $C_{ij}$ represents the raw frequency count of sequential transitions observed from state $i$ to state $j$ across all historical path vectors.
* $\sum_{k \in S} C_{ik}$ represents the total outward structural flux exiting state $i$.

### The Removal Effect Principle
To isolate the true systemic value of channel $c$, the engine recalculates the universal system conversion probability vector $\alpha$ after setting the transition row matrix parameters for $c$ directly to an absorption death state:

$$P(c \rightarrow \text{DROP\_OFF}) = 1.0$$

The resulting variation yields the absolute **Removal Effect Index ($R_c$)**:

$$R_c = \frac{\alpha_{\text{base}} - \alpha_{\text{conditioned}}}{\alpha_{\text{base}}}$$

---

## 📂 System Topology & Architecture

```text
Project_Markov_Nexus/
│
├── assets/
│   └── nexus_preview.png           # UI dashboard visualization snapshot
│
├── core_logic/
│   └── user_journey_sequences.csv  # 5,000 synthetic stochastic journey logs
│
├── generate_journeys.py            # Transition probability simulation script
├── engine.py                       # Matrix processing object-oriented kernel
├── app.py                          # Streamlit UI simulation dashboard
├── requirements.txt                # System environment manifest
└── README.md                       # High-end mathematical engineering whitepaper
