from typing import Dict, List, Optional, Type

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
    name: str = 'global-search'
    css_class: str = 'mb-3'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.form is None:
            self.form = GlobalSearchForm()


class SearchResultBlock(Block):

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

    def __init__(self, obj: SearchResult, **kwargs):
        super().__init__(**kwargs)
        self.add_class('shadow')
        self.add_class('border')
        self.add_class('p-4')
        self.add_class('mb-4')
        self.add_block(SearchResultBlock.Header(obj))
        text = strip_tags(obj.object.body)
        text = text[:self.max_text_length].rsplit(' ', 1)[0] + '...'
        self.add_block(
            Block(text, name='search-result_snippet', css_class='fs-8 text-muted mb-3')
        )
        self.add_block(
            HorizontalLayoutBlock(
                LinkButton(text='Read', url=obj.object.get_absolute_url()),
                Block(f'Rank: {obj.score}', css_class='fs-6 text-muted'),
                justify='between',
                align='baseline'
            )
        )


class SearchResultsHeader(HorizontalLayoutBlock):

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
    This is a block that
    """

    model: Type[Model] = SphinxPage
    page_kwarg: str = 'p'
    paginate_by: int = 10

    def __init__(self, results: SearchQuerySet, query: Optional[str], **kwargs):
        if query is not None:
            kwargs['extra_url'] = {'q': query}
        super().__init__(queryset=results, **kwargs)

    def get_model_widget(self, instance: SearchResult, **kwargs) -> Block:  # pylint: disable=arguments-renamed
        return SearchResultBlock(instance)


class FacetBlock(Block):

    model: Type[Model]
    title: str
    facet: str
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

    model: Type[Model] = Classifier
    title: str = 'Classifiers'
    facet: str = 'classifiers'
    model_field: str = 'name'


class SearchResultsProjectFacet(FacetBlock):

    model: Type[Model] = Project
    title: str = 'Projects'
    facet: str = 'project_id'
    model_field: str = 'pk'


class SearchResultsPageHeader(Block):

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
