/**
 * Created by mbechtel on 6/16/15.
 */


var storage = {
    test: 'Will I hold?'
};

// pass in an array
// [action [, key [, value]]]
// action = set_key, get_key, get_all
// key = key to modify
// value = value to apply to key

self.onmessage = function(e){
    var d = e.data;
    switch(d.action){
        case 'set_key':
            storage[d.key] = d.value;
            self.postMessage(storage);
            break;
        case 'get_key':
            self.postMessage(storage[d.key]);
            break;
        case 'get_all':
            self.postMessage(storage);
            break;
    }
};