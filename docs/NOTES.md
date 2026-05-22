# Lessons learned
- Don't speed-run through planning phases just so you can start building something and getting dopamine hits for seeing a cool result inside the browser. BMAD is geared towards carefully guiding the AI by setting up guardrails. Focus on learning about how to enforce good coding practices, instead of building fast.
- Think carefully about the features, architecture and code structure in the beginning because it's going to be slow to refactor all of it later. If you already have tests, it's going to be even slower.

# Other considerations
- After having worked on data science algorithms and physics simulations for almost a year, I immediately focused on the energy & engineering aspects of my application, rather than paying attention on building a web application that followed best practices. I think I missed the point of the exercise, which asked to implement a very simple application with focus on best practices.
- After implementing an MVP with vanilla JS, I kind of miss having React components
- Story creation and sprint planning are my least favorite steps

# Doubts
- Not sure why AI artifacts are getting created in different folders? I expected everything to be inside _bmad-output, but at some point some stories were added to the implementation folder. Product brief and PRD are placed in the .claude folder.

# TODO
- Update readme
- Finish tests, accessibility, security

### Create stories for
- E2E tests
- Playwright
- Check WCAG violation/Accessibility
- Security review
- Review dead code and simplify if possible
