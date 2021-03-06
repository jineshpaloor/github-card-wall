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
        var wall = document.getElementById('card-wall');
        Sortable.create(wall, {
            draggable: '.swim-lane',
            handle: '.swim-lane-title',
            onUpdate: function(evt) {
            }
        });

        var elements = wall.getElementsByClassName('my-list-group')
        for (var i in elements) {
        //[].forEach.call(wall.getElementsByClassName('my-list-group'), function(el){
            if ((' ' + elements[i].className + ' ').indexOf(' my-list-group ') > -1)
            {
                Sortable.create(elements[i], {
                    group: 'wall',
                    animation: 100,
                    sort : false,
                    draggable : '.card',
                    onAdd: function(evt){
                        var element = evt.item;
                        // console.log('label :', $(element).parents('div.my-list-group').attr('id'));
                        var issue_id = element.getAttribute('id');
                        var from_label = element.getAttribute('data-label');
                        var to_label = $(element).parents('div.my-list-group').attr('id');
                        var issue_no = element.getAttribute('data-number');
                        var repo = element.getAttribute('data-repo');
                        console.log("label: ", from_label, to_label, issue_no, repo);
                        if (from_label == to_label){return false}

                        $.getJSON(
                            $SCRIPT_ROOT + '/change_label',
                            {'issue_id' : issue_id, 'from_label': from_label, 'to_label': to_label, 'issue_no': issue_no, 'repo': repo},
                            function(data) {
                                $("#loader_image").addClass("hidden");
                                if(data.success) {
                                    alert("label changed");
                                    if (to_label == "DONE") {
                                        $("#" + data.issue_id).addClass("hidden");
                                    } else {
                                        $("#" + data.issue_id).attr("data-label", to_label);
                                    }
                                }
                                else alert("operation failed. Please reload the page");
                            }
                        );
                    }
                });
            }
        }
    };

    var createIssue = function(){
        $(".create_issue").on('click', function(e) {
            e.preventDefault();
            var that = $(this);
            var issue_form = $('#form_create_issue');
            var label_name = $(this).data('labelname');

            $("#label").val(label_name);
            $('#modal_new_issue').removeClass('hide');
            $("#issue-creation-ok").addClass("hidden");
            $('#modal_new_issue').modal('show').one('click', '#submit', function (e) {
                var url = $(issue_form).attr("action");
                var data = $(issue_form).serialize();
                $.getJSON(
                    $SCRIPT_ROOT + url,
                    data,
                    function(data) {
                        $("#loader_image").addClass("hidden");
                        if(data.success) {
                            console.log("issue created");
                            $(that).parents('div.swim-lane').find('div.my-list-group').append(data.html);
                            $("#issue-creation-ok").removeClass("hidden");
                        }
                        else console.log("operation failed. Please reload the page");
                    }
                );
            });
        });
    };

    var init = function(){
        dragNdrop2();
        createIssue();
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
            }
        });

        var update_label_order = function(project_id, label_dict){
            $.getJSON(
                $SCRIPT_ROOT + '/project/'+project_id+'/update-labels' ,
                label_dict,
                function(data) {
                    $("#loader_image").addClass("hidden");
                    $("#id_message_label p").text(data.message);
                    $("#id_message_label").removeClass("hidden");
                }
            );
        };

        $("#save_label_order").click(function(){
            var label_dict = {};
            $("#label_order_list li").each(
            function(i,v){ 
                var index = i+1;
                var label = $(v).text();
                label_dict[label] = index; 
            });
            var project_id = $("#project_id").val();
            update_label_order(project_id, label_dict);
        });
    };

    return {
        config: config,
        init: init
    };
})();

GithubCardWall.projectModule = (function(){
    // define some configuration settings
    var config = {
        autoInvokeInit: false
    };

    var deleteProject = function(){
        $('button[name="delete_project"]').on('click', function(e){
            var $form=$(this).closest('form');
            console.log("form is ", $form);
            e.preventDefault();
            $('#confirm').removeClass("hide");
            $('#confirm').modal('show').one('click', '#delete', function (e) {
                $form.trigger('submit');
            });
        });
    };

    var init = function(){
        deleteProject();
    };

    return {
        config: config,
        init: init
    };
})();
