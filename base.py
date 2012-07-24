""" Module: elements

Provide generic HTML5 tag implementations as subclasses of python's
cElementTree library to be wielded for rendering by Tornado's UIModule.

Mobile, web, and native application views should extend these to create
generic and application-specific components.

Over time and as needed, this module will codify portions of the HTML5
spec. To wit, when front-end code for generating markup seems broadly
applicable to building anything on any platform, it likely belongs here.


All Element subclasses have access to and may override:
    def tag(self)
    def text(self)
    def set_text(self, text)
    def tail(self)
    def set_tail(self, tail)
    def attributes(self)
    def id(self)
    def set_id(self, id)
    def classes(self)
    def set_classes(self, classes)
    def append_class(self, additional_class)
    def append_classes(self, additional_classes)
    def data(self, key)
    def dataset(self)
    def set_data(self, data_key, value)
    def remove_data(self, key)
    def href(self)
    def set_href(self, href)
    def name(self)
    def set_name(self, name)
    def action(self)
    def set_action(self, url)
    def type(self)
    def set_type(self, type)
    def value(self)
    def set_value(self, value)
    def placeholder(self)
    def set_placeholder(self, value)
    def is_autofocus(self)
    def set_autofocus(self, autofocus=True)
    def is_checked(self)
    def set_checked(self, checked=True)
    def children(self)
    def first_child(self)
    def last_child(self)
    def append_child(self, element)
    def append_children(self, elements)


The base class Element also provides static cElementTree wrappers:
    def to_string(element)


The following tags are implemented as Element subclasses:
    div
    span
    ol
    ul
    li
    nav
    a
    h1
    h2
    header
    section
    form
    input
    button
    br
    footer
    table
    tr
    td
    th

The following tags are not implemented because they are hard-coded in
the top-level templates, which are not dynamically generated:
    html
    head
    body
    meta
    link
    script
    hgroup

The following global html5 attributes are currently implemented:
    class
    id
    data-*

    http://www.w3.org/community/webed/wiki/HTML/Attributes/_Global
    http://www.w3schools.com/html5/html5_ref_globalattributes.asp
    http://www.w3schools.com/html5/html5_ref_eventattributes.asp


The following non-global html5 attributes are currently implemented:

    Attribute       Tag[s]
    ----------------------
    href            a
    name            form, input, button
    action          form, input[type="submit"], button
    type            input, button
    value           input, button
    checked         input[type="checkbox"]
    placeholder     input
    autofocus       input, button

TODO: required, pattern

Note: we don't actually check for type of input.

The following attributes are implemented as subclasses because
they change the functionality of their element.
    type

"""

import xml.etree.cElementTree as ET

from constants import HTML_TAG, HTML_ATTRIBUTE, HTML_TYPE, HTML_CONSTANT


class Element(object):

    """ Abstract Element proxy-subclassing xml.etree.cElementTree.Element.

    class xml.etree.cElementTree.Element(tag, attrib={}, **extra)

    http://docs.python.org/library/xml.etree.elementtree.html

    Version 2.7

    Note that this documentation is for ElementTree, but we subclass
    cElementTree for speed. The problem is that cElementTree is not as
    up-to-date, so be wary of anything new or deprecated in v2.7.

    To protect against this uncertainty, we define convenience wrappers
    around most of the cElementTree.Element API in this subclass to
    avoid a widespread and massively obnoxious change in the event that
    we need to swap out this library for another implementation.

    This class defines the Element interface, and provides a reference
    implementation of this interface.

    The element name, attribute names, and attribute values can be either
    bytestrings or Unicode strings. tag is the element name. attrib is an
    optional dictionary, containing element attributes. extra contains
    additional attributes, given as keyword arguments.

    Properties:
    str     tag     element type
    str     text    additional data found between the element's tags
    str     tail    additional data found after the element's end tag
    dict    attrib  the element's attributes

    Methods:
    def clear()

    def get(key, default=None)
    def items()
    def keys()
    def set(key, value)

    def append(subelement)
    def extend(subelements)         <-- New
    def find(match)
    def findall(match)
    def findtext(match, default=None)
    def getchildren()               <-- Deprecated. Use list(elem)
    def getiterator(tag=None)       <-- Deprecated. Use Element.iter().
    def insert(index, element)
    def iter(tag=None)              <-- New
    def iterfind(match)             <-- New
    def itertext()                  <-- New
    def makeelement(tag, attrib)    <-- Use SubElement() factory.
    def remove(subelement)

    Elements also support the following sequence type methods for
    working with subelements: __delitem__(), __getitem__(),
    __setitem__(), __len__().

    Caution: Elements with no subelements will test as False. This
    behavior will change in future versions. Use specific len(elem) or
    elem is None test instead.

    """

    _element = None

    def __init__(self, tag):
        """ Construct an abstract Element. """
        # enforce that the attributes and extra parameters are unused and that
        # attributes are explicitly set. it's not even clear what extra is.
        self._element = ET.Element(tag)


    def element(self):
        """ Return this element. Bitches. """
        return self._element


    def tag(self):
        """ Return this element's tag with <> removed for convenience. """
        return self.element().tag


    def text(self):
        """ Return this element's text. """
        return self.element().text


    def set_text(self, text):
        """ Set this element's text content. """
        self.element().text = text


    def tail(self):
        """ Return this element's tail. """
        return self.element().tail


    def set_tail(self, tail):
        """ Set this element's tail content. """
        self.element().tail = tail


    def attributes(self):
        """ Return this element's attributes as a sequence of (key, value)
        tuples. """
        return self.element().items()


    def _attribute(self, attribute):
        """ Return this element's requested attribute's value.

        If the requested attribute doesn't exist on the element
        then it returns None.

        Note: Only Element should call this method.

        """
        return self.element().get(attribute, None)


    def _boolean_attribute(self, attribute):
        """ Return this element's boolean value.

        If the value = the attribute name then it's true.
        Otherwise, including if it doesn't exist, it's false.

        """
        return attribute == self._attribute(attribute)


    def _set_attribute(self, attribute, value):
        """ Set an attribute with the value for this element.

        Raise InvalidAttributeError if the attribute is not allowed
        for this element or the value is None.

        Note: Only Element should call this method.

        """
        if value is None:
            description = "Cannot set {0} to None.".format(attribute)
            raise InvalidAttributeError([attribute, "None"], description)
        else:
            value = str(value)

        if attribute in HTML_CONSTANT.ATTRIBUTES[self.tag()]:
            self.element().set(attribute, value)
        # special condition for data-* attribute
        elif attribute.find(HTML_ATTRIBUTE.DATA) != -1:
            self.element().set(attribute, value)
        else:
            description = "{0} cannot have attribute {1}.".format(
                    self.tag(),
                    attribute)
            raise InvalidAttributeError([attribute, value], description)


    def _remove_attribute(self, attribute):
        """ Remove this attribute from the element. """
        if self._attribute(attribute) is not None:
            del self.attribtues()[attribute]


    def _set_boolean_attribute(self, attribute, value):
        """ Set a boolean attribute for this element.

        If True then set it to itself. If False then remove it.

        """
        if value:
            self._set_attribute(attribute, attribute)
        else:
            self._remove_attribute(attribute)


    def id(self):
        """ Return this element's id attribute. """
        return self._attribute(HTML_ATTRIBUTE.ID)


    def set_id(self, id):
        """ Set the id attribute for this element. """
        self._set_attribute(HTML_ATTRIBUTE.ID, id)


    def classes(self):
        """ Return this element's classes as a list."""
        classes = self._attribute(HTML_ATTRIBUTE.CLASS)
        if classes is None:
            return []
        else:
            return classes.split()


    def set_classes(self, classes):
        # TODO: add a constant for class delimiter? [ebh: no.]
        """ Set a list of classes for this element. """
        self._set_attribute(HTML_ATTRIBUTE.CLASS, " ".join(classes))


    def append_class(self, additional_class):
        """ Add a class for this element. """
        classes = self.classes()
        classes.append(additional_class)
        self.set_classes(classes)


    def append_classes(self, additional_classes):
        """ Add a list of classes to the current classes list for this i
        element.

        """
        classes = self.classes()
        classes.extend(additional_classes)
        self.set_classes(classes)


    def data(self, data_key):
        """ Return this element's data-KEY attribute.

        Optional:
        data_key         Key of requested data.

        """
        key = "{0}{1}".format(HTML_ATTRIBUTE.DATA, data_key)
        return self._attribute(key)


    def dataset(self):
        """ Return this element's data-* attributes.

        Return:
        dict of {key: value}

        """
        all_attributes = self.attributes()
        dataset = {}

        # put the data-* key/values into the dataset
        for attribute, value in all_attributes:
            data_index = attribute.rfind(HTML_ATTRIBUTE.DATA)
            if data_index != -1:
                dataset[attribute[data_index:]] = value
        return dataset


    def set_data(self, data_key, value):
        """ Set the data-KEY attribute for this element. """
        data_attribute = "{0}{1}".format(HTML_ATTRIBUTE.DATA, data_key)
        self._set_attribute(data_attribute, value)


    def remove_data(self, data_key):
        """ Remove the data-KEY attribute for this element. """
        data_attribute = "{0}{1}".format(HTML_ATTRIBUTE.DATA, data_key)
        self._remove_attribute(data_attribute)


    def href(self):
        """ Return this element's href attribute. """
        return self._attribute(HTML_ATTRIBUTE.HREF)


    def set_href(self, href):
        """ Set the href attribute for this element. """
        self._set_attribute(HTML_ATTRIBUTE.HREF, href)


    def name(self):
        """ Return this element's name attribute. """
        return self._attribute(HTML_ATTRIBUTE.NAME)


    def set_name(self, name):
        """ Set the name attribute for this element.

        The name attribute's value cannot be "".

        """
        if name == "":
            description = "Name cannot be empty."
            raise InvalidAttributeError([name], description)
        else:
            self._set_attribute(HTML_ATTRIBUTE.NAME, name)


    def action(self):
        """ Return this element's action attribute. """
        return self._attribute(HTML_ATTRIBUTE.ACTION)


    def set_action(self, url):
        """ Set the action attribute for this element. """
        self._set_attribute(HTML_ATTRIBUTE.ACTION, url)


    def type(self):
        """ Return this element's type attribute. """
        return self._attribute(HTML_ATTRIBUTE.TYPE)


    def set_type(self, type):
        """ Set the type attribute for this element.

        Check the type against the list of allowed type values.

        """
        if type in HTML_CONSTANT.TYPES:
            self._set_attribute(HTML_ATTRIBUTE.TYPE, type)
        else:
            description = "Type cannot be of value {0}.".format(type)
            raise InvalidAttributeError([type], description)


    def value(self):
        """ Return this element's value attribute. """
        return self._attribute(HTML_ATTRIBUTE.VALUE)


    def set_value(self, value):
        """ Set the value attribute for this element. """
        self._set_attribute(HTML_ATTRIBUTE.VALUE, value)


    def placeholder(self):
        """ Return this element's placeholder attribute. """
        return self._attribute(HTML_ATTRIBUTE.PLACEHOLDER)


    def set_placeholder(self, value):
        """ Set the placeholder attribute for this element. """
        self._set_attribute(HTML_ATTRIBUTE.PLACEHOLDER, value)


    def is_autofocus(self):
        """ Return True if element is set to autofocus.

        Considered True if the element has value "autofocus".

        """
        return self._boolean_attribute(HTML_ATTRIBUTE.AUTOFOCUS)


    def set_autofocus(self, autofocus=True):
        """ Set the boolean autofocus attribute for this element.

        Optional:
        bool    autofocus   if omitted then set as true.

        """
        self._set_boolean_attribute(HTML_ATTRIBUTE.AUTOFOCUS, autofocus)


    def is_checked(self):
        """ Return True if element is set to be checked.

        Considered True if the element has value "checked".

        """
        return self._boolean_attribute(HTML_ATTRIBUTE.CHECKED)


    def set_checked(self, checked=True):
        """ Set the boolean checkbox attribute for this element.

        Optional:
        bool    checked     if omitted then set as true.

        """
        self._set_boolean_attribute(HTML_ATTRIBUTE.CHECKED, checked)


    def children(self):
        """ Return a list of the immediate children for this element. """
        # TODO: elementTree suggests list(element) over element.getchildren(),
        # which is deprecated in v2.7, but iter(), iterfind(), and itertext()
        # are not yet available in cElementTree. update this when they are.
        #return self.element().getchildren()
        return list(self.element())


    def first_child(self):
        """ Return the first immediate child for this element. """
        return self.children()[0]


    def last_child(self):
        """ Return the last immediate child for this element. """
        return self.children()[-1:]


    def append_child(self, element):
        """ Append a child element to this element's direct children.

        Required:
        Element     element     an instance of elements.Element

        """
        self.element().append(element.element())


    def append_children(self, elements):
        """ Append child elements to this element's direct children.

        Required:
        list    element     a list of elements.Elements

        """
        for e in elements:
            self.element().append_child(e)


#   @staticmethod
#   def validate(tags):
#       """ Validate data being used to create a new HTML element. """
#
#       for tag in tags:
#
#           # is this a valid tag that has been implemented?
#           if tag not in HTML_CONSTANT.TAGS:
#               raise InvalidTagError(tag, "HTML tag not implemented.")
#
#           invalid_attributes = []
#           invalid_classes = []
#
#           for attribute, value in tag.attributes():
#
#               # is this a valid attribute that has been implemented?
#               if attribute not in HTML_CONSTANT.ATTRIBUTES[tag]:
#                   invalid_attributes.append(attribute)
#
#               # if this is the class attribute, is its value valid?
#               if attribute == HTML_ATTRIBUTE.CLASS:
#                   class_set = set(tag.classes())
#                   valid_class_set = set(HTML_CONSTANT.CLASSES[tag])
#                   diff_set = class_set.difference(valid_class_set)
#                   # TODO: this should be a dictionary keyed on tag.
#                   invalid_classes.extend(list(diff_set))
#
#           if invalid_attributes is not []:
#               raise InvalidAttributeError(
#                       invalid_attributes,
#                       "HTML attributes not allowed.")
#
#           # TODO: define InvalidClassError and pass it a dictionary.
#           if invalid_attributes is not []:
#               raise InvalidAttributeError(
#                       invalid_classes,
#                       "HTML classes not allowed for this tag.")


    @staticmethod
    def to_string(element_tree):
        """ Convenience wrapper to standardize on utf-8 and html. """
        # TODO: elementree and celementree differ; does method="html" exist?
        #return ET.tostring(element_tree, "utf-8", "html")
        return ET.tostring(element_tree, "utf-8")


class Div(Element):

    """ Div element <div>. """


    def __init__(self):
        """ Construct a <div>. """
        super(Div, self).__init__(HTML_TAG.DIV)


class Span(Element):

    """ Span element <span>. """


    def __init__(self):
        """ Construct a <span>. """
        super(Span, self).__init__(HTML_TAG.SPAN)


class List(Element):

    """ Abstract list element. """


    def __init__(self, tag, items):
        """ Construct an abstract List. """
        super(List, self).__init__(tag)

        # guarantees direct children of subclasses are <li> elements
        self.set_list_items(items)


    def set_list_items(self, items):
        """ Construct and add list items as this list's children. """
        index = 0
        for item in items:
            self.set_list_item(item, index)
            index = index + 1


    def set_list_item(self, item, index):
        """ Construct and add a list item as a child of this list.

        Required:
        ??? item    undefined item that each subclass LI will interpret
        int index   index of item on the list

        """
        self.append_child(LI(item, index))


class OL(List):

    """ Ordered List element <ol>.

    Attribute   Value           Description
    ---------------------------------------
    reversed    reversed        Specifies that the list order should be
                                descending (9,8,7...)
    start       {number}        Specifies the start value of an ordered
                                list
    type        1               Specifies the kind of marker to use in
                A               the list
                a
                I
                i

    """


    def __init__(self, items):
        """ Construct a <ol>. """
        super(OL, self).__init__(HTML_TAG.OL, items)


class UL(List):

    """ Unordered List element <ul>. """

    def __init__(self, items):
        """ Construct a <ul>. """
        super(UL, self).__init__(HTML_TAG.UL, items)


class LI(Element):

    """ List Item element <li>.

    Attribute   Value           Description
    ---------------------------------------
    value       number          Specifies the value of a list item. The
                                following list items will increment from
                                that number (only for <ol> lists)

    Required:
    int     _index              index of this list item.

    """

    _index = -1

    def __init__(self, item, index):
        """ Construct a <li>. """
        super(LI, self).__init__(HTML_TAG.LI)
        self._index = index
        self.set_content(item)


    def set_content(self, item):
        """ Add content to <li>. """
        # TODO: make a generic implementation of <li>
        raise NotImplementedError()


class Nav(Element):

    """ Nav element <nav>.

    <nav> elements should always have a <ul> as a first direct child. It
    may later become necessary to allow for mobility among direct
    direct children, but this seems sufficient for now.

        <nav>
            <ul>
                ...
            </ul>
        </nav>

    Required:
    list    items               list of generic items
    item?   special_item        an 'item' that stands out in the list
                                (E.g., active link, action item)
    int     special_item_index  where to put the special item

    """


    def __init__(self, items, special_item=None, special_item_index=0):
        """ Construct a <nav>. """
        super(Nav, self).__init__(HTML_TAG.NAV)

        if special_item is not None:
            items.insert(special_item_index, special_item)

        self.set_list(items)

        # TODO: is there css we want applied even to this base class?
        #self.append_classes([])


    def set_list(self, items):
        """ Construct and add the list for this <nav>. """
        self.append_child(UL(items))


class A(Element):

    """ Anchor element <a>.

    Attribute   Value           Description
    ---------------------------------------
    href        {URL}           Specifies the URL of the page the link
                                goes to
    hreflang    {language_code} Specifies the language of the linked
                                document
    media       {media_query}   Specifies what media/device the linked
                                document is optimized for
    rel         alternate       Specifies the relationship between the
                                current document and the linked document
                author
                bookmark
                help
                license
                next
                nofollow
                noreferrer
                prefetch
                prev
                search
                tag
    target      _blank          Specifies where to open the linked
                _parent         document
                _self
                _top
                {framename}
    type        {MIME_type}     Specifies the MIME type of the linked
                                document

    Required:
    url         link            Specifies the value for href

    """


    def __init__(self, link):
        """ Construct a <a>. """
        super(A, self).__init__(HTML_TAG.A)

        # TODO: these are hardcoded strings and not constants because once we
        # have a Link class [and an Item interface or some such thing for it
        # to implement] we will just be accessing properties there. this makes
        # it more obvious what to change.
        self.set_href(link["href"])
        self.set_text(link["text"])

        # TODO: is there css we want applied even to this base class?
        #self.append_classes([])


class H1(Element):

    """ Header 1 element <h1>."""


    def __init__(self):
        """ Construct a <h1>. """
        super(H1, self).__init__(HTML_TAG.H1)


class H2(Element):

    """ Header 2 element <h2>."""

    def __init__(self):
        """ Construct a <h2>. """
        super(H2, self).__init__(HTML_TAG.H2)


class Header(Element):

    """ Header element <header>. """

    def __init__(self):
        """ Construct a <header>. """
        super(Header, self).__init__(HTML_TAG.HEADER)


class Footer(Element):

    """ Footer element <header>. """

    def __init__(self):
        """ Construct a <Footer>. """
        super(Footer, self).__init__(HTML_TAG.FOOTER)


class Section(Element):

    """ Section element <section>. """

    def __init__(self):
        """ Construct a <section>. """
        super(Section, self).__init__(HTML_TAG.SECTION)


class BR(Element):

    """ Break element <br>. """

    def __init__(self):
        """ Construct a <br>. """
        super(BR, self).__init__(HTML_TAG.BR)


class Table(Element):

    """ Table element <table>. """

    def __init__(self, rows_list, header_items=None):
        """ Construct a <table>.

        Required:
        list rows_list    list of lists - each list has td items.

        Optional:
        list header_items   list of th items

        """
        super(Table, self).__init__(HTML_TAG.TABLE)
        if header_items is not None:
            self.set_header(header_items)
        self.set_rows(rows_list)


    def set_header(self, header_items):
        """ Add header row with a th for each item. """
        self.append_child(HeaderTR(header_items))


    def set_rows(self, rows_list):
        """ Add rows to table with tr element. """
        for items in rows_list:
            self.set_row(items)


    def set_row(self, items):
        """ Add individual row with tr element.

        Subclass and override to change functionality.

        """
        self.append_child(TR(items))


class TR(Element):

    """ Table Row element <tr> with <td>. """

    def __init__(self, items):
        """ Construct a <tr>. """
        super(TR, self).__init__(HTML_TAG.TR)
        self.set_row(items)


    def set_row(self, items):
        """ Add items to row with td elements.

        Subclass and ovveride to use different TD.

        """
        for item in items:
            self.append_child(TD(item))


class HeaderTR(TR):

    """ Header Table Row element <tr> with <th>. """

    def set_row(self, items):
        """ Subclass TR set_row. Add items to th elements. """
        for item in items:
            self.append_child(TH(item))



class TRElement(Element):

    """ Superclass of TD and TH for common functionality. """

    def __init__(self, tag, item):
        """ Construct either a td or th element with an item. """
        super(TRElement, self).__init__(tag)
        self.set_item(item)


    def set_item(self, item):
        """ Add an element or a string to this Element. """
        # TODO move this to Item class that wraps text node.
        # TODO LI can also have this functionality.
        if isinstance(item, Element):
            self.append_child(item)
        elif isinstance(item, str):
            self.set_text(item)
        else:
            error_msg = "TH.__init__: Item isn't an Element or string."
            raise InvalidTagError(item, error_msg)


class TD(TRElement):

    """ Section element <td>. """

    def __init__(self, item):
        """ Construct a <td>. """
        super(TD, self).__init__(HTML_TAG.TD, item)


class TH(TRElement):

    """ Section element <th>. """

    def __init__(self, item):
        """ Construct a <th>. """
        super(TH, self).__init__(HTML_TAG.TH, item)


class Form(Element):

    """ Form element <form>. """

    def __init__(self, name, xsrf_token, action_url=None):
        """ Construct a <form>.

        Required:
        str     name            unique identifying name of form
        str     xsrf_token      xsrf token to prevent forgery

        Optional:
        str     action_url      Form submits to this url. Can also
                                be identified in the submit button.

        """
        super(Form, self).__init__(HTML_TAG.FORM)
        self.set_name(name)
        if action_url is not None:
            self.set_action(action_url)

        # add xsrf token bit to prevent xsrf
        self.append_child(XSRFHiddenInput(xsrf_token))


class Input(Element):

    """ Input element <input>. """

    def __init__(self, type, name, value=""):
        """ Construct a <input>.

        Required:
        str     type            type of input element
        str     name            unique name to be submitted with form

        Optional:
        str     value           value to be submitted with form

        """
        super(Input, self).__init__(HTML_TAG.INPUT)
        self.set_type(type)
        self.set_name(name)
        self.set_value(value)


class HiddenInput(Input):

    """ Input element of Hidden type <input type="hidden">. """

    def __init__(self, name, value=""):
        """ Construct a <input type="hidden">

        Required:
        str     name            unique name to be submitted with form

        Optional:
        str     value           value to be submitted with form

        """
        super(HiddenInput, self).__init__(HTML_TYPE.HIDDEN, name, value)


class DataInput(HiddenInput):

    """ Input element of Hidden type to store data <input type="hidden">."""

    name = "hidden-data"

    def __init__(self):
        """ Construct a <input type="hidden">. """
        super(DataInput, self).__init__(self.name)


class XSRFHiddenInput(HiddenInput):

    """ Special Input element of Hidden type that contains the xsrf token:
    <input type="hidden" name="_xsrf" value=TOKEN />

    """

    xsrf_key = "_xsrf"

    def __init__(self, xsrf_token):
        """ Construct a <input type="hidden" name="_xsrf" value=TOKEN />

        Required:
        str     xsrf_token      xsrf token to prevent forgery

        """
        super(XSRFHiddenInput, self).__init__(self.xsrf_key, xsrf_token)


class TextInput(Input):

    """ Input element of Text type <input type="text">. """

    def __init__(self, name, value=""):
        """ Construct a <input type="text">.

        Required:
        str     name            unique name to be submitted with form

        Optional:
        str     value           value to be submitted with form

        """
        super(TextInput, self).__init__(HTML_TYPE.TEXT, name, value)


class CheckboxInput(Input):

    """ Input element of Checkbox type <input type="checkbox">. """


    def __init__(self, name, value, checked=False):
        """ Construct a <input type="checkbox">.

        Required:
        str     name            unique name to be submitted with form
        str     value           value to be submitted with form

        Optional:
        bool    checked         determines if checkbox begins checked

        """
        super(CheckboxInput, self).__init__(HTML_TYPE.CHECKBOX, name, value)
        self.set_checked(checked)


class Button(Element):

    """ Button element <button>. """

    def __init__(self, type=None):
        """ Construct a <button>.

        Optional:
        str     type    the button's type

        Button's type can be "submit", "reset", or no value.
        TODO implement "reset"

        """
        super(Button, self).__init__(HTML_TAG.BUTTON)
        if type in HTML_CONSTANT.TYPES:
            self.set_type(type)
        elif type is not None:
            # TODO better way to handle this but didn't want to
            # introduce a bug
            msg = "Type can only be submit right now."
            raise InvalidAttributeError([type], msg)


class SubmitButton(Button):

    """ Button element of type Submit <button type="submit">. """

    def __init__(self, action_url=None):
        """ Construct a <button type="submit">.

        Optional:
        str     action_url      form submits to this url. can also
                                be identified in the form element.

        """
        super(SubmitButton, self).__init__(HTML_TYPE.SUBMIT)
        if action_url is not None:
            self.set_action(action_url)


class ElementError(Exception):

    """ ElementError is a subclass of Exception.

    Provide an exception superclass from which all Element errors
    should inherit.

    Required:
    str     reason      what went wrong?

    """

    def __init__(self, parameters, description):
        """ Construct a generic, not quite abstract ElementError. """
        self.expr = ", ".join([str(p) for p in parameters])
        self.msg = description


class InvalidTagError(ElementError):

    """ InvalidTagError is a subclass of ElementError.

    Provide an exception to be raised when an attempt is made to create
    an element from an invalid html tag.

    """

    def __init__(self, parameter, description):
        """ Construct a InvalidTagError extending ElementError. """
        super(InvalidTagError, self).__init__(
                [parameter],
                description)


class InvalidElementError(ElementError):

    """ InvalidElementError is a subclass of ElementError.

    Provide an exception to be raised when an attempt is made to modify
    an invalid element as though it were valid HTML.

    """

    def __init__(self, parameter, description):
        """ Construct a InvalidElementError extending ElementError. """
        super(InvalidElementError, self).__init__(
                [parameter],
                description)


class InvalidContentError(ElementError):

    """ InvalidContentError is a subclass of ElementError.

    Provide an exception to be raised when an element has both text and
    child HTML content.

    """

    def __init__(self, parameters, description):
        """ Construct a InvalidContentError extending ElementError. """
        super(InvalidContentError, self).__init__(
                parameters,
                description)


class InvalidAttributeError(ElementError):

    """ InvalidAttributeError is a subclass of ElementError.

    Provide an exception to be raised when an element has invalid
    attributes.

    """

    def __init__(self, parameters, description):
        """ Construct a InvalidAttributeError extending ElementError. """
        super(InvalidAttributeError, self).__init__(
                parameters,
                description)
