/**
 * Created by mbechtel on 6/15/15.
 */

var load_api_data = function(api_url){

    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200){
           self.postMessage(xmlhttp.responseText);
           self.close();
        }
    };

    xmlhttp.open("GET", api_url, true);
    xmlhttp.send();
};

self.onmessage = function(e){
    load_api_data(e.data);
};
