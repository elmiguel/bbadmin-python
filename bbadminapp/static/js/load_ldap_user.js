(function($){
    $.fn.load_ldap_user = function(options){
        var defaults = {
            url: '',
            primary_validator: '',
            mappings: {}
        };

        var settings = $.extend(true, {}, defaults, options);

        return $(this).each(function(instance){
            $(this).on('click', function(){
                var username = $(settings.primary_validator).val();
                if(username != ''){
                    $.ajax({url: settings.url + username}).done(function(json){
                        var data = JSON.parse(json.data);
                        //console.log(data);
                        for(var i=0; i <= data.length; i++){
                            //console.log(data[i]);
                            for(var key in data[i]){
                                if(data[i].hasOwnProperty(key)){
                                    //console.log(key, data[i][key]);
                                    $(settings.mappings[key]).val(data[i][key]);
                                    $(settings.mappings[key]).focus();
                                    $(settings.mappings[key]).blur();
                                }
                            }
                        }
                    });
                }
            });
        });
    };
})(jQuery);