(function() {
    //$("#loader_image").hide();
    // $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
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

})();
