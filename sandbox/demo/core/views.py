from typing import Any, Dict, Type

from django.views.generic import TemplateView
from wildewidgets import MenuMixin, BasicMenu

from .wildewidgets import MainMenu


class HomeView(MenuMixin, TemplateView):
    template_name: str = "core/home.html"
    menu_class: Type[BasicMenu] = MainMenu
    menu_item: str = "Home"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        kwargs['mydata'] = 'Here is my data.'
        return super().get_context_data(**kwargs)
