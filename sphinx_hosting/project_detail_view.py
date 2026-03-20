from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.urls import reverse
from wildewidgets import Widget, WidgetListLayout

from .forms import ProjectReadonlyUpdateForm
from .project_detail_layout import apply_project_detail_layout_builders
from .views import ProjectDetailView as BaseProjectDetailView
from .wildewidgets import (
    ProjectClassifierListWidget,
    ProjectDetailWidget,
    ProjectInfoWidget,
    ProjectRelatedLinksListWidget,
    ProjectVersionsTableWidget,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    from .models import Project


class ProjectDetailView(BaseProjectDetailView):
    """
    Project detail view with host-project layout customization hooks.

    This subclass preserves the built-in ``ProjectDetailView`` layout while
    allowing host projects to mutate the live ``WidgetListLayout`` through
    ``PROJECT_DETAIL_LAYOUT_BUILDERS``.
    """

    def get_content(self) -> Widget:
        """
        Build the project detail layout and apply host-project extensions.

        Returns:
            The populated project detail ``WidgetListLayout``.

        Side Effects:
            May invoke configured project-detail layout builders that mutate the
            returned layout in place.

        """
        layout = WidgetListLayout(self.object.title)
        layout.add_widget(ProjectInfoWidget(self.object))
        layout.add_widget(
            ProjectDetailWidget(
                self.object, form=ProjectReadonlyUpdateForm(instance=self.object)
            )
        )
        layout.add_widget(
            ProjectRelatedLinksListWidget(queryset=self.object.related_links.all())
        )
        layout.add_widget(
            ProjectClassifierListWidget(queryset=self.object.classifiers.all())
        )
        layout.add_widget(ProjectVersionsTableWidget(project_id=self.object.pk))
        user = cast("AbstractUser", self.request.user)
        version = self.object.latest_version
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
        if user.has_perm("sphinxhostingcore.change_project"):
            layout.add_sidebar_link_button(
                "Edit Project",
                reverse(
                    "sphinx_hosting:project--update", args=[self.object.machine_name]
                ),
                color="azure",
            )
        apply_project_detail_layout_builders(
            request=self.request,
            user=user,
            project=cast("Project", self.object),
            layout=layout,
            view=self,
        )
        return layout
