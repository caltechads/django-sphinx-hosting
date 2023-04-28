from typing import Dict, List, Optional, Type, cast

from django.db.models import Model
from django.utils import timezone
from django.utils.html import strip_tags
from django.urls import reverse
from haystack.models import SearchResult
from haystack.query import SearchQuerySet
import humanize
from wildewidgets import (
    Block,
    Column,
    CrispyFormWidget,
    FontIcon,
    HorizontalLayoutBlock,
    Link,
    LinkButton,
    PagedModelWidget,
    Row,
    TagBlock
)

from ..forms import GlobalSearchForm
from ..models import Classifier, Project, SphinxPage


class GlobalSearchFormWidget(CrispyFormWidget):
    """
    This widget encapsulates the :py:class:`sphinx_hosting.forms.GlobalSearchForm`.
    """
    name: str = 'global-search'
    css_class: str = 'mb-3'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.form is None:
            self.form = GlobalSearchForm()


class SearchResultBlock(Block):
    """
    This is the block we use for rendering a particular search result on the search
    results page.

    Keyword Args:
        object: the :py:class:`haystack.models.SearchResult` object to render
    """

    block: str = 'search-result'
    max_text_length: int = 200

    class Header(Block):
        name: str = 'search-result__header'

        def __init__(self, result: SearchResult, **kwargs):
            super().__init__(**kwargs)
            self.add_class('mb-3')
            now = timezone.now()
            ago = humanize.naturaldelta(
                now - result.object.version.modified,
                minimum_unit='seconds'
            )
            self.add_block(
                HorizontalLayoutBlock(
                    Block(
                        str(result.object.version),
                        name='search-result__header__subtitle',
                        css_class='fs-6 text-muted font-bold'
                    ),
                    Block(
                        f'{ago} ago',
                        name='search-result__header__ago',
                        css_class='text-muted fs-6 text-uppercase'
                    ),
                    justify='between',
                    align='baseline'
                )
            )
            self.add_block(Block(result.object.title, tag='h3'))

    def __init__(self, object: SearchResult = None, **kwargs):  # pylint: disable=redefined-builtin
        result = cast(SearchResult, object)
        super().__init__(**kwargs)
        self.add_class('shadow')
        self.add_class('border')
        self.add_class('p-4')
        self.add_class('mb-4')
        self.add_block(SearchResultBlock.Header(result))
        page = cast(SphinxPage, result.object)
        text = strip_tags(page.body)
        text = text[:self.max_text_length].rsplit(' ', 1)[0] + '...'
        self.add_block(
            Block(text, name='search-result_snippet', css_class='fs-8 text-muted mb-3')
        )
        self.add_block(
            HorizontalLayoutBlock(
                LinkButton(text='Read', url=page.get_absolute_url()),
                Block(f'Rank: {result.score}', css_class='fs-6 text-muted'),
                justify='between',
                align='baseline'
            )
        )


class SearchResultsHeader(HorizontalLayoutBlock):
    """
    The header for the search results listing (not the page header -- that is
    :py:class:`SearchResultsPageHeader`).

    Args:
        results: the Haystack search queryset containing our search results
    """

    name: str = 'search-results__title'
    justify: str = 'between'

    def __init__(self, results: SearchQuerySet, **kwargs):
        super().__init__(**kwargs)
        self.add_block(
            Block(
                str(f"Search Results: {results.count()}"),
                css_class='fs-6 font-bold mb-3'
            )
        )


class PagedSearchResultsBlock(PagedModelWidget):
    """
    This is a paged listing of :py:class:`SearchResultBlock` entries describing
    our search results.
    """

    model: Type[Model] = SphinxPage
    page_kwarg: str = 'p'
    paginate_by: int = 10
    model_widget: Block = SearchResultBlock

    def __init__(self, results: SearchQuerySet, query: Optional[str], **kwargs):
        if query is not None:
            kwargs['extra_url'] = {'q': query}
        super().__init__(queryset=results, **kwargs)


class FacetBlock(Block):
    """
    This is a base class for blocks that appear to the right of the search
    results listing on the search results page that allows you to refine your
    results by a particular facet that is present in the result set.

    Subclass this to create facet filtering blocks for specific facets.  Any
    facet you want to filter by must be defined on your search index by adding
    ``faceted=True`` to the field definition.

    Args:
        results: the Haystack search queryset containing our search results
        query: the text entered into the search form that got us to this results
            page
    """

    #: The model class which our facet is related to
    model: Type[Model]
    #: The title for our block
    title: str
    #: The name of the facet
    facet: str
    #: The field on :py:attr:`model` that we will filter by
    model_field: str

    def __init__(self, results: SearchQuerySet, query: Optional[str], **kwargs):
        self.query = query
        super().__init__(**kwargs)
        self.add_class('border')
        self.add_class('bg-white')
        facet_qs = results.facet(self.facet)
        stats = facet_qs.facet_counts()
        self.add_block(Block(self.title, tag='h3', css_class='p-3'))
        body = Block(name='list-group', css_class='list-group-flush')
        for identifier, count in stats['fields'][self.facet]:
            kwargs = {self.model_field: identifier}
            instance = self.model.objects.get(**kwargs)
            body.add_block(
                Block(
                    HorizontalLayoutBlock(
                        Link(str(instance), url=instance.get_absolute_url(), css_class='fs-5'),  # type: ignore
                        HorizontalLayoutBlock(
                            TagBlock(count, color='cyan', css_class='me-2'),
                            LinkButton(
                                text='Filter',
                                url=reverse('sphinx_hosting:search') + f"?q={query}&{self.facet}={identifier}",
                                color='outline-secondary',
                                size='sm'
                            ),
                        )
                    ),
                    tag='li',
                    name='list-group-item'
                )
            )
        self.add_block(body)


class SearchResultsClassifiersFacet(FacetBlock):
    """
    A :py:class:`FacetBlock` that allows the user to filter search results by classifier.
    """

    model: Type[Model] = Classifier
    title: str = 'Classifiers'
    facet: str = 'classifiers'
    model_field: str = 'name'


class SearchResultsProjectFacet(FacetBlock):
    """
    A :py:class:`FacetBlock` that allows the user to filter search results by project.
    """

    model: Type[Model] = Project
    title: str = 'Projects'
    facet: str = 'project_id'
    model_field: str = 'pk'


class SearchResultsPageHeader(Block):
    """
    The header for the entire search results page.  This shows the search string
    that got us here, and any active facet filters, allowing the user to remove
    any active filter by clicking the "X" next to the filter name.

    Args:
        query: the text entered into the search form that got us to this results
            page

    Keyword Args:
        facets: the active facet filters.  This will be a dict where the key is the
            facet name, and the value is a list of facet values to filter by.
    """

    block: str = 'search-results__header'
    css_class: str = 'mb-5'

    def __init__(
        self,
        query: Optional[str],
        facets: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ):
        if facets is None:
            facets = {}
        super().__init__(**kwargs)
        self.add_class('mb-4')
        self.add_block(
            Block(
                "Search Results",
                tag='h1',
                name='search-results__header__title',
            )
        )
        self.add_block(
            Block(
                f'Query: "{query}"',
                name='search-results__header__subtitle',
                css_class='text-muted fs-6 text-uppercase'
            )
        )
        if facets:
            buttons = HorizontalLayoutBlock(
                Block('Filters:', tag='h3', css_class='me-3'),
                justify='start',
                align='baseline',
                css_class='mt-3'
            )
            for facet, identifiers in facets.items():
                for identifier in identifiers:
                    if facet == 'project_id':
                        project = Project.objects.get(pk=identifier)
                        label = Block(
                            FontIcon(icon='file-excel-fill'),
                            f'Project: {project.title}'
                        )
                    elif facet == 'classifiers':
                        classifier = Classifier.objects.get(name=identifier)
                        label = Block(
                            FontIcon(icon='file-excel-fill'),
                            f'Classifier: {classifier.name}'
                        )
                    buttons.add_block(
                        LinkButton(
                            text=label,
                            url=reverse('sphinx_hosting:search') + f"?q={query}",
                            color='outline-azure',
                            css_class='me-3'
                        )
                    )
            self.add_block(buttons)


class PagedSearchLayout(Block):
    """
    This is the page layout for the entire search results page.

    Args:
        query: the text entered into the search form that got us to this results
            page


    Keyword Args:
        query: the text entered into the search form that got us to this results
            page
        facets: the active facet filters.  This will be a dict where the key is
            the facet name, and the value is a list of facet values to filter by.
    """

    name: str = 'search-layout'
    modifier: str = 'paged'

    def __init__(
        self,
        results: SearchQuerySet,
        query: Optional[str] = None,
        facets: Optional[Dict[str, List[str]]] = None,
        **kwargs
    ):
        self.query = query
        if facets is None:
            facets = {}
        super().__init__(**kwargs)
        self.add_block(SearchResultsPageHeader(query, facets=facets))
        self.add_block(SearchResultsHeader(results))
        row = Row()
        row.add_column(
            Column(
                PagedSearchResultsBlock(results, query),
                name='middle',
                base_width=8
            )
        )
        row.add_column(
            Column(
                SearchResultsProjectFacet(results, query, css_class='mb-4'),
                SearchResultsClassifiersFacet(results, query),
                name='right',
                base_width=4
            )
        )
        self.add_block(row)
