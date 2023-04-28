*****************************
Authoring your Sphinx project
*****************************

When authoring your Sphinx project that will be imported into
``django-sphinx-hosting``, the most important thing to be careful with is your
global table of contents.

The global table of contents for a documentation set is something that the
author of the Sphinx documents defines with :rst:dir:`toctree` directives.
Sphinx uses those :rst:dir:`toctree` directives to construct the linkages
between pages.  This affects the following things within
``django-sphinx-hosting``:

* The ``Next``, ``Previous`` and ``Parent`` page buttons at the top of each page
* The navigation menu that appears in the main navigation sidebar

How the global table of contents is built
=========================================

There are two methods for building the global table of contents navigation in
the sidebar: use sphinxcontrib_jsonglobaltoc_ to add a ``globaltoc`` key to
every ``.ftjson`` file created when doing ``make json`` from your source files;
have ``django-sphinx-contrib`` build a global table of contents by starting at
the root page and traversing the page tree via the ``next`` key in each
``.ftjson`` file.

The main reason to use sphinxcontrib_jsonglobaltoc_ over the traversal mechanism
is so that the in-page anchors to page sections to show up in your sidebar
navigation, or both.  It also will obey the ``:caption:`` setting in your
:rst:dir:`toctree` directives.

How to make a good global table of contents
===========================================

Our goal here is to make a global table of contents that looks good in the
navigation sidebar of ``django-sphinx-hosting``.

As we said above, it is the source ``.rst`` documents for the documentation set
that determine the global table of contents, not ``django-sphinx-hosting``.
``django-sphinx-hosting`` just interprets what Sphinx gives it, and uses that to
build the main navigation in the sidebar and the the ``Next``, ``Previous`` and
``Parent`` buttons at the top and bottom of each page.

Headings
--------

You **MUST** get the heading levels right throughout your entire set of
documentation if you want your global table of contents to look right.

First, let's review how to do headings in ReStructuredText, because it wil be
really important in a minute.  The Sphinx docs say:

> Normally, there are no heading levels assigned to certain characters as the structure is determined from the succession of headings.

The "is determined by from the succession of headings" is quite important and
unfortunate here.   Sphinx is overly forgiving where it might save a lot of
heartache if it were to be a bit more draconian, and that can easily cause subtle
problems in global table of contents creation.

Here is the Python Style Guide convention:

* Level 1: # under and overline, for parts
* Level 2: * under and overline, for chapters
* Level 3: = underline for sections
* Level 4: - underline for subsections
* Level 5: ^ underline for subsubsections
* Level 6: " underline for paragraphs

.. note::

    Using Markdown with the ``myst_parser`` extension may make headings less
    easy to screw up, since Markdown has formal heading definitions, unlike
    ReStructuredText.

Guidelines:

* **Headings in the root page**: the document heading (the page title)
  on your root page **must be a level 1 heading**.  If you have subsections in
  the root page, **make them level 3 headings or lower**.  If you use level
  2 headings on the root page, you'll compete with your page document headings,
  which should be level 2, and you'll get a mess in your navigation.  If you're
  going to do nested :rst:dir:`toctree` directives (see below), you may want
  subheadings on the root page to be level 4 or below.
* **Headings in all other pages**: pages under the root page must have a level 2
  heading.  In ReStructuredText that is `*` underline and overline.  If you
  don't get the heading levels right, you end up with very odd nesting behavior
  in the resultant global table of contents.

toctree directives
------------------

:rst:dir:`toctree` directives and only those directives determine the page/section
hierarchy shown in the navigtion sidebar.  Filesystem layout of your ``.rst``
documents has no impact on the global table of contents.

* You must put at least one :rst:dir:`toctree` directive in your root page. This
  will form the root of your global table of contents.
* If you are using nested :rst:dir:`toctree` directives on sub-pages, put your directive
  directly under the document heading on those sub-pages.  Do this because, on
  sub-pages, the toctree recalibates the starting heading level for the pages it
  references to be relative to the **nearest preceding heading** for the
  :rst:dir:`toctree`, not from the page heading for the page the directive is on.
* If all you're interested in for your global table of contents are the page titles, be
  sure to add ``:titlesonly:`` to your :rst:dir:`toctree` directive.
* Unless you really want to show the global table of contents within the page contents
  in addition to the navigation sidebar, use the ``:hidden:`` parameter in your
  :rst:dir:`toctree` directives.
* The ``:caption:`` parameter for a :rst:dir:`toctree` directive only produces an
  actual caption if that directive **is on the root page**.  ``:caption:`` parameters
  on sub-pages are ignored.
* You will only see captions in the ``django-sphinx-hosting`` if you used the
  ``sphinxcontrib-jsonglobaltoc`` extension when building your JSON package.

Now on to constructing your document hierarchy and :rst:dir:`toctree` directives.

Examples
========

.. _single directive:

Single one-level toctree directive
----------------------------------

If all you have is that single :rst:dir:`toctree` directive in the root page of
your documentation, then it's pretty difficult to make that not build and render
properly.

Here's an example root page::

    #######
    My Book
    #######

    .. toctree::
    :hidden:

    chapter1
    chapter2
    chapter3

    Introduction
    ============

    Note this is under a level 3 heading, not a level 2.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

And here's ``chapter1.rst``::

    *********
    Chapter 1
    *********

    .. toctree::
       :hidden:

    page1
    page2
    page3

    Section 1
    =========

    Note that our document title is a level 2 heading, and here we are under a level
    3 heading.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Multiple one-level toctree directives
-------------------------------------

You may want multiple :rst:dir:`toctree` directives in your root document so
that you can separate pages into different logical sections at the same level,
each with its own ``:caption:``.

For example, here's ``index.rst``, our root document::

    #######
    My Book
    #######

    .. toctree::
       :hidden:
       :caption: The first things

    chapter1
    chapter2
    chapter3

    .. toctree::
       :hidden:
       :caption: The second things

    chapter4
    chapter5
    chapter6

    Introduction
    ============

    Note this is under a level 3 heading, not a level 2.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


The ``chapter1.rst`` etc. pages should all follow the heading strategy in the
example ``chapter1.rst`` in :ref:`single directive`.

Nested toctree directives
-------------------------

Nested toctrees happen when you have a top level :rst:dir:`toctree` directive in
your root page and also :rst:dir:`toctree` directives in child pages.  You may
want to do this because you have many pages in your set, and the navigation sidebar
is getting too complicated to use as a flat set of links.

It is probably best to not go beyond two levels of :rst:dir:`toctree` directives
to avoid header collisions between document titles and subheadings on a page.

.. warning::

    If you are using the sphinxcontrib_jsonglobaltoc_ extension to build your
    JSON files, you may want to use the ``:titlesonly:`` parameter on your
    :rst:dir:`toctree` directives to avoid mingling document titles with other
    headings at the same level.  Mingling the document titles and subheadings
    makes the navigation.

    It is possible to make the global table of contents be sane without
    ``:titlesonly:`` but you do have to be very careful with your headings on
    all pages.

As an example of nested :rst:dir:`toctree` direcrives here's our root document::

    #######
    My Book
    #######

    .. toctree::
       :hidden:
       :titlesonly:

    chapter1
    chapter2/index
    chapter3

    Introduction
    ------------

    Note this is under a level 4 heading, not a level 2.  We need a level 4 here
    because chapter2/index needs a level 2 heading as a document title, and
    chapter2/section1 needs a level 3 heading as document title.   If we make our
    subheading here be level 3, it will confuse the global table of contents by
    putting "Introduction" and chapter2/section1 at the same level.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Now let's say that ``chapter2/index.rst`` also has a :rst:dir:`toctree` directive::

    *********
    Chapter 2
    *********

    .. toctree::
       :hidden:
       :titlesonly:

    chapter2/section1
    chapter2/section2
    chapter2/section3

    Introduction
    ------------

    Note that our document title is a level 2 heading, and here we are under a
    level 4 heading.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Then this is what ``chapter2/section1.rst`` should look like::

    Chapter 2, Section 1
    ====================

    Introduction
    ------------

    Note that our document title is a level 3 heading, and here we are under a
    level 4 heading.

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


.. _sphinxcontrib_jsonglobaltoc: https://github.com/caltechads/sphinxcontrib-jsonglobaltoc