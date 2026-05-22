---
storyKey: 3-12-accessibility-audit-and-color-contrast-fixes
storyId: "3.12"
title: Accessibility Audit & Color Contrast Fixes
epicId: 3
epicTitle: Quality, Reliability & Security
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 3-12: Accessibility Audit & Color Contrast Fixes

## Story

As an accessibility advocate,
I want automated accessibility scanning and color contrast fixes,
So that the application meets WCAG 2.1 Level AA standards.

**Requirements Covered:** WCAG 2.1 Level AA, Accessibility Best Practices

---

## Acceptance Criteria

**Given** I run automated accessibility tests with jest-axe
**When** the tests execute
**Then** no accessibility violations are found

**And** jest-axe is installed: npm install --save-dev jest-axe axe-core

**Given** I run Lighthouse accessibility audit via Chrome DevTools
**When** the audit completes
**Then** accessibility score is ≥90

**Given** I check color contrast of text on background
**When** I measure contrast ratio using WebAIM Contrast Checker
**Then** normal text contrast is ≥4.5:1

**And** large text (18pt+ or 14pt bold) contrast is ≥3:1

**Given** I audit the current styling
**When** I find insufficient contrast (e.g., error messages in light red)
**Then** I fix by using darker color that meets 4.5:1 ratio

**And** accessibility checklist is completed with all items verified

---

## Tasks & Subtasks

- [ ] Install jest-axe for automated accessibility testing
  - [ ] Install: `npm install --save-dev jest-axe axe-core`
  - [ ] Verify installation in package.json devDependencies
  - [ ] Verify axe-core installed as dependency of jest-axe

- [ ] Create accessibility test suite
  - [ ] File: `frontend/__tests__/accessibility.test.js`
  - [ ] Test: "Page has no accessibility violations"
    - [ ] Render app component
    - [ ] Run axe.toHaveNoViolations() assertion
    - [ ] Verify no violations found
  - [ ] Test: "Form inputs are accessible"
    - [ ] Check all inputs have labels
    - [ ] Check labels have for attributes
    - [ ] Verify no violations in form structure
  - [ ] Test: "Error messages are accessible"
    - [ ] Display error message
    - [ ] Verify aria-invalid and aria-describedby present
    - [ ] Run axe check
  - [ ] Test: "Tab navigation is accessible"
    - [ ] Check tabs have role="tab"
    - [ ] Check tablist has role="tablist"
    - [ ] Verify aria-selected attributes
    - [ ] Run axe check
  - [ ] Test: "Charts are accessible"
    - [ ] Check chart containers have role="img"
    - [ ] Check aria-label present and descriptive
    - [ ] Run axe check

- [ ] Run Lighthouse audit
  - [ ] Open Chrome DevTools (F12)
  - [ ] Go to Lighthouse tab
  - [ ] Run audit with these categories: Accessibility
  - [ ] Verify Accessibility score ≥90
  - [ ] Note any issues found
  - [ ] Document fixes needed

- [ ] Check color contrast ratios
  - [ ] Use WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/)
  - [ ] Test all text color combinations in app:
    - [ ] Form labels (text color on form background)
    - [ ] Button text (text color on button background)
    - [ ] Error messages (error text color on background)
    - [ ] Result card values (text color on card background)
    - [ ] Links (if any)
  - [ ] Verify normal text contrast ≥4.5:1
  - [ ] Verify large text (18pt+ or 14pt bold) contrast ≥3:1
  - [ ] Document any colors that fail

- [ ] Fix insufficient color contrast issues
  - [ ] Identify all colors that don't meet WCAG AA standards
  - [ ] Update CSS color values to darker/lighter colors that meet ratios
  - [ ] Common fixes:
    - [ ] Lighten button text (white on light background)
    - [ ] Darken error message text (red/pink text may be too light)
    - [ ] Darken placeholder text if visible and contrasting
  - [ ] Re-test with WebAIM Contrast Checker after each fix
  - [ ] Verify visual appearance is still acceptable

- [ ] Verify focus indicators have sufficient contrast
  - [ ] Use WebAIM Contrast Checker for focus outline color on button backgrounds
  - [ ] Verify focus outline contrast ≥3:1 with background
  - [ ] Adjust CSS if needed: use darker outline color or add background color change on focus

- [ ] Check text size and spacing
  - [ ] Verify body text size ≥14px (base font size)
  - [ ] Verify line height ≥1.5x (for readability)
  - [ ] Verify button text size ≥14px
  - [ ] Verify no important text <12px
  - [ ] Verify input labels are readable

- [ ] Test zoom and responsive layout
  - [ ] Zoom page to 200% in browser (Ctrl/Cmd + +)
  - [ ] Verify all content is still readable
  - [ ] Verify no horizontal scrolling required at 200% zoom
  - [ ] Verify buttons still clickable (>44x44px recommended)
  - [ ] Test on mobile viewport (375px width)

- [ ] Run accessibility checklist (WCAG 2.1 Level AA)
  - [ ] Perceived: Text Alternatives
    - [ ] All images have alt text or aria-label
    - [ ] Charts have aria-label descriptions
  - [ ] Perceived: Contrast
    - [ ] All text ≥4.5:1 contrast (normal) or ≥3:1 (large)
  - [ ] Operable: Keyboard Accessible
    - [ ] All interactive elements keyboard accessible
    - [ ] Tab order logical
    - [ ] Focus indicators visible
    - [ ] No keyboard traps
  - [ ] Operable: Enough Time
    - [ ] No content that changes or disappears without user control
  - [ ] Operable: Seizures and Physical Reactions
    - [ ] No content that flashes >3 times per second
  - [ ] Operable: Navigable
    - [ ] Purpose of links is clear
    - [ ] Page has descriptive title
    - [ ] Focus order is meaningful
  - [ ] Understandable: Readable
    - [ ] Page language identified (lang attribute in HTML)
    - [ ] Text is clear and understandable
  - [ ] Understandable: Predictable
    - [ ] No unexpected context changes on input focus
    - [ ] Consistent navigation across pages
  - [ ] Understandable: Input Assistance
    - [ ] Form inputs have labels
    - [ ] Error messages are descriptive
    - [ ] Form submission is reversible or confirmed
  - [ ] Robust: Compatible
    - [ ] HTML is valid
    - [ ] ARIA attributes are valid
    - [ ] Parsing has no errors

- [ ] Document accessibility improvements
  - [ ] Create ACCESSIBILITY.md file listing:
    - [ ] WCAG 2.1 Level AA compliance checklist
    - [ ] Color contrast ratios used
    - [ ] Keyboard navigation documented
    - [ ] Screen reader support documented
    - [ ] Testing tools and procedures

- [ ] Create automated accessibility test in CI/CD (optional)
  - [ ] Add jest-axe test to CI/CD pipeline
  - [ ] Fail build if accessibility violations found
  - [ ] Add Lighthouse CI (optional, more advanced)

---

## Dev Notes

**Architecture Context:**
Accessibility audit is the final validation that Stories 3-10 and 3-11 (semantic HTML, ARIA, keyboard navigation) are correctly implemented. This story uses automated tools (jest-axe, Lighthouse) plus manual testing to verify WCAG 2.1 Level AA compliance.

**Key Standards (WCAG 2.1 Level AA):**
- **Contrast (4.5:1)**: Text and background must have sufficient contrast for readability
- **Keyboard accessible**: All interactive elements must work with keyboard only
- **Focus visible**: User can see which element has focus
- **Form labels**: All inputs have associated labels
- **Error messages**: Clear, descriptive error messaging
- **Semantics**: Proper HTML structure and ARIA attributes

**Testing Tools:**
- jest-axe: Automated accessibility testing in Jest
- Lighthouse: Chrome DevTools audit (scores 0–100)
- WebAIM Contrast Checker: Manual color contrast verification
- NVDA/VoiceOver: Screen reader testing (from Story 3-11)
- axe DevTools: Browser extension for quick checks

**Key Metrics:**
- Jest-axe: 0 violations (all tests pass)
- Lighthouse: Accessibility score ≥90
- Contrast: Normal text ≥4.5:1, large text ≥3:1
- Focus: Always visible, sufficient contrast

**Dependencies:**
- jest-axe (add to devDependencies)
- axe-core (automatic dependency of jest-axe)
- No changes to production dependencies

**Related Stories:**
- Story 3-10 (Semantic HTML & ARIA) — provides ARIA attributes tested here
- Story 3-11 (Keyboard Navigation) — provides keyboard support tested here

**Files Modified/Created:**
- `frontend/__tests__/accessibility.test.js` — NEW, automated accessibility tests
- `frontend/styles/main.css` (or equivalent) — update color values for contrast
- `ACCESSIBILITY.md` — NEW, accessibility documentation
- `package.json` — add jest-axe, axe-core to devDependencies

---

## Dev Agent Record

### Implementation Plan

(To be filled in during implementation)

### Debug Log

(To be filled in during implementation)

### Completion Notes

(To be filled in during implementation)

---

## File List

**New Files:**
- frontend/__tests__/accessibility.test.js
- ACCESSIBILITY.md

**Modified Files:**
- frontend/styles/main.css (or equivalent)
- package.json (add dependencies)

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-22: Story created from Epic 3 specification

---

## Status

**Current:** ready-for-dev
**Completion:** pending
**Final:** Awaiting implementation
