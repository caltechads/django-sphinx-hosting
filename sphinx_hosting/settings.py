from django.conf import settings


MAX_GLOBAL_TOC_TREE_DEPTH: int = int(getattr(settings, 'SH_MAX_GLOBAL_TOC_TREE_DEPTH', 2))
