# Tutorial 4: Modeling

This Chapter covers the **design and integration of custom components* in RSTT. We implement reasonable models to generate realistic dataset emulating the profesional League of Legend ecosystem.

---

📝 **About This Tutorial**

* 📚 **Focus**: Modeling Riot Games' *Global Power Ranking (GPR)* system
* 🎯 **Goal**: Simulate realistic *League of Legends* competitive seasons using the RSTT framework
* 🧪 **Output**: Custom simulation models, GPR implementation, comparative studies and ablation experiments

---

## 👋 Introduction

This tutorial is a **practical implementation of Riot Games' Global Power Ranking (GPR)** — a system designed to evaluate and compare the strength of *League of Legends* teams across international competitions.

Using the RSTT framework, you will simulate a realistic esports season and replicate the logic and structure of a competitive dataset., including time-evolving player skill, meta shifts and qualifications.

This is a **advanced tutorial**, ideal for users ready to go beyond basic usage. You’ll work hands-on with simulation models and internal workflows of RSTT.

---


## 🏗️ Project Overview


### 🔧 Tasks

You’ll complete the following core tasks:

* Implement a `Competition` class
* Build an automated yearly calendar
* Create a `Player` class with time-varying skill
* Design a `Solver` for unbalanced matches and meta shifts
* Implement a flexible version of the *Global Power Ranking*
* Define simulation-specific metrics
* Conduct comparative and ablation studies on synthetic data

---


### 📂 Materials

The tutorial includes:

* **`4_Modeling_GPR.ipynb`** – A step-by-step notebook walking through all project tasks, with coding exercises and detailed explanations
* **`Verification.ipynb`** – Contains test cells and sanity checks to validate your implementation
* **`exercises/`** – Starter code and scaffolding for you to work from
* **`project/`** – Full solution to the modeling project
* **`simulation/`** – Experimental modules for metrics, simulation protocols, and model parameterizations
* **`data/`** – Includes:

  * `teams.json` with GPR ratings from 2024
  * `qualifications.fson` describing tournament dependencies and qualification rules
* **`Experiments.ipynb`** – Evaluation notebook for testing your models via comparative studies and ablation experiments

---

### 📎 Global Power Ranking

Riot’s *Global Power Ranking* (GPR) is an Elo based ranking system that evaluates the strength of teams by combining **team performance** and **regional context**.


> For full details, see Riot’s [Dev Diary on GPR](https://lolesports.com/en-US/news/dev-diary-unveiling-the-global-power-rankings)

---

#### Design Summary:

* **Elo Rationale**:

  With rating updated on a Game basis:

  $$
  \text{Pafter} = \text{Pbefore} + \text{I} \times (\text{W} -\text{We})
  $$

  And the expected score estimated by:

  $$
  \text{We} = \frac{1}{10^{-(\text{dr})/600} + 1}
  $$


* **Ratings**: Rating for both team and region

* **Power Score**: Computed as a weighted combination:

  $$
  \text{Power Score} = 0.8 \times \text{Team Elo} + 0.2 \times \text{Region Elo}
  $$

* **Match Weighting (K-factors or I)**: Important matches (e.g., playoffs, international games) have a larger impact on Elo updates.

* **Update**: Ratings use recent match history.

  * Team Elo: last **2 years**
  * Region Elo: last **3 years** (international encounters)

> For full details, see Riot’s [Dev Diary on GPR](https://lolesports.com/en-US/news/dev-diary-unveiling-the-global-power-rankings) and its [Introduction](https://lolesports.com/en-US/news/introducing-lol-esports-global-power-rankings-powered-by-aws)

---

#### Context

The claim is:
> "The dynamic nature of League of Legends—with its frequent meta shifts, varying regional league structures, and diverse play styles—demands a more nuanced approach."

---

#### Evaluation

The system has been evaluated with predictive accuracy.

---


## ⚠️ Prerequisites

This chapter assumes **strong familiarity** with the RSTT framework and its abstractions.

Please make sure you’ve completed:

* [Tutorial 1: Basics](https://github.com/Ematrion/rstt/blob/main/tutorials/1_Basics/1_Basics.ipynb)
* [Tutorial 2: Integration](https://github.com/Ematrion/rstt/blob/main/tutorials/2_Intergration/2_Integration.ipynb)
* Optionally: [Tutorial 3: Research Reproduction](https://github.com/Ematrion/rstt/blob/main/tutorials/3_Research_Reproduction/3_Solution)

You should also:

* Understand the 5 core RSTT components: `SPlayer`, `SMatch`, `Solver`, `Ranking`, and `Scheduler`
* Be comfortable with the user API and top-level abstractions
* Be familiar with the ranking class design and its components: `Standing`, `RatingSystem`, `Observer`, and `Inference`

---


## 🧠 Learning Outcomes

By the end of this tutorial, you will be able to:


### Automation
- Understand the scheduler run() worflow behind data generation
- Understand how rankings are updated via `observer.handle_observations` 
- Design a custom `Competition` class with valid and reusable outputs  

### Ranking Design
- Grasp the *implicit agreements* between Ranking's components
- Use `SPlayer` directly as a rating object, bypassing `RatingSystem` constraints  
- Implement flexible versions of `Inference`, `Observer`, and `RatingSystem`  
- Tune ranking state with the ordinal method

### Modeling
- Understand the interactions between `SPlayer`, `Solver`, and `SMatch`  
- Work around current `SMatch` constraints.
- Implement a time-varying `SPlayer` model  
- Create a `Solver` that captures balance shifts and meta variance  


