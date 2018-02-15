/**
 * Created by elmiguel on 6/18/15.
 */
(function($){
    $.fn.paginator = function(options){

        var defaults = {
            api_url: '/api/users',
            params:{page: 1},
            first_page: 1,
            last_page: 100,
            current_page: 1,
            prev_display: [],
            curr_display: [],
            next_display: [],
            pages_to_display: 5,
            fetched_data: {},
            table_data: 1,
            table: 'table.users'
        };

        var settings = $.extend(true, {}, defaults, options);

        function set_pagination(){
            // first clear current pagination
            var $paginators = $('.pagination');
            $paginators.children().each(function(){$(this).remove();});

            update_display();

            $paginators.append('<li data-page="previous" class="waves-effect"><a href="#!"><i class="mdi-navigation-chevron-left"></i></a></li>');

            for (var p=0; p < settings.curr_display.length; p++){
                var li_class = 'waves-effect';

                if (settings.curr_display[p] == settings.current_page){
                    li_class = 'active';
                }
                    $paginators.append('<li data-page="' + settings.curr_display[p] + '" class="' + li_class + '"><a href="#!">' + settings.curr_display[p] + '</a></li>')
            }

            $paginators.append('<li data-page="next" class="waves-effect"><a href="#!"><i class="mdi-navigation-chevron-right"></i></a></li>');
        }


        function update_display(){
            // check the current display
            // if the current display is empty then
            // this is the initial load
            if(
                settings.prev_display.length === 0 &&
                settings.curr_display.length === 0 &&
                settings.next_display.length === 0
            ){
                for (var i=1; i <= settings.pages_to_display; i++){
                    settings.curr_display.push(i);
                }

                for (;i <= settings.last_page; i++){
                    settings.next_display.push(i);
                }
            }

            // need a check if current_page becomes greater than +-one
            // ex: requested page is 16 but the current display is at 8
            // the different is 8. What would be the best way to iterate over
            // that different and handle the page loading at the same time?
            //if (settings.current_page > settings.curr_display.length - 1){
            if (settings.current_page > settings.curr_display[settings.pages_to_display - 1]){
                //copy curr[0] to prev
                settings.prev_display.push(settings.curr_display[0]);
                // remove curr[0]
                settings.curr_display.shift();

                // move the next item over from next
                settings.curr_display.push(settings.next_display[0]);
                //remove the next[0]
                settings.next_display.shift();
            }

            // reverse from above
            if (settings.current_page < settings.curr_display[0]){
                settings.curr_display.unshift(settings.prev_display[settings.prev_display.length - 1]);
                settings.prev_display.pop();
                settings.next_display.unshift(settings.curr_display[settings.curr_display.length - 1]);
                settings.curr_display.pop();
            }

            //console.log(settings.prev_display);
            //console.log(settings.curr_display);
            //console.log(settings.next_display);

        }

        function set_table(){
            var $tables = $(settings.table);
            $tables.each(function(){
                var $table = $(this);
                var $headers = $table.find('thead tr').children();
                var $tbody = $table.find('tbody');

                // clear current table
                $tbody.empty();

                settings.fetched_data[settings.current_page].forEach(function(value){
                    var tmp = '';
                    $headers.each(function(){
                        //console.log(value, index, $(this).data('field'));
                        tmp += '<td>' + value[$(this).data('field')] + '</td>';
                    });
                    $tbody.append('<tr>' + tmp + '</tr>');
                });
            });
        }

        function load_api_data(){
            //console.log(settings.fetched_data);
            if (settings.current_page in settings.fetched_data){
                set_pagination();
                set_table();
            } else {
                // spawn a worker and load the first page
                // based off the settings

                // setup worker,
                var url_filter = $.param({page: settings.current_page});
                var api_url = '{0}?{1}'.format(settings.api_url, url_filter);
                var api_worker = new Worker('js/workers/load_api_data.js');

                api_worker.onmessage = function (e) {
                    var ret_data = JSON.parse(e.data);

                    settings.last_page = ret_data.total_pages;
                    settings.total_records = ret_data.recordsTotal;
                    settings.current_page = ret_data.page;
                    settings.fetched_data[ret_data.page] = ret_data.data;
                    set_pagination();
                    set_table();
                };

                api_worker.postMessage(api_url);
            }

        }


        function bind_click_links(){
            $('.pagination').on('click', 'li', function(){
                var $link = $(this);
                var data_page = $link.data('page');
                if ($link.hasClass('disabled') || $link.hasClass('active')){return 0;}

                // check for prev/next
                if($.inArray(data_page, ['previous','next']) > -1){
                    //console.log('Single page step');
                    if (data_page == 'next'){
                        settings.current_page++;
                    } else {
                        settings.current_page--;
                    }
                } else {
                    // if number proceed to page loading
                    //console.log('Loading single page');
                    settings.current_page = parseInt(data_page);
                }

                if (settings.current_page <= 0){
                    settings.current_page = 1;
                }

                if (settings.current_page >= settings.last_page){
                    settings.current_page = settings.last_page;
                }

                    load_api_data();
            });
        }

        return $(this).each(function(instance){
            // Check for the first instance and do the initializing
            // of the bindings and setup
            // this will ensure that there not be multiple
            // calls to the api or the plugin functions

            if (instance === 0){
                //check if fetched_data has been provided
                //console.log('first instance detected');
                if ($.isEmptyObject(settings.fetched_data)){
                    load_api_data();
                }

            }

            $(this).data('instance', instance);
            bind_click_links();
        });
    };

})(jQuery);