# Sphinx Hosting

A Django app that hosts Sphinx documentation sets as versioned projects for reading, search, and editorial management.

## Language

**Project**:
A named documentation set (an application, library, etc.) that owns Versions.
_Avoid_: package, docs site, repository

**Version**:
One published snapshot of a Project's Sphinx output. Versions own pages, images, and documents.
_Avoid_: release, build, tag (unless you mean the Version's version string)

**Latest Version**:
The Version currently designated as a Project's published pointer. "Read Docs" and the search index follow this pointer. It is not necessarily the newest upload or the highest semver; import may set it, and Make Latest may retarget it.
_Avoid_: current version, newest version, default version

**Make Latest**:
The write that retargets a Project's Latest Version to another Version of that same Project.
_Avoid_: update project, set current, promote (ambiguous with publishing)

**Viewer**:
A user in none of the Django auth groups. They can search and read documentation, and cannot create, modify, or delete anything.
_Avoid_: anonymous (anonymous is unauthenticated; a Viewer may be logged in)

**Project Permission Group**:
A named membership list that restricts *viewing* of a Project to its users. It is not a Django auth Group and does not grant write permissions.
_Avoid_: permission group, auth group, Editors (those are Django `auth.Group` roles)

**Page Body**:
The HTML fragment stored on a Sphinx page after import from the Sphinx JSON builder. The hosting app renders it; Sphinx theme assets are not part of it.
_Avoid_: imported HTML, Sphinx HTML site, full page HTML

**Mermaid source**:
Page Body content the host turns into a diagram: nodes with class `mermaid` only.
_Avoid_: mermaid image (a Sphinx-built SVG/PNG stored as a page image); mermaid-language code fences (those stay code)
