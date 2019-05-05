/*jslint forin: true */

; (function ($) {
    $.fn.extend({
        mention: function (options) {
            this.opts = {
                users: [],
                delimiter: '@',
                sensitive: true,
                queryBy: 'DisplayName',
                typeaheadOpts: {}
            };

            var settings = $.extend({}, this.opts, options),
                _checkDependencies = function () {
                    if (typeof $ == 'undefined') {
                        throw new Error("jQuery is Required");
                    }
                    else {
                        if (typeof $.fn.typeahead == 'undefined') {
                            throw new Error("Typeahead is Required");
                        }
                    }
                    return true;
                },
                _extractCurrentQuery = function (query, caratPos) {
                    var i;
                    for (i = caratPos; i >= 0; i--) {
                        if (query[i] == settings.delimiter) {
                            break;
                        }
                    }
                    return query.substring(i, caratPos);
                },
                _matcher = function () {
                    this.query = this.query.toLowerCase();
                    if (this.query.indexOf(settings.delimiter) > -1) {
                        var delimiter_index = this.query.lastIndexOf(settings.delimiter);
                        var element = document.querySelector('#' + this.$element[0].id);
                        var coordinates = getCaretCoordinates(element, this.query.lastIndexOf(settings.delimiter) + 1);
                        var fontSize = getComputedStyle(element).getPropertyValue('font-size').replace('px', '');
                        this.at_top = coordinates.top + parseInt(fontSize);
                        this.at_left = coordinates.left;
                        var lastQuery = this.query.substring(delimiter_index + 1);
                        if (lastQuery.indexOf(' ') == -1 && lastQuery.length > 0) {
                            this.query = lastQuery;
                        } else {
                            if (lastQuery != '') {
                                return false;
                            }
                            this.query = '';
                        }
                        return true;
                    }
                    return false;
                },
                _updater = function (item) {
                    var data = this.textValue,
                        caratPos = this.$element[0].selectionStart,
                        i;

                    for (i = caratPos; i >= 0; i--) {
                        if (data[i] == settings.delimiter) {
                            break;
                        }
                    }
                    var replace = data.substring(i, caratPos),
                    	textBefore = data.substring(0, i),
                    	textAfter = data.substring(caratPos),
                    	data = textBefore + settings.delimiter + item + textAfter;

                    this.tempQuery = data;
                    return data;
                },
                _sorter = function (items) {
                    if (items.length && settings.sensitive) {
                        var currentUser = _extractCurrentQuery(this.query, this.$element[0].selectionStart).substring(1),
                            i, len = items.length,
                            priorities = {
                                highest: [],
                                high: [],
                                med: [],
                                low: []
                            }, finals = [];
                        if (currentUser.length == 1) {
                            for (i = 0; i < len; i++) {
                                var currentRes = items[i];

                                if ((currentRes.DisplayName[0] == currentUser)) {
                                    priorities.highest.push(currentRes);
                                }
                                else if ((currentRes.DisplayName[0].toLowerCase() == currentUser.toLowerCase())) {
                                    priorities.high.push(currentRes);
                                }
                                else if (currentRes.DisplayName.indexOf(currentUser) != -1) {
                                    priorities.med.push(currentRes);
                                }
                                else {
                                    priorities.low.push(currentRes);
                                }
                            }
                            for (i in priorities) {
                                var j;
                                for (j in priorities[i]) {
                                    finals.push(priorities[i][j]);
                                }
                            }
                            return finals;
                        }
                    }
                    return items;
                },
                _render = function (items) {
                    var that = this;
                    items = $(items).map(function (i, item) {

                        i = $(that.options.item);

                        var _linkHtml = $('<div />');

                        if (item.IconUrl) {
                            _linkHtml.append('<img class="mention_image" src="' + item.IconUrl + '">');
                        }
                        if (item.DisplayName) {
                            _linkHtml.append('<b class="mention_name">' + item.DisplayName + '</b>');
                        }

                        i.find('a').html(that.highlighter(_linkHtml.html()));
                        return i[0];
                    });

                    items.first().addClass('active');
                    this.$menu.html(items);
                    return this;
                };

            $.fn.typeahead.Constructor.prototype.render = _render;

            return this.each(function () {
                var _this = $(this);
                if (_checkDependencies()) {
                    _this.typeahead($.extend({
                        source: settings.users,
                        matcher: _matcher,
                        updater: _updater,
                        sorter: _sorter
                    }, settings.typeaheadOpts));
                }
            });
        }
    });
})(jQuery);

/* =============================================================
 * bootstrap-typeahead.js v2.3.2
 * http://twitter.github.com/bootstrap/javascript.html#typeahead
 * =============================================================
 * Copyright 2012 Twitter, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ============================================================ */


!function ($) {

    "use strict"; // jshint ;_;


    /* TYPEAHEAD PUBLIC CLASS DEFINITION
     * ================================= */

    var Typeahead = function (element, options) {
        this.$element = $(element)
        this.options = $.extend({}, $.fn.typeahead.defaults, options)
        this.matcher = this.options.matcher || this.matcher
        this.sorter = this.options.sorter || this.sorter
        this.highlighter = this.options.highlighter || this.highlighter
        this.updater = this.options.updater || this.updater
        this.source = this.options.source;
        this.search = this.options.search;
        this.under = this.options.under || false;
        this.fixed = this.options.fixed || false;
        this.sort = this.options.sort || false;
        this.input_text = this.options.input_text || false;
        this.url = this.options.url ||  location.protocol + '//mention.cnblogs.com/mention-users';
        this.item_count = this.options.item_count || 10;
        this.textValue;
        this.at_top;
        this.at_left;
        this.$menu = $(this.options.menu)
        this.shown = false
        this.listen()
    }

    Typeahead.prototype = {

        constructor: Typeahead

    , select: function () {
        var separator=' '
        if (this.query == '') {
            separator = ''
        }
        var val = this.$menu.find('.active').text()
        this.$element
          .val(this.updater(val + separator))
          .change()
        return this.hide()
    }

    , updater: function (item) {
        return item
    }

    , show: function () {
        var pos = $.extend({}, this.$element.position(), {
            height: this.$element[0].offsetHeight
        })

        if (this.shown && this.fixed) {
            this.$menu.show()
        }
        else {
            var top, left;
            if (this.under) {
                top = pos.top + this.at_top
                left = pos.left + this.at_left
            }
            else if (this.input_text) {
                top = pos.top + pos.height
                left = pos.left + this.at_left
            }
            else {
                top = pos.top + pos.height
                left = pos.left
            }

            this.$menu
              .insertAfter(this.$element)
              .css({
                  top: top,
                  left: left
              })
              .show()
        }

        this.shown = true
        return this
    }

    , hide: function () {
        this.$menu.hide()
        this.shown = false
        return this
    }

    , lookup: function (event) {
        var that = this

        var items

        this.query = this.$element.val()
        this.textValue = this.query

        if (!this.query || this.query.length < this.options.minLength) {
            return this.shown ? this.hide() : this
        }

        if (this.matcher()) {
            if (this.search) {
                if (this.query == '') {
                    this.$menu.html('<b class="tips">输入要@的人</b>')
                    this.show()
                } else {
                    this.source = this.search(this.query)
                    items = this.source
                    return items ? this.process(items) : this
                }
            }
            else {
                if (this.query == '') {
                    this.$menu.html('<b class="tips">输入要@的人</b>')
                    this.show()
                } else {
                    $.ajax({
                        timeout: 1000, //1s
                        type: "get",
                        dataType: "json",
                        contentType: "application/json; charset=utf-8",
                        url: this.url + '?displayName=' + encodeURIComponent(this.query) + '&itemCount=' + this.item_count,
                        success: function (data) {
                            that.source = data;
                            items = that.source
                            return items ? that.process(items) : this
                        },
                        error: function (xhr) {
                            console.log(xhr)
                        }
                    });
                }
            }
        }
        else if (this.shown) {
            this.hide()
        }
    }

    , process: function (items) {
        var that = this

        if (this.sort) {
            items = this.sorter(items)
        }

        if (!items.length) {
            return this.shown ? this.hide() : this
        }

        return this.render(items.slice(0, this.options.items)).show()
    }

    , matcher: function (item) {
        return ~item.toLowerCase().indexOf(this.query.toLowerCase())
    }

    , sorter: function (items) {
        var beginswith = []
          , caseSensitive = []
          , caseInsensitive = []
          , item

        while (item = items.shift()) {
            if (!item.toLowerCase().indexOf(this.query.toLowerCase())) beginswith.push(item)
            else if (~item.indexOf(this.query)) caseSensitive.push(item)
            else caseInsensitive.push(item)
        }

        return beginswith.concat(caseSensitive, caseInsensitive)
    }

    , highlighter: function (item) {
        var query = this.textValue.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, '\\$&')
        return item.replace(new RegExp('(' + query + ')', 'ig'), function ($1, match) {
            return '<strong>' + match + '</strong>'
        })
    }

    , render: function (items) {
        var that = this

        items = $(items).map(function (i, item) {
            i = $(that.options.item).text(item)
            i.find('a').html(that.highlighter(item))
            return i[0]
        })

        items.first().addClass('active')
        this.$menu.html(items)
        return this
    }

    , next: function (event) {
        var active = this.$menu.find('.active').removeClass('active')
          , next = active.next()

        if (!next.length) {
            next = $(this.$menu.find('li')[0])
        }

        next.addClass('active')
    }

    , prev: function (event) {
        var active = this.$menu.find('.active').removeClass('active')
          , prev = active.prev()

        if (!prev.length) {
            prev = this.$menu.find('li').last()
        }

        prev.addClass('active')
    }

    , listen: function () {
        this.$element
          .on('focus', $.proxy(this.focus, this))
          .on('blur', $.proxy(this.blur, this))
          .on('keypress', $.proxy(this.keypress, this))
          .on('keyup', $.proxy(this.keyup, this))

        if (this.eventSupported('keydown')) {
            this.$element.on('keydown', $.proxy(this.keydown, this))
        }

        this.$menu
          .on('click', 'li', $.proxy(this.click, this))
          .on('mouseenter', 'li', $.proxy(this.mouseenter, this))
          .on('mouseleave', 'li', $.proxy(this.mouseleave, this))
    }

    , eventSupported: function (eventName) {
        var isSupported = eventName in this.$element
        if (!isSupported) {
            this.$element.setAttribute(eventName, 'return;')
            isSupported = typeof this.$element[eventName] === 'function'
        }
        return isSupported
    }

    , move: function (e) {
        if (!this.shown) return

        switch (e.keyCode) {
            case 9: // tab
            case 13: // enter
            case 27: // escape
                e.preventDefault()
                break

            case 38: // up arrow
                e.preventDefault()
                this.prev()
                break

            case 40: // down arrow
                e.preventDefault()
                this.next()
                break
        }

        e.stopPropagation()
    }

    , keydown: function (e) {
        this.suppressKeyPressRepeat = ~$.inArray(e.keyCode, [40, 38, 9, 13, 27])
        this.move(e)
    }

    , keypress: function (e) {
        if (this.suppressKeyPressRepeat) return
        this.move(e)
    }

    , keyup: function (e) {
        switch (e.keyCode) {
            case 40: // down arrow
            case 38: // up arrow
            case 16: // shift
            case 17: // ctrl
            case 18: // alt
                break

            case 9: // tab
            case 13: // enter
                if (!this.shown) return
                this.select()
                break

            case 27: // escape
                if (!this.shown) return
                this.hide()
                break

            default:
                this.lookup()
        }

        e.stopPropagation()
        e.preventDefault()
    }

    , focus: function (e) {
        this.focused = true
    }

    , blur: function (e) {
        this.focused = false
        if (!this.mousedover && this.shown) this.hide()
    }

    , click: function (e) {
        e.stopPropagation()
        e.preventDefault()
        this.select()
        this.$element.focus()
    }

    , mouseenter: function (e) {
        this.mousedover = true
        this.$menu.find('.active').removeClass('active')
        $(e.currentTarget).addClass('active')
    }

    , mouseleave: function (e) {
        this.mousedover = false
        if (!this.focused && this.shown) this.hide()
    }

    }


    /* TYPEAHEAD PLUGIN DEFINITION
     * =========================== */

    var old = $.fn.typeahead

    $.fn.typeahead = function (option) {
        return this.each(function () {
            var $this = $(this)
              , data = $this.data('typeahead')
              , options = typeof option == 'object' && option
            if (!data) $this.data('typeahead', (data = new Typeahead(this, options)))
            if (typeof option == 'string') data[option]()
        })
    }

    $.fn.typeahead.defaults = {
        source: []
    , items: 8
    , menu: '<ul class="typeahead dropdown-menu"></ul>'
    , item: '<li><a href="#"></a></li>'
    , minLength: 1
    }

    $.fn.typeahead.Constructor = Typeahead


    /* TYPEAHEAD NO CONFLICT
     * =================== */

    $.fn.typeahead.noConflict = function () {
        $.fn.typeahead = old
        return this
    }


    /* TYPEAHEAD DATA-API
     * ================== */

    $(document).on('focus.typeahead.data-api', '[data-provide="typeahead"]', function (e) {
        var $this = $(this)
        if ($this.data('typeahead')) return
        $this.typeahead($this.data())
    })

}(window.jQuery);

/* from: https://github.com/component/textarea-caret-position/ */
/* jshint browser: true */

(function () {

    // The properties that we copy into a mirrored div.
    // Note that some browsers, such as Firefox,
    // do not concatenate properties, i.e. padding-top, bottom etc. -> padding,
    // so we have to do every single property specifically.
    var properties = [
      'direction',  // RTL support
      'boxSizing',
      'width',  // on Chrome and IE, exclude the scrollbar, so the mirror div wraps exactly as the textarea does
      'height',
      'overflowX',
      'overflowY',  // copy the scrollbar for IE

      'borderTopWidth',
      'borderRightWidth',
      'borderBottomWidth',
      'borderLeftWidth',
      'borderStyle',

      'paddingTop',
      'paddingRight',
      'paddingBottom',
      'paddingLeft',

      // https://developer.mozilla.org/en-US/docs/Web/CSS/font
      'fontStyle',
      'fontVariant',
      'fontWeight',
      'fontStretch',
      'fontSize',
      'fontSizeAdjust',
      'lineHeight',
      'fontFamily',

      'textAlign',
      'textTransform',
      'textIndent',
      'textDecoration',  // might not make a difference, but better be safe

      'letterSpacing',
      'wordSpacing',

      'tabSize',
      'MozTabSize'

    ];

    var isFirefox = window.mozInnerScreenX != null;

    function getCaretCoordinates(element, position) {
        // mirrored div
        var div = document.createElement('div');
        div.id = 'input-textarea-caret-position-mirror-div';
        document.body.appendChild(div);

        var style = div.style;
        var computed = window.getComputedStyle ? getComputedStyle(element) : element.currentStyle;  // currentStyle for IE < 9

        // default textarea styles
        style.whiteSpace = 'pre-wrap';
        if (element.nodeName !== 'INPUT')
            style.wordWrap = 'break-word';  // only for textarea-s

        // position off-screen
        style.position = 'absolute';  // required to return coordinates properly
        style.visibility = 'hidden';  // not 'display: none' because we want rendering

        // transfer the element's properties to the div
        properties.forEach(function (prop) {
            style[prop] = computed[prop];
        });

        if (isFirefox) {
            // Firefox lies about the overflow property for textareas: https://bugzilla.mozilla.org/show_bug.cgi?id=984275
            if (element.scrollHeight > parseInt(computed.height))
                style.overflowY = 'scroll';
        } else {
            style.overflow = 'hidden';  // for Chrome to not render a scrollbar; IE keeps overflowY = 'scroll'
        }

        div.textContent = element.value.substring(0, position);
        // the second special handling for input type="text" vs textarea: spaces need to be replaced with non-breaking spaces - http://stackoverflow.com/a/13402035/1269037
        if (element.nodeName === 'INPUT')
            div.textContent = div.textContent.replace(/\s/g, "\u00a0");

        var span = document.createElement('span');
        // Wrapping must be replicated *exactly*, including when a long word gets
        // onto the next line, with whitespace at the end of the line before (#7).
        // The  *only* reliable way to do that is to copy the *entire* rest of the
        // textarea's content into the <span> created at the caret position.
        // for inputs, just '.' would be enough, but why bother?
        span.textContent = element.value.substring(position) || '.';  // || because a completely empty faux span doesn't render at all
        div.appendChild(span);

        var coordinates = {
            top: span.offsetTop + parseInt(computed['borderTopWidth']),
            left: span.offsetLeft + parseInt(computed['borderLeftWidth'])
        };

        document.body.removeChild(div);

        return coordinates;
    }

    if (typeof module != "undefined" && typeof module.exports != "undefined") {
        module.exports = getCaretCoordinates;
    } else {
        window.getCaretCoordinates = getCaretCoordinates;
    }

}());