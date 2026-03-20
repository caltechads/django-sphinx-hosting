from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.urls import reverse
from django.utils.translation import gettext as _
from wildewidgets import Widget, WidgetListLayout

from .forms import VersionUploadForm
from .project_detail_layout import apply_project_detail_layout_builders
from .views import ProjectUpdateView as BaseProjectUpdateView
from .wildewidgets import (
    ProjectClassifierSelectorWidget,
    ProjectDetailWidget,
    ProjectInfoWidget,
    ProjectRelatedLinkCreateModalWidget,
    ProjectRelatedLinksWidget,
    ProjectVersionsTableWidget,
    VersionUploadBlock,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    from .models import Project


class ProjectUpdateView(BaseProjectUpdateView):
    """
    Project update view with host-project layout customization hooks.

    This subclass preserves the built-in ``ProjectUpdateView`` layout while
    allowing host projects to mutate the live ``WidgetListLayout`` through
    ``PROJECT_DETAIL_LAYOUT_BUILDERS``.
    """

    def get_content(self) -> Widget:
        """
        Build the project update layout and apply host-project extensions.

        Returns:
            The populated project update ``WidgetListLayout``.

        Side Effects:
            May invoke configured project-detail layout builders that mutate the
            returned layout in place.

        """
        layout = WidgetListLayout(self.object.title)
        layout.add_widget(ProjectInfoWidget(self.object))
        layout.add_widget(ProjectDetailWidget(self.object))
        layout.add_widget(ProjectRelatedLinksWidget(self.object))
        layout.add_widget(ProjectClassifierSelectorWidget(self.object))
        layout.add_widget(ProjectVersionsTableWidget(project_id=self.object.pk))
        layout.add_modal(ProjectRelatedLinkCreateModalWidget(self.object))
        version = self.object.latest_version
        user = cast("AbstractUser", self.request.user)
        if version and version.head:
            layout.add_sidebar_link_button(
                "Read Docs",
                reverse(
                    "sphinx_hosting:sphinxpage--detail",
                    args=[
                        self.object.machine_name,
                        version.version,
                        version.head.relative_path,
                    ],
                ),
                color="orange",
                css_class="mb-3",
            )
        if user.has_perm("sphinxhostingcore.add_version"):
            layout.add_sidebar_bare_widget(
                VersionUploadBlock(form=VersionUploadForm(project=self.object))
            )
        if user.has_perm("sphinxhostingcore.delete_project"):
            layout.add_sidebar_form_button(
                "Delete Project",
                reverse(
                    "sphinx_hosting:project--delete", args=[self.object.machine_name]
                ),
                color="outline-secondary",
                confirm_text=_("Are you sure you want to delete this project?"),
            )
        apply_project_detail_layout_builders(
            request=self.request,
            user=user,
            project=cast("Project", self.object),
            layout=layout,
            view=self,
        )
        return layout
