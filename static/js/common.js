(function() {

    // $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
    $(".draggable").draggable();
    $(".droppable").droppable({
        drop: function(e, ui) {
            var issue_id = ui.draggable.attr("id");
            var repo = $("#" + issue_id).data("repo");
            var from_label = $("#" + issue_id).parents("td").attr("id");
            var to_label = $(this).attr('id');
            console.log("label: ", from_label, to_label, issue_id, repo);
            if (from_label == to_label){return false}

            // send ajax request to change label
            $.getJSON(
                $SCRIPT_ROOT + '/change_label',
                {'from_label': from_label, 'to_label': to_label, 'issue_id': issue_id, 'repo': repo},
                function(data) {
                    if(data.success) alert("label changed");
                    else alert("operation failed. Please reload the page");
                }
            );
        }
    });


    // dragula([document.querySelector("#issue-98372333"), document.querySelector("#question")]);
    // var drake = dragula({});

    // $(".draggable").on("click", function(e){
        // console.log('clicked');
        // drake.containers.push(this);
    // });
     //dragula([document.querySelector(".draggable")]);
})();
