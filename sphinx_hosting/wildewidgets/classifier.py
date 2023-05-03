from typing import Dict

from django.utils.text import slugify

from wildewidgets import (
    Block,
    CardWidget,
    CollapseWidget,
    CheckboxInputBlock,
    HorizontalLayoutBlock,
    LinkButton,
    NavLinkToggle,
    UnorderedList,
)

from ..models import Classifier, ClassifierNode


class ClassifierFilterForm(Block):
    """
    This is the tree-like classifier filter form that appears to the right of
    the :py:class:`sphinx_hosting.wildewidgets.project.ProjectTable`.  It
    is embedded in :py:class:`ClassifierFilterBlock`.

    It allows the user to select a set of classifiers by which to filter the
    projects listing table.
    """

    SCRIPT = """
$(document).ready(function() {{
    function classifier_filter_check_parents($li, state) {{
        var $siblings = $li.siblings();
        var $parent = $li.parent().closest('li');
        state = state && $siblings.children('label').find('input').prop('checked');
        $parent.children('label').find('input').prop('checked', state);
        if ($parent.parents('li').length) {{
            classifier_filter_check_parents($parent, state);
        }};
    }}
    function classifier_filter_open_sections() {{
        $('{block_id} input[type="checkbox"]:checked').each(function() {{
            var last = null;
            var target = null;
            var parents = $(this).parents().each(function() {{
                if ($(this).hasClass('classifiers__filter__form')) {{
                    target = last.prev();
                    return false;
                }}
                last = $(this);
            }});
            target.attr('aria-expanded', 'true');
            var collapse_id = target.attr('data-bs-target');
            $(collapse_id).addClass('show');
        }});
    }}
    classifier_filter_open_sections();
    $('{block_id} input').change(function () {{
        var $cb = $(this);
        var $li = $cb.closest('li');
        var state = $cb.prop('checked');

        // check all children
        $li.find('input').prop('checked', state);

        // check all parents, as applicable
        if ($li.parents('li').length) {{
            classifier_filter_check_parents($li, state);
        }};
    }});
    $('{block_id} .classifier--submit').on('click', function () {{
        var classifier_ids = [];
        $('{block_id} input[type="checkbox"]:checked').each(function() {{
            classifier_ids.push($(this).val());
        }});
        var table = $('.{table_name}').DataTable();
        table.column({column_number}).search(classifier_ids.join()).draw();
    }});
    $('{block_id} .classifier--clear').on('click', function () {{
        $('{block_id} input[type="checkbox"]:checked').each(function() {{
            $(this).prop('checked', false)
        }});
    }});
}});
"""

    block: str = 'classifiers__filter__form'
    tag: str = 'form'

    def __init__(self, table_name: str, column_number: int, **kwargs):
        self.table_name = table_name
        self.column_number = column_number
        super().__init__(**kwargs)
        self._css_id = self.block
        self.script = self.SCRIPT.format(
            block_id=f'#{self._css_id}',
            column_number=self.column_number,
            table_name=self.table_name
        )
        self._attributes['method'] = 'get'
        self._attributes['name'] = self.block
        self.tree: Dict[str, ClassifierNode] = Classifier.objects.tree()
        for node in self.tree.values():
            name = slugify(node.title)
            target = f'#{name}'
            self.add_block(NavLinkToggle(node.title, collapse_id=target, css_class='my-2'))
            contents = UnorderedList()
            self.add_block(CollapseWidget(contents, css_id=name))
            self.add_subtree(contents, node.items)
        self.add_block(
            HorizontalLayoutBlock(
                LinkButton(name='classifier--submit', text='Filter Projects', color='primary'),
                LinkButton(
                    name='classifier--clear',
                    text='Clear',
                    color='outline-secondary',
                    css_class="mt-2 mt-xl-0"
                ),
                css_class='my-3',
                justify='between',
                flex_size='xl'
            )
        )

    def add_subtree(self, contents: UnorderedList, nodes: Dict[str, ClassifierNode]) -> None:
        """
        Add a subtree of classifier checkboxes.

        Args:
            contents: the ``<ul>`` block to which to add our list of classifier checkboxes
            nodes (_type_): _description_
        """
        for node in nodes.values():
            checkbox = self.get_checkbox(node)
            if node.items:
                container = Block(tag='li')
                container.add_block(checkbox)
                sub_contents = UnorderedList()
                container.add_block(sub_contents)
                contents.add_block(container)
                self.add_subtree(sub_contents, node.items)
            else:
                contents.add_block(checkbox)

    def get_checkbox(self, node: ClassifierNode) -> HorizontalLayoutBlock:
        """
        Build and return the :py:class:`wildewidgets.CheckboxInputBlock` for the
        classifier ``node``.

        Args:
            node: the classifier data

        Returns:
            A configured :py:class:`wildewidgets.CheckboxInputBlock`
        """
        value = node.classifier.id if node.classifier else 'empty'
        return CheckboxInputBlock(
            label_text=node.title,
            bold=False,
            input_name=slugify(node.title),
            value=value
        )


class ClassifierFilterBlock(CardWidget):
    """
    A :py:class:`wildewidgets.CardWidget` that contains the
    :py:class:`ClassifierFilterForm`.  This the right of the
    :py:class:`sphinx_hosting.wildewidgets.project.ProjectTable`.  This widget
    is embedded in
    :py:class:`sphinx_hosting.wildewdigets.project.ProjectTableWidget`

    Args:
        table_name: the name of the dataTables table to control
        column_number: the number of the column in the dataTable that contains
            classifier names
    """

    name: str = 'classifiers__filter'

    card_title: str = 'Filter by classifier'

    def __init__(self, table_name: str, column_number: int, **kwargs):
        self.table_name = table_name
        self.column_number = column_number
        super().__init__(**kwargs)
        self.set_widget(
            ClassifierFilterForm(
                table_name=self.table_name,
                column_number=column_number
            )
        )
