$('#sync_ldap_user').on('click', function(){
    $('.modal').modal({
        dismissible: true, // Modal can be dismissed by clicking outside of the modal
        opacity: .5, // Opacity of modal background
        inDuration: 300, // Transition in duration
        outDuration: 200, // Transition out duration
        startingTop: '4%', // Starting top style attribute
        endingTop: '10%', // Ending top style attribute
      }
    );

    var user_data = {
        pid: $('#pid').val(),
        username: $('#username').val(),
        firstname: $('#firstname').val(),
        lastname: $('#lastname').val(),
        email: $('#email').val(),
        institution_role: $('#institution_role').val(),
        system_role: $('#system_role').val(),
        data_source_key: "ADMINTOOL",
        showTracking: $('#alert-success').is(':checked'),
        workday: $('#enroll-org-workday').is(':checked'),
        bb_essentials: $('#enroll-course-bb-essentials').is(':checked'),
        tech_training: $('#enroll-org-tech-training').is(':checked'),
        prac_gc: $('#create-course-bb-grade-center').is(':checked'),
        training: $('#create-course-bb-training').is(':checked')
    };
    console.log(user_data);

    if (user_data.pid != '' && user_data.username != '' && user_data.firstname != '' && user_data.lastname != '' && user_data.email != ''){
        if (user_data.institution_role == '') user_data.institution_role = 'FACULTY';
        if (user_data.system_role == '') user_data.system_role = 'None';

        //set the fields for prosperity
        $('#institution_role').val(user_data.institution_role);
        $('#system_role').val(user_data.system_role);
        //console.log(JSON.stringify(user_data));

        $.ajax({
            type: 'POST',
            url: '/bb/user',
            data: JSON.stringify(user_data),
            contentType: "application/json; charset=utf-8",
            dataType: 'json'})
            .done(function(data){

                console.log(data);
                if(user_data.showTracking){
                    $('#success')
                        .find('.modal-content p')
                        .html('User Sync: ' + data.person +
                        '<br>' +
                        'Enrollments: <br>' + data.enrollments.join('<br>') +
                        '<br>' +
                        'Shells: <br>' + data.shells.join('<br>'));
                    $('#success').modal('open');
                    // var html = '<span>User Sync: ' + data.person +
                    // '<br>' +
                    // 'Enrollments: <br>' + data.enrollments.join('<br>') +
                    // '<br>' +
                    // 'Shells: <br>' + data.shells.join('<br>' +
                    // '</span>');
                    // var $toastContent = $(html).add($('<button class="btn-flat toast-action">SUCCESS</button>'));
                    // Materialize.toast($toastContent, 10000);
                }
            })
            .fail(function(e){
                $('#error')
                    .find('.modal-content p')
                    .html('There was an error in sending this request!<br><br>'+ e.message);
                    $('#success').modal('open');
                    
            });
    } else {
        $('#error')
            .find('.modal-content p')
            .html('One or more of the required fields is empty: PID, Username, First Name, Last Name, Email.');
            $('#success').modal('open');
    }
});
