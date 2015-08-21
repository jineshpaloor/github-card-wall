/** this will be our global, top-level namespace */
var GithubCardWall = GithubCardWall || { };

/** some IE related stuff */
GithubCardWall.ie = function() {
    return navigator.userAgent.indexOf('MSIE') != -1;
};

/** this is the skeleton of a module, copy this to start a new module */
GithubCardWall.cardwallModule = (function(){
    // define some configuration settings
    var config = {
        autoInvokeInit: false
    };

    // define the init function
    var dragNdrop1 = function () {
        $(".draggable").draggable();
        $(".droppable").droppable({
           drop: function(e, ui) {
                $("#loader_image").removeClass("hidden");
                var issue_id = ui.draggable.attr("id")
                var issue_no = ui.draggable.attr("data-number");
                var repo = ui.draggable.attr("data-repo");
                var from_label = ui.draggable.attr("data-label");
                var to_label = $(this).attr('id');
                console.log("label: ", from_label, to_label, issue_no, repo);
                if (from_label == to_label){return false}

                // send ajax request to change label
                $.getJSON(
                    $SCRIPT_ROOT + '/change_label',
                    {'issue_id' : issue_id, 'from_label': from_label, 'to_label': to_label, 'issue_no': issue_no, 'repo': repo},
                    function(data) {
                        $("#loader_image").addClass("hidden");
                        if(data.success) {
                            alert("label changed");
                            $("#" + data.issue_id).attr("data-label", to_label);
                        }
                        else alert("operation failed. Please reload the page");
                    }
                );
            }
        });
    };

    /** using Sortable library */
    var dragNdrop2 = function() {
        var elements = document.getElementsByTagName('*'), i;
        for (i in elements) {
            if ((' ' + elements[i].className + ' ').indexOf(' list-group ') > -1)
            // && (element.getAttribute('id').indexOf('card-wall') == -1)
            {
                Sortable.create(elements[i], {
                    group: 'wall',
                    animation: 100,
                    sort : false,
                    onAdd: function(evt){
                        var element = evt.item;
                        var issue_id = element.getAttribute('id');
                        var from_label = element.getAttribute('data-label');
                        var to_label = '';
                        var issue_no = element.getAttribute('data-number');
                        var repo = element.getAttribute('data-repo');
                        //evt.from
                    }
                });
            }
        }
    };

    var init = function(){
        dragNdrop1();
    };
    // return an object (this is available globally)
    return {
        config: config,
        init: init
    };
})();

/** for ordering the labels */
GithubCardWall.labelorderModule = (function(){
    // define some configuration settings
    var config = {
        autoInvokeInit: false
    };

    // define a function
    var init = function() {
        var element = document.getElementById('label_order_list');
        var mylist = Sortable.create(element, {
            sort: true,
            group: "localStorage-persistent",
            animation: 100,
            store: {
                get: function (sortable) {
                    console.log("inside get func");
                    var order = localStorage.getItem(sortable.options.group);
                    return order ? order.split('|') : [];
                },
                set: function (sortable) {
                    console.log("inside set func");
                    var order = sortable.toArray();
                    localStorage.setItem(sortable.options.group, order.join('|'));
                }
            },
            onUpdate: function(evt){
                var label_id = evt.item.getAttribute('id');
                console.log("on update func :: ", label_id, evt.oldIndex, evt.newIndex);
                // label.order = evt.newIndex
                // evt.oldIndex
                // evt.newIndex
            }
        });

        $("#save_label_order").click(function(){
            console.log("inside click function");
            console.log(localStorage);
            //console.log(sortable.toArray());
            console.log(mylist.options.group);



            //var sortable = Sortable.active;

        });
    };

// return an object (this is available globally)
    return {
        config: config,
        init: init
    };
})();


//(function() {
    //$("#loader_image").hide();
    //$(".swim_lane").each(function(i, v){
      // var ul_id = $(v).attr('id');
       //Sortable.create(ul_id, {});
    //});

    //var wall = document.getElementById('card-wall')
    //Sortable.create(wall, {})

//})();


