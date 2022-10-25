#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Tuple

from django.templatetags.static import static
from wildewidgets import VerticalDarkMenu


#------------------------------------------------------
# Menus
#------------------------------------------------------

class MainMenu(VerticalDarkMenu):
    brand_image: str = static("core/images/logo.svg")
    brand_image_width: str = "100%"
    brand_text: str = "Sphinx Hosting"
    items: List[Tuple[str, str]] = [
        ('Home', 'core:home'),
    ]
