/*
USE pagination.js

 */

(function($){

    $.fn.paginate = function(options){

        var settings = $.extend(true, {}, $.fn.paginate.defaults, options);

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
        }

        function set_table_data(){
            console.log(settings.table_data);
            console.log(settings.table);
        }


        function load_api_data(){
            if(!isNaN(settings.load_page)){
                //update the settings.api.page_filter
                settings.api.page_filter = $.param({page: settings.load_page});
                var api_url = '{0}?{1}'.format(settings.api.url, settings.api.page_filter);

                $.ajax(api_url).done(function(data){
                    settings.table_data = data;
                    settings.last_page = data[settings.api_total_pages];
                    set_table_data();
                });
            }
        }


        return $(this).each(function(){

            var selector_type = (typeof $(this).attr('class') != 'undefined') ? '.': '#';
            var selector_name = (selector_type === '.') ? $(this).attr('class') : $(this).attr('id');
            var paginate = '{0}{1}'.format(selector_type, selector_name);


            // insert the previous page btn
            $(this).append('<{0} class="{1}" data-page="{2}"><a href="#!"><i class="mdi-navigation-chevron-left"></i></a></{0}>'.format(
                settings.paginate_item,
                settings.page_disabled,
                settings.page_previous_text)
            );

            // set the chunked display window
            // and also setup the pagination
            for(var i=0; i <= (settings.last_page - settings.pages_to_display); i+=settings.pages_to_display){
                var tmp = [];
                for(var j=i; j<(i+settings.pages_to_display); j++){
                    var visibility = ( settings.current_data_set >= j <= j+settings.pages_to_display )  ?
                          settings.page_enabled : '{0} {1}'.format(settings.page_enabled, settings.page_hidden);

                    $(this).append('<{0} class="{1}" data-page="{2}"><a href="#!">{2}</a></{0}>'.format(
                        settings.paginate_item,
                        visibility,
                        j+1));
                    tmp.push(j);
                }
                settings.display_window.push(tmp);
            }

            // insert the next page btn
            $(this).append('<{0} class="{1}" data-page="{2}"><a href="#!"><i class="mdi-navigation-chevron-right"></i></a></{0}>'.format(
                settings.paginate_item,
                settings.page_enabled,
                settings.page_next_text)
            );

            // bind the li links to process the data loading
            $(paginate).on('click', settings.paginate_item, function(){
                // bailout when a disabled button is clicked
                if ($(this).hasClass(settings.page_disabled) || $(this).hasClass(settings.page_active)){return 0;}

                // find sibling with active state and remove active and add enable (if any)
                 $(paginate).each(function(){
                     //noinspection JSValidateTypes
                     $(this).children('{0}.{1}'.format(settings.paginate_item, settings.page_active)).each(function(){
                        $(this).removeClass(settings.page_active).addClass(settings.page_enabled);
                     });
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
            //console.log(this);
            $(this).find('li:nth-child({0})'.format(settings.current_page + 1)).click();
        });
    };

    $.fn.paginate.defaults = {
        api: {
            url: '',
            page_filter: 1
        },
        table: null,
        table_data: {},
        load_page: 1,
        current_page: 1,
        pages_to_display: 8,
        display_window: [],
        current_data_set: 0,
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
        last_page: 10,
        api_total_pages: 'total_pages'
    };
})(jQuery);
