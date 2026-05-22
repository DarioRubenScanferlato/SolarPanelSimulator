---
storyKey: 3-11-keyboard-navigation-and-screen-reader-support
storyId: "3.11"
title: Keyboard Navigation & Screen Reader Support
epicId: 3
epicTitle: Quality, Reliability & Security
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 3-11: Keyboard Navigation & Screen Reader Support

## Story

As an accessibility advocate,
I want keyboard navigation with arrow keys and screen reader testing,
So that keyboard-only users and screen reader users can operate the app.

**Requirements Covered:** WCAG 2.1 Level AA Keyboard Navigation, Screen Reader Support

---

## Acceptance Criteria

**Given** I navigate the page using only the Tab key
**When** I press Tab repeatedly
**Then** focus moves through all interactive elements in logical order

**Given** I am focused on a tab button
**When** I press ArrowLeft or ArrowRight
**Then** focus moves to the adjacent tab button

**And** pressing ArrowRight on the last tab moves focus to the first tab (wraps)

**Given** I navigate the page using a screen reader (NVDA, VoiceOver)
**When** I move through the page
**Then** all content is announced correctly: tab buttons announce their name and selected state, form labels are announced with inputs, error messages are announced as alerts, results section updates are announced

**And** focus indicators are always visible (CSS outline or ring, not invisible)

---

## Tasks & Subtasks

- [ ] Implement tab keyboard navigation in tabs.js
  - [ ] Listen for keydown events on tab buttons
  - [ ] When ArrowLeft pressed: move focus to previous tab (wrap to last if at first)
  - [ ] When ArrowRight pressed: move focus to next tab (wrap to first if at last)
  - [ ] When Home pressed: move focus to first tab
  - [ ] When End pressed: move focus to last tab
  - [ ] Update aria-selected when focus/tab changes
  - [ ] Call switchTab() to update visible panel

- [ ] Verify tab order is logical
  - [ ] Tab buttons should be in correct DOM order (Solar, Battery, Cost)
  - [ ] Form inputs should be in logical order (latitude, longitude, panels, area, etc.)
  - [ ] Results section should come after form
  - [ ] Button should be focusable

- [ ] Ensure all interactive elements are keyboard accessible
  - [ ] Button elements: naturally focusable
  - [ ] Input elements: naturally focusable
  - [ ] Tab buttons: verify tabindex not needed (role="tab" provides focus management)
  - [ ] Custom interactive elements: add tabindex="0" if needed

- [ ] Add visible focus indicators with CSS
  - [ ] Add `:focus` or `:focus-visible` styles to all interactive elements
  - [ ] Use outline, border, or background color (not just color change)
  - [ ] Ensure focus indicator has sufficient contrast (4.5:1)
  - [ ] Make focus indicator at least 2px visible
  - [ ] Remove any `outline: none` without replacement style

- [ ] Test Tab key navigation
  - [ ] Press Tab from page load; verify first interactive element focused
  - [ ] Press Tab repeatedly; verify focus moves in logical order
  - [ ] Press Shift+Tab; verify focus moves backward
  - [ ] Verify no elements skipped or out of order
  - [ ] Verify focus visible at each step

- [ ] Test arrow key navigation on tabs
  - [ ] Focus on first tab (Solar)
  - [ ] Press ArrowRight; verify focus moves to Battery tab
  - [ ] Press ArrowRight again; verify focus moves to Cost tab
  - [ ] Press ArrowRight again; verify focus wraps to Solar tab
  - [ ] Press ArrowLeft from Solar; verify focus moves to Cost (wraps backward)
  - [ ] Press Home; verify focus on first tab
  - [ ] Press End; verify focus on last tab

- [ ] Test with screen reader (NVDA on Windows)
  - [ ] Start NVDA
  - [ ] Navigate to page using Tab key
  - [ ] Verify NVDA announces: page title, tab buttons (with "selected" state), form labels, inputs
  - [ ] Click Simulate and verify results announced
  - [ ] Verify error messages announced (aria-live="polite")
  - [ ] Verify all content is accessible (no orphaned text)
  - [ ] Verify no keyboard traps

- [ ] Test with screen reader (VoiceOver on Mac)
  - [ ] Enable VoiceOver (Cmd+F5)
  - [ ] Navigate page with arrow keys and Tab
  - [ ] Verify VoiceOver announces all content correctly
  - [ ] Verify interactive elements have roles announced
  - [ ] Verify form inputs announced with labels
  - [ ] Verify error messages announced

- [ ] Test with screen reader (mobile — VoiceOver on iOS or TalkBack on Android)
  - [ ] Navigate app with swipe gestures
  - [ ] Verify all content reachable
  - [ ] Verify buttons can be activated (double-tap)
  - [ ] Verify form inputs usable with virtual keyboard

- [ ] Verify focus order is logical and matches visual layout
  - [ ] Focus should move top-to-bottom, left-to-right on screen
  - [ ] Verify tabindex not set to positive values (can break natural order)
  - [ ] Use tabindex="0" only if absolutely necessary
  - [ ] Use tabindex="-1" for programmatically managed focus

- [ ] Add keyboard shortcuts documentation (optional)
  - [ ] Document arrow keys for tab navigation
  - [ ] Document Home/End for first/last tab
  - [ ] Add help text or tooltip (optional feature)

- [ ] Test skip links (optional but recommended)
  - [ ] Consider adding "Skip to main content" link
  - [ ] Visible only on focus
  - [ ] Useful for keyboard-only users to bypass navigation

---

## Dev Notes

**Architecture Context:**
Keyboard navigation and screen reader support are essential for WCAG 2.1 Level AA compliance. Key requirements:

1. **Tab order**: Logical flow through interactive elements (Tab key)
2. **Arrow key navigation**: Tabs use arrow keys to switch (custom interaction pattern)
3. **Focus indicators**: Always visible, sufficient contrast
4. **Screen readers**: All content announced correctly, form labels associated, live regions for updates

Implementation strategy:
- Use native HTML elements (button, input) for automatic keyboard support
- Add custom keyboard handling for tabs (ArrowLeft/Right)
- Ensure aria-selected/aria-invalid managed by JavaScript match actual state
- Test with multiple screen readers (NVDA, VoiceOver)

**Key Patterns:**
- Tab button should use role="tab" (not custom div) for native keyboard behavior
- event.preventDefault() on arrow keys to prevent browser scrolling
- Focus management via focus() method when switching tabs
- aria-selected reflects actual selected state
- Focus indicators must be visible (CSS), not removed

**Testing Tools:**
- Keyboard only navigation: disable mouse input in browser dev tools
- NVDA: free screen reader for Windows (https://www.nvaccess.org/)
- VoiceOver: built-in on Mac/iOS (Cmd+F5 or Cmd+Fn+F5)
- TalkBack: built-in on Android (hold power button, tap accessibility)
- axe DevTools: browser extension to check accessibility programmatically

**Dependencies:**
- No new npm dependencies required
- Uses native browser keyboard events and focus management

**Related Stories:**
- Story 3-10 (Semantic HTML & ARIA) — prerequisite (roles, attributes)
- Story 3-12 (Accessibility Audit) — validates keyboard/screen reader support

**Files Modified:**
- `frontend/app/tabs.js` — add ArrowLeft/Right keyboard handling
- `frontend/styles/main.css` (or equivalent) — add focus indicator styles
- `frontend/index.html` — ensure proper semantic structure (from Story 3-10)

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
- frontend/app/tabs.js
- frontend/styles/main.css (or equivalent)

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
