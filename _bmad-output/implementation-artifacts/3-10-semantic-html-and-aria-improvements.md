---
storyKey: 3-10-semantic-html-and-aria-improvements
storyId: "3.10"
title: Semantic HTML & ARIA Improvements
epicId: 3
epicTitle: Quality, Reliability & Security
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 3-10: Semantic HTML & ARIA Improvements

## Story

As an accessibility advocate,
I want semantic HTML and ARIA roles/labels added to the UI,
So that screen readers can announce content correctly.

**Requirements Covered:** WCAG 2.1 Level AA, Accessibility Best Practices

---

## Acceptance Criteria

**Given** I inspect the tab navigation in the HTML
**When** I check the structure
**Then** the nav element has role="tablist"

**And** each tab button has role="tab" and aria-selected="true" (active) or aria-selected="false" (inactive)

**Given** I inspect form inputs
**When** I check each input
**Then** each input has an associated label with matching for attribute

**Given** I inspect the results section
**When** results update after simulate
**Then** the results section has aria-live="polite" for dynamic update announcements

**Given** I inspect chart elements
**When** I check the chart canvas
**Then** the parent div has role="img" and aria-label describing the chart

---

## Tasks & Subtasks

- [ ] Add semantic HTML structure to index.html
  - [ ] Use `<nav>` for tab navigation (not generic `<div>`)
  - [ ] Use `<section>` or `<main>` for main content areas (not generic divs)
  - [ ] Use `<header>`, `<footer>` for page structure
  - [ ] Use `<form>` element for input forms
  - [ ] Use `<fieldset>` and `<legend>` for related form groups (optional but recommended)

- [ ] Add ARIA roles and attributes to tab navigation
  - [ ] Add `role="tablist"` to nav element containing tab buttons
  - [ ] Add `role="tab"` to each tab button
  - [ ] Add `aria-selected="true"` to active tab button
  - [ ] Add `aria-selected="false"` to inactive tab buttons
  - [ ] Add `aria-controls="panel-{tabId}"` to each tab button (links tab to panel)
  - [ ] Add `id="panel-solar"`, `id="panel-battery"`, `id="panel-cost"` to tab panels

- [ ] Add ARIA roles and attributes to form inputs
  - [ ] Verify each input has associated `<label>` with matching `for` attribute
  - [ ] Add `aria-label` to inputs if label text is unclear
  - [ ] Add `aria-required="true"` to required inputs
  - [ ] Add `aria-invalid="true"` when validation error present
  - [ ] Add `aria-describedby="error-{fieldId}"` to link input to error message
  - [ ] Add error message element with id="error-{fieldId}"

- [ ] Add ARIA live regions for dynamic content
  - [ ] Add `aria-live="polite"` to results section
  - [ ] Add `aria-live="polite"` to error message container
  - [ ] Set `aria-atomic="true"` for entire result cards section (announces all on update)
  - [ ] Verify results updates trigger announcements without refresh

- [ ] Add ARIA attributes to chart elements
  - [ ] Add `role="img"` to chart container div
  - [ ] Add `aria-label="Daily energy production chart showing hourly output in kWh"` to daily chart
  - [ ] Add `aria-label="Monthly energy production chart showing kWh per month"` to yearly chart
  - [ ] Add `aria-label` descriptions that summarize chart data (not just "Chart")

- [ ] Update tabs.js to manage ARIA attributes
  - [ ] When switchTab() called, update aria-selected on all tabs
  - [ ] When switchTab() called, verify correct panel ID in aria-controls
  - [ ] Log warnings if tab/panel structure is invalid

- [ ] Update forms.js to add ARIA attributes dynamically
  - [ ] showFieldError() adds aria-invalid="true" and aria-describedby attribute
  - [ ] clearErrors() removes aria-invalid and aria-describedby attributes
  - [ ] Verify all error display respects ARIA attributes

- [ ] Add button and link labels
  - [ ] Add `aria-label` to buttons if text is ambiguous
  - [ ] Simulate button: verify text content is clear ("Simulate")
  - [ ] Tab buttons: verify aria-selected announces state to screen readers
  - [ ] Links (if any): add title or aria-label for context

- [ ] Test with screen reader (manual)
  - [ ] Use NVDA (Windows) or VoiceOver (Mac) to navigate page
  - [ ] Verify tab navigation announces: "Tab, selected" or "Tab, not selected"
  - [ ] Verify form labels announced with inputs
  - [ ] Verify error messages announced as alert (aria-live)
  - [ ] Verify results updates announced when charts update
  - [ ] Verify chart descriptions provided via aria-label

- [ ] Validate HTML structure
  - [ ] Run HTML validator (e.g., W3C validator) on index.html
  - [ ] Fix any semantic HTML issues
  - [ ] Verify no nesting violations (e.g., button inside button)
  - [ ] Verify form inputs properly contained in `<form>`

- [ ] Document ARIA structure in code comments
  - [ ] Add comments to index.html explaining ARIA roles
  - [ ] Document which elements have aria-live regions
  - [ ] Document which inputs have error handling via aria-invalid

---

## Dev Notes

**Architecture Context:**
Semantic HTML + ARIA attributes enable screen readers to announce content correctly:

1. **Semantic HTML**: Use correct elements (`<nav>`, `<form>`, `<main>`, etc.) so screen readers understand page structure
2. **ARIA roles**: Add role="tab", role="tablist", role="img" to identify interactive patterns
3. **ARIA states**: Add aria-selected, aria-invalid to announce current state
4. **ARIA live regions**: Add aria-live="polite" to announce dynamic updates (results, errors)
5. **Labels**: Add `<label>` elements with `for` attributes to associate text with inputs

**Key Patterns:**
- Always use native HTML elements when possible (button, form, nav) — don't use divs with roles
- Use aria-label only when visual text is insufficient
- Use aria-describedby to link inputs to detailed descriptions (e.g., error messages)
- Use aria-live="polite" for non-urgent updates, aria-live="assertive" for urgent (errors)
- Test with real screen readers (NVDA, VoiceOver, JAWS) — automated tools can't catch everything

**ARIA Best Practices:**
- Don't use aria-hidden for visual hiding; use display:none or visibility:hidden
- Don't duplicate labels with aria-label — use aria-label only when text is visual only
- aria-selected, aria-invalid should match actual state (managed by JavaScript)
- aria-live regions should contain the content that changes, not be an empty container

**Dependencies:**
- No new npm dependencies required
- Uses native ARIA support in browsers

**Related Stories:**
- Story 1-1 (Tab Layout) — tabs need ARIA roles
- Story 3-11 (Keyboard Navigation) — works with ARIA attributes
- Story 3-12 (Accessibility Audit) — validates ARIA improvements

**Files Modified:**
- `frontend/index.html` — add semantic HTML and ARIA attributes
- `frontend/app/tabs.js` — manage aria-selected dynamically
- `frontend/app/forms.js` — manage aria-invalid dynamically

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
(none)

**Modified Files:**
- frontend/index.html
- frontend/app/tabs.js
- frontend/app/forms.js

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
