#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Tuple

from django.templatetags.static import static

from academy_theme.wildewidgets import AcademyThemeMainMenu


#------------------------------------------------------
# Menus
#------------------------------------------------------

class MainMenu(AcademyThemeMainMenu):
    brand_image: str = static("core/images/logo3.png")
    brand_text: str = "Sphinx Hosting"
    items: List[Tuple[str, str]] = [
        ('Home', 'core:home'),
    ]
