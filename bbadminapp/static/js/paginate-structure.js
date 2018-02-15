// initialize closure and pass in jQuery
/*
USE pagination.js

 */


(function($){
    // create jQuery fn(s)
    $.fn.p4g1n8 = function(options){
        // create a local format function
        String.prototype.format = function() {
            var s = this,
                i = arguments.length;

            while (i--) {
                s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
            }

            return s;
        };

        // setup a copy of the settings and merge the options passed in
        var settings = $.extend(true, {}, $.fn.p4g1n8.defaults, options);

        // create any private globals or functions
        var page_padding = settings.page_padding * 2;
        var page_width = settings.page_unit + page_padding;
        var display_window_width = (settings.pages_to_display * page_width) + (settings.pages_to_display * page_padding);

        function set_click_bind(){
           // bind the li links to process the data loading
            $(settings.pagination).on('click', settings.paginate_item, function(){
                // bailout when a disabled button is clicked
                if ($(this).hasClass(settings.page_disabled) || $(this).hasClass(settings.page_active)){return 0;}

                // find sibling with active state and remove active and add enable (if any)
                 $('{0} {1}.{2}'.format(settings.pagination, settings.paginate_item, settings.page_active)).each(function(){
                    $(this).removeClass(settings.page_active).addClass(settings.page_enabled);
                 });

                // setup the left and right page increment controls
                var page_control = $(this).data(settings.page_data);
                if([settings.page_previous_text, settings.page_next_text].indexOf(page_control) > -1){
                    // go to previous page
                    if(page_control == settings.page_previous_text){
                        settings.current_page--;
                    } else {
                        // go to next page
                        settings.current_page++;
                    }

                    settings.load_page = settings.current_page;
                } else {
                    settings.load_page = parseInt(page_control);
                }
                set_pagination_page();
                load_api_data();
            });
        }

        function set_pagination_page(){
            $(settings.paginate_item).each(function(){
                // set the active page
                if ($(this).data(settings.page_data) == settings.load_page){
                    $(this).removeClass(settings.page_enabled).addClass(settings.page_active);
                    settings.current_page = settings.load_page;
                }

                //set previous or next when applicable, default to active
                $('{0}, {1}'.format(settings.page_previous, settings.page_next))
                    .removeClass(settings.page_disabled).addClass(settings.page_enabled);

                // force the pages to stay at min of 1
                // set the previous
                if (settings.current_page <= 1){
                    $(settings.page_previous).removeClass(settings.page_enabled).addClass(settings.page_disabled);
                    settings.current_page = 1;
                }

                // force the pages to stay at max of the last available page
                // set the next
                if (settings.current_page >= settings.last_page) {
                    $(settings.page_next).removeClass(settings.page_enabled).addClass(settings.page_disabled);
                    settings.current_page = settings.last_page;
                }
            });

            //update_display_window();
        }


        function set_display_window(){
            for(var i=1; i <= (settings.last_page - settings.pages_to_display); i+=settings.pages_to_display){
                var temp = [];
                for(var j=i; j<= (i+=settings.pages_to_display); j++){
                    temp.push(j);
                }
                //console.log(temp);
            }
        }

        function update_display_window(){
            if ($.inArray(i, settings.display_window[settings.current_data_set]) > -1){
                $(settings.paginate_item).each(function(){
                    var page_control = $(this).data(settings.page_data);
                    if([settings.page_previous_text, settings.page_next_text].indexOf(page_control) > -1) {
                        $(this).removeClass(settings.page_hidden);
                    }
                });
            } else {
                if([settings.page_previous_text, settings.page_next_text].indexOf(page_control) > -1) {
                    if (!$(this.hasClass('hidden'))) {
                        $(this).addClass(settings.page_hidden);
                    }
                }
            }
        }

        function set_pagination(){
            // clear out children if existing
            $(settings.pagination).empty();

            // insert the previous page btn
            $(settings.pagination).append('<{0} class="{1}" data-page="{2}"><a href="#!"><i class="mdi-navigation-chevron-left"></i></a></{0}>'.format(
                settings.paginate_item,
                settings.page_enabled,
                settings.page_previous_text)
            );


            $(settings.pagination).append('<ul class="pagination pagination-display-window"></ul>');
            $(settings.pagination).children('ul').each(function(){
                //console.log($(this));
                $(this)
                    .css('display', 'inline-block')
                    .css('width', display_window_width)
                    .css('height', settings.page_height + 'px')
                    .css('overflow', 'hidden')
                    .css('position', 'relative')
                    .css('float', 'left')
                    .css('margin', 0);
                // insert the pages
                //for(var i=1; i <= settings.last_page; i++){
                // unit test: 10000 pages
                for(var i=1; i <= 10; i++){
                     $(this)
                        .append('<{0} class="{1}" data-page="{2}"><a href="#!">{2}</a></{0}>'.format(
                        settings.paginate_item,
                        (settings.current_page == i) ? settings.page_active : settings.page_enabled,
                        i));
                }
            });

            // insert the next page btn
            $(settings.pagination).append('<{0} class="{1}" data-page="{2}"><a href="#!"><i class="mdi-navigation-chevron-right"></i></a></{0}>'.format(
                settings.paginate_item,
                settings.page_enabled,
                settings.page_next_text)
            );
        }

        function set_table_data(){
            // loop through each record
            settings.table.find('td').remove();

            for(var i=0; i <= settings.table_data.length - 1; i++){
                // loop through each header
                var tmp = '';
                for(var j=0; j <= settings.table_headers.length - 1; j++){
                    tmp += '<td>{0}</td>'.format(settings.table_data[i][settings.table_headers[j]]);
                }

                // append it to the table
                settings.table.append('<tr>{0}></tr>'.format(tmp));
            }
        }

        function load_api_data(){
            if(!isNaN(settings.load_page)) {
                //update the settings.api.page_filter
                settings.api.page_filter = $.param({page: settings.load_page});
                var api_url = '{0}?{1}'.format(settings.api.url, settings.api.page_filter);
                var api_worker = new Worker('js/workers/load_api_data.js');

                api_worker.onmessage = function (e) {
                    var ret_data = JSON.parse(e.data);

                    settings.table_data = ret_data.data;
                    settings.last_page = ret_data[settings.api_total_pages];
                    settings.total_records = ret_data[settings.api_total_records];
                    settings.current_page = ret_data.page;
                    settings.fetched_data[ret_data.page] = ret_data.data;
                    set_table_data();
                };

                if(settings.load_page in settings.fetched_data){
                    console.log('loading pre-fetched data for:', settings.load_page);
                    settings.table_data = settings.fetched_data[settings.load_page];
                    settings.current_page = settings.load_page;
                    set_table_data();
                } else {
                    console.log('fetching data for:', settings.load_page);
                    api_worker.postMessage(api_url);
                }


            }
        }

        // finally return the object to the caller (as a jQuery object)
        return $(this).each(function(evt){
            // the initial call and create the reset from within the success
            if(evt === 0){
                // setup the table_headers
                settings.table.find('th').each(function(){
                    var th = $(this).data('field');
                    if ($.inArray(th, settings.table_headers) === -1){
                        settings.table_headers.push(th);
                    }
                });

                set_click_bind();
                set_display_window();
                set_pagination();
                set_pagination_page();
                load_api_data();
            }
        });
    };


    // create any extras such as defaults or external/usable functions
    $.fn.p4g1n8.defaults = {
        api: {
            url: '',
            page_filter: 1
        },
        table: null,
        table_data: {},
        table_headers: [],
        previous_display: [],
        current_display:[],
        next_display: [],
        fetched_data: {},
        load_page: 1,
        current_page: 1,
        pages_to_display: 8,
        display_window: [],
        current_data_set: 0,
        pagination: '.pagination',
        paginate_item: 'li',
        page_disabled: 'disabled',
        page_active: 'active',
        page_enabled: 'waves-effect',
        page_hidden: 'hidden',
        page_data: 'page',
        page_previous: '.pagination li[data-page="previous"]',
        page_previous_text: 'previous',
        page_next: '.pagination li[data-page="next"]',
        page_next_text: 'next',
        last_page: null,
        total_records: null,
        api_total_pages: 'total_pages',
        api_total_records: 'recordsTotal',
        page_padding: 5,
        page_unit: 30,
        page_height: 30
    };


})(jQuery);