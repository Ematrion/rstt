# Contributing to RSTT

Contributions of various nature are greatly appreciated. The package is in the early stages of long journey and you are welcome on board.


## Community Growth

Use the package, cite it, spread the word and contribute to its popularity.
Join discord and exchange with us. This helps more than anything.


## Reporting Issues

Before submission, please check the folowings

- Make sure there is not already an open issue on the same matter
- Provide a minimal code example to replicate the issue
- Specify the expected behaviour
- In simulation, make sure it is not a model mispecification that results in unexpected behaviour.
(The opposite shoudl also apply, when observing an expected behaviour make sure it is indeed the results of a well specified model and not a bug...)

Note: Bug exist even when they are not catched.
If you are unable to reproduce your issue, but also are certain that there is one that need to be fixed. 
Join discord and talk about it.


## Features Addition

Anything missing? Something you would like to do but can not?
Redundant code that your keep rewriting poject after project and could be provided by the package?

- Open feature request on Github or on Discord
- Justify why it is of public interest.


## Performance Optimization

Perofrmance is an important yet challenging aspect of simulation. When it comes to RSTT, automatic sorting of ranking and matching strategy in competition can be resources demanding. You can help by identifying bottleneck, improve algorithm or even highlight typcal slow code and provide faster alternatives. 


## Documentation

Anything that improves the user experience is welcome
- Correct typos
- Adapt the language
- Improve style and layout
- Add simple explicit code examples
- Include model citations, sources and references.
- Improve tutorials


## Package Scope

Defining the current scope of application is an important aspect of the devellopement. What model should be included, what features are typically needed in the field. 
Keep in touch with litterature about simulation based reasearch and join discord to discuss if and how RSTT provides supports.


## Contributing Code

- Comply with python coding style best practicies [pep8](https://peps.python.org/pep-0008/).
- Do not increase dependencies without first talking with maintainers.
- Use type annotations and typecheck decorator from typeguard. Favor duck-typing.
- Document functionnalities using docstring.
- When implementing model, link sources in comment.
- When implementing an algorithm, use the same naming convention as the linked source(s) for both functions and variables. In some cases this results in hardly readable code - explain it in comments or add a direct link to a verbose verison of the algorithm.
- If an author add a side comment on a concept or algorithm steps in a source paper, mention it.
- If a sources is unclear, comment it.
- Arbitrary choices must be explained clearly in comments.
- Include corresponding pytest. If your code is a bug fix, your test MUST fail first on the previous implementation.


#### Testing requirement

- All pytest tests must pass (100% pass rate)
- High coverage rate
- Examples on github must not break
- Tutorials on github must not break

In cases where those requierements can not be fullfiled, contact maintainers before any pull request.


#### Content limitation

RSTT is not a creative package, it provides scientical tools. RSTT must match sources behaviour.
- DO NOT pull your own model. First write a paper, publish it, and link that paper to us.
- DO NOT FIX 'outside' bugs without a source for the fix.
- AS-IS implementation of sources. If an algorithm has an illed-defined behaviour in edge cases, it is the user responasbility to find is own solution for it. If possible, it should be mentioned in the documentation and advise on best/common practices.

