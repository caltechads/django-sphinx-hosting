---
title: Make Latest authorization - Plan
type: fix
date: 2026-08-19
origin: docs/adr/0001-make-latest-authorization.md
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-plan-bootstrap
execution: code
---

# Make Latest authorization - Plan

## Goal Capsule

- Objective: Close the unauthenticated Make Latest write. Enforce the ADR: `change_project` or `change_version`, Version belongs to the URL Project, hide the button unless permitted.
- Authority: `docs/adr/0001-make-latest-authorization.md` and `CONTEXT.md` win on product behavior. This plan's KTDs win on mechanism. Sibling views in `sphinx_hosting/views.py` win on mixin and invalid-form patterns.
- Stop: Access mixins run. Bogus `update_project` is gone. Foreign Version pk does not write. Viewers do not see the button. Tests below pass. Do not add an API write, a custom permission, or object-level ACL.
- Execution: Test-first on the POST contract and the button. Mock Haystack at `SphinxPageIndex` so default `sandbox` tests run without the `integration` mark.
- Tail: `ce-work` or equivalent. Gauntlet after the code lands.

Product Contract preservation: bootstrap from the ADR. No prior unified plan. Meaning unchanged; mechanism corrected for django-braces (see KTD1).

## Product Contract

### Summary

Make Latest retargets a Project's Latest Version. Anyone with project-change or version-change permission may do it, only for a Version of the Project in the URL. Viewers never get a working POST and do not see the control.

### Problem Frame

`VersionMakeLatestView` lists `BaseFormView` first. `View.dispatch` never calls access mixins. `permission_required` names `sphinxhostingcore.update_project`, which Django does not generate. `VersionMakeLatestForm.save` writes `version.project.latest_version` from an unchecked pk, so a POST to project alpha with a beta Version pk mutates beta and rewrites Haystack. CSRF still applies for browsers. The intended permission model does not.

### Requirements

**Authorization**

- R1. Anonymous POST to Make Latest does not write. Same login redirect as sibling braces `LoginRequiredMixin` views.
- R2. Authenticated user without `sphinxhostingcore.change_project` and without `sphinxhostingcore.change_version` does not write. per KD1.
- R3. Authenticated user with only `change_project`, or only `change_version`, can Make Latest for a Version of the URL Project. per KD1.

**Scoping**

- R4. POST whose Version pk belongs to another Project does not write either Project. Validation error. Redirect with error messages, not a 200 template redisplay. per KD2. Mechanism: KTD3.

**UI**

- R5. Version detail shows "Set This As Latest" only when the user has `change_project` or `change_version`, the Version has a head page, and it is not already Latest. per KD3.

### Key Decisions

- KD1. Authorize Make Latest with `change_project` **or** `change_version`. Governs R2, R3. (session-settled: user-directed — chosen over change_project-only, change_version-only, and a custom permission: both manager roles keep the action.)
- KD2. Version pk must belong to the URL Project or the write is refused. Governs R4. (session-settled: user-directed — chosen over following the Version's Project or pointing the URL Project at a foreign Version: stops the confused-deputy write.)
- KD3. Hide "Set This As Latest" unless the user has one of those two permissions. Governs R5. (session-settled: user-directed — chosen over always showing the button or deferring UI: same pattern as Delete Version.)

### Actors

- A1. Anonymous: not logged in.
- A2. Viewer: logged in, neither write permission.
- A3. Project Manager analogue: `change_project` only.
- A4. Version Manager analogue: `change_version` only.
- A5. Editor analogue: both permissions.

### Key Flows

- F1. Make Latest POST. Trigger: POST `sphinx_hosting:project--set-latest` with hidden `version` pk. Actors A1–A5. Outcome: write + Haystack reindex only when R3 holds and the Version belongs to the URL Project.
- F2. Version detail GET. Trigger: open a non-latest Version that has a head. Outcome: button present iff R5.

### Acceptance Examples

- AE1. Covers R1 / F1. Given anonymous client, when POST a valid Version pk for project slug `alpha`, then no `Project.latest_version` change and response is a login redirect.
- AE2. Covers R2 / F1. Given Viewer, when same POST, then no write and permission denied (braces default for authenticated-without-perm).
- AE3. Covers R3 / F1. Given A3 or A4, when POST own Project's Version pk, then that Project's Latest Version is that Version.
- AE4. Covers R4 / F1. Given A3, when POST to `/project/alpha/set-latest/` with a Version pk from project `beta`, then neither Project's Latest Version changes.
- AE5. Covers R5 / F2. Given Viewer GET of a non-latest Version with head, then HTML has no "Set This As Latest". Given A3 or A4, then it does.

### Success Criteria

Anonymous and Viewer cannot retarget Latest. Project-only and Version-only permission holders can, only inside the URL Project. The button matches that rule.

### Scope Boundaries

- In: `VersionMakeLatestView`, `VersionMakeLatestForm`, Version detail button, tests, one sentence in `doc/source/overview/authorization.rst`, ADR mechanism note for braces.
- Deferred for later: `VersionUploadView` missing `form_invalid_message` (same latent braces gap). API write of Latest Version. Custom `set_latest_version` permission. django-guardian / per-Project write ACL. Full mixin-order audit of other views.
- Outside this product's identity: object-level write permissions. `ProjectPermissionGroup` is view restriction only.

### Sources

- Origin: `docs/adr/0001-make-latest-authorization.md`, `CONTEXT.md`.
- Patterns: `VersionUploadView` mixin order. `ProjectCreateView.form_invalid` redirect. `VersionDeleteView` queryset scoped to `project_slug`. Delete button `has_perm` gate in `VersionDetailView`.
- django-braces already imported in `sphinx_hosting/views.py`. PyPI `django-braces` 1.15+ (project pin `>=1.15.0`). `MultiplePermissionsRequiredMixin` `permissions["any"]` is OR.
- Django docs: access mixin leftmost; Django `permission_required` list is AND. This repo does not use Django's mixin on these views.
- Package advisor: reuse installed braces. No new dependency. Object-level package was a false trail.

## Planning Contract

### Key Technical Decisions

- KTD1. Use braces `MultiplePermissionsRequiredMixin` with `permissions = {"any": ("sphinxhostingcore.change_project", "sphinxhostingcore.change_version")}`. Instantiates KD1 / R2 / R3. (session-settled: user-directed — chosen over change_project-only, change_version-only, and a custom permission: both manager roles must Make Latest without a new codename.) Conflict: the ADR said override Django `has_permission`. These views import braces `PermissionRequiredMixin`, which has `check_permissions` and no `has_permission`. A Django override would be a no-op. Do not switch the rest of the app to Django mixins in this change.
- KTD2. Pass the URL slug into `VersionMakeLatestForm` via `get_form_kwargs`. `clean_version` requires `version.project.machine_name` equal to that slug. Missing Version and wrong Project both raise `ValidationError`. Instantiates KD2 / R4.
- KTD3. Invalid POST redirects to `project--update` for that slug and flashes form errors, matching `ProjectCreateView.form_invalid`. Conflict: grill/ADR said HTTP 400. `BaseFormView` has no `template_name`. `FormMixin.form_invalid` would `AttributeError` after mixins are fixed. Reject-don't-write is the product rule; status code follows the existing POST-only form pattern.
- KTD4. Tests mock `sphinx_hosting.forms.SphinxPageIndex` (or the form's index collaborator) on successful save. Default `sandbox` `make test` runs `-m 'not integration'`. Do not mark these tests `integration`.

### Assumptions

- Braces authenticated-without-permission behavior matches sibling write views. Tests assert that status, not a hardcoded 403 vs login-redirect guess.
- Django test client does not enforce CSRF. Production CSRF stays as-is.
- `authorization.rst` gets one sentence that Project Managers and Version Managers can Make Latest. No new Sphinx page.

### Sequencing

U1 form scoping, then U2 view auth plus POST tests (needs form kwargs), then U3 button plus GET tests.

## Implementation Units

### U1. Scope Version pk to the URL Project

- Goal: Form refuses a Version that is missing or belongs to another Project.
- Requirements: R4. KTD2.
- Dependencies: none
- Files: Modify `sphinx_hosting/forms.py` (`VersionMakeLatestForm`). Test `sandbox/tests/test_version_make_latest.py` (form cases).
- Approach:
  1. Accept project machine name (or Project) in the form constructor.
  2. In `clean_version`, load Version by pk and require `project.machine_name` matches.
  3. Keep `save()` writing `version.project` only after clean passed, so URL Project and Version Project are the same object.
- Patterns to follow: `VersionDeleteView.get_queryset` filters by `project__machine_name`.
- Execution note: Form tests first. No search backend.
- Test scenarios:
  - Happy: Version of project `alpha` cleans to that pk when slug is `alpha`.
  - Error: Unknown pk raises ValidationError. No `save`.
  - Error: Version of `beta` with slug `alpha` raises ValidationError. `save` not called.
- Verification: Form tests fail before the slug check exists and pass after. `save` is not reached on mismatch.

### U2. Run access mixins and OR permissions on Make Latest

- Goal: Mixins run. OR of the two permissions. Invalid POST does not 500.
- Requirements: R1, R2, R3. KTD1, KTD3.
- Dependencies: U1
- Files: Modify `sphinx_hosting/views.py` (`VersionMakeLatestView`). Patch `docs/adr/0001-make-latest-authorization.md`. One sentence in `doc/source/overview/authorization.rst`. Test `sandbox/tests/test_version_make_latest.py` (POST cases). Follow `sandbox/tests/test_project_detail_customization_integration.py` for `create_user` + `user_permissions.add` + `client.force_login`.
- Approach:
  1. MRO: `LoginRequiredMixin`, `MultiplePermissionsRequiredMixin`, message mixins, `BaseFormView`.
  2. Set braces `permissions["any"]` per KTD1. Remove `update_project`.
  3. `get_form_kwargs` supplies the URL `slug` to the form.
  4. Override `form_invalid` like `ProjectCreateView`: messages + redirect to `project--update`.
  5. Fix `get_form_valid_message` copy (it currently says "Uploaded version").
  6. ADR: name braces `any`, and say invalid POST redirects rather than HTTP 400.
  7. One sentence in `doc/source/overview/authorization.rst` that Project Managers and Version Managers can Make Latest.
- Patterns to follow: `VersionUploadView` mixin order. `ProjectCreateView.form_invalid`.
- Execution note: Failing POST tests first, then mixin/permission/form_invalid wiring. Mock `SphinxPageIndex` on success paths (KTD4). No `integration` mark.
- Test scenarios:
  - Covers AE1. Anonymous POST. No write. Login redirect.
  - Covers AE2. Viewer POST. No write. Denied (assert sibling braces status, not a guessed 403).
  - Covers AE3. `change_project` only, own Version. Write. Index mock called.
  - Covers AE3. `change_version` only, own Version. Write.
  - Covers AE4. `change_project` user POSTs beta Version pk to alpha URL. Neither Latest Version changes. Redirect with errors, not a write.
- Verification: `LoginRequiredMixin` precedes `BaseFormView` in MRO. `update_project` is gone. ADR names braces `any` and redirect-on-invalid. Default `sandbox` `make test` runs AE1–AE4.

### U3. Hide Set This As Latest unless permitted

- Goal: Button matches R5.
- Requirements: R5. KD3.
- Dependencies: none (permission strings from KTD1)
- Files: Modify `sphinx_hosting/views.py` (`VersionDetailView.get_content`). Test `sandbox/tests/test_version_make_latest.py` (GET button cases).
- Approach: Same shape as the Delete Version `has_perm` block. Require `change_project` or `change_version` before `add_sidebar_form_button` for Make Latest. Keep the existing head / not-already-latest guards.
- Patterns to follow: Delete Version button in the same method.
- Test scenarios:
  - Covers AE5. Viewer GET of a non-latest Version with head: HTML has no "Set This As Latest".
  - Covers AE5. `change_project` or `change_version` user GET: button present when not Latest, absent when it already is.
- Verification: Viewer HTML lacks the label. Permitted user HTML has it when the Version is not Latest.

## Verification Contract

| Gate | When | Command / outcome |
|---|---|---|
| Demo pytest | always | From `sandbox`, `rtk make test`. New file must run under default `-m 'not integration'`. AE1–AE5 pass. |
| Ruff | Python edits | `rtk .venv/bin/ruff` on touched library and test files. Zero new issues. |
| Mypy | Library Python | `rtk .venv/bin/mypy` on touched `sphinx_hosting` files. |
| Napoleon | Library Python | `rtk make napoleon-gate`. No new violations vs baseline. |
| Gauntlet | after implementation, user-requested | Tier 3 (auth). Run then. Not a planning deliverable. |

## Definition of Done

- Global: R1–R5 hold in tests. Mixins run. `update_project` gone. Foreign pk does not write. Button hidden for Viewer. Quality gates above green. Abandoned spikes deleted.
- U1: mismatch pk cannot `save`.
- U2: MRO and braces `any` in place. Invalid POST redirects. ADR braces note written. AE1–AE4 tests run in default `make test`.
- U3: button gated. AE5 tests run in default `make test`.

## System-Wide Impact

This is an auth-boundary fix on one POST and one button. Haystack still reindexes only after a permitted in-project `save`. API `latest_version` stays read-only. Django auth Groups from `sphinx_hosting/migrations/0010_add_groups.py` already grant the two permissions to the right roles; no migration.

## Risks & Dependencies

- Mixin order is load-bearing. `BaseFormView` leftmost leaves `View.dispatch` in charge. Access mixins stay dead.
- Fixing MRO while leaving `update_project` 403s every editor.
- After MRO fix, `FormInvalidMessageMixin` still calls `FormMixin.form_invalid` unless `form_invalid` is overridden. No template → `AttributeError` on bad POST. KTD3 is required, not optional polish.
- `save` talks to Haystack. Unmocked success tests will fail or skip in the default suite. KTD4.
- django-braces `LoginRequiredMixin` and Django's are different classes. Do not import Django's mixin for this view while siblings use braces.
