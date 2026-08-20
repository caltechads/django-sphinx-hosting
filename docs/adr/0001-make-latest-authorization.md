# Make Latest is authorized by change_project or change_version, scoped to the URL Project

Make Latest retargets a Project's Latest Version and rebuilds that Project's search index. We allow the write when the user has `sphinxhostingcore.change_project` **or** `sphinxhostingcore.change_version`, and we reject a Version that does not belong to the Project identified by the URL. Django's `permission_required` list is AND, so the view uses django-braces `MultiplePermissionsRequiredMixin` with `permissions["any"]`; do not collapse this to a list or to `change_project` alone — that would lock out Version Managers or Project Managers. Do not override Django `has_permission` on this view: braces `PermissionRequiredMixin` uses `check_permissions`, so a Django override would be a no-op.

## Status

accepted

## Considered Options

- **`change_project` only** (audit default): matches sibling Project-mutating views, but Version Managers cannot Make Latest even though they own Version CRUD.
- **`change_version` only**: Version Managers can, Project Managers cannot, despite the pointer living on Project.
- **`change_project` OR `change_version`** (chosen): both manager roles can retarget Latest; Editors and Administrators already have both.
- **New custom permission**: precise, but needs a migration, group assignment, and docs for a split we do not have.
- **Honor a Version from another Project**: `save()` today writes `version.project`, so a POST to `/project/alpha/set-latest/` with a beta Version pk mutates beta. Rejected as a confused-deputy write.
- **Point the URL Project at a foreign Version**: would break the Version→Project invariant.

## Consequences

- Reorder mixins to `LoginRequiredMixin`, `MultiplePermissionsRequiredMixin`, …, `BaseFormView`. `BaseFormView.dispatch` does not call `super()`, so access mixins never ran. This is a bugfix, not a second decision.
- Replace the non-existent `sphinxhostingcore.update_project` string. Do not fix mixin order without this, or every editor 403s.
- `VersionMakeLatestForm.clean_version` requires `version.project.machine_name` to equal the URL slug; mismatch is a validation error. Invalid POST redirects to `project--detail` with flashed form errors (not HTTP 400: `BaseFormView` has no `template_name`). Success also redirects to `project--detail`, which Version Managers can GET; `project--update` requires `change_project`.
- Hide "Set This As Latest" unless the user has one of the two permissions (same pattern as Delete Version).
- API `latest_version` stays read-only. No new package; reuse django-braces `MultiplePermissionsRequiredMixin`.
