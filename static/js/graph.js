$(document).ready(function(){

    var today = new Date();

    $('.input-daterange').datepicker({
        format: 'mm/dd/yyyy',
        startDate: '05/22/2024',
        endDate: today,
        autoclose: true,
        todayHighlight: true
    });

    $('#submitBtn').click(function() {
        var startDate = $('#startDate').val();
        var endDate = $('#endDate').val();
        var dataType = $('#dataselector').val();

        if (startDate && endDate && dataType) {

            $('#graph').hide();
            $.ajax({
                type: 'POST',
                url: '/process_dates',
                contentType: 'application/json',
                data: JSON.stringify({ 'start_date': startDate, 'end_date': endDate, 'data_type': dataType }),
                success: function(response) {
                    var newSrc = '/static/img/data_graph/graph.png?' + new Date().getTime();
                    $('#graph').attr('src', newSrc);
                    $('#graph').show();
                },
                error: function(error) {
                    console.error('Error:', error);
                }
            });
        } else {
            alert('Please select both a start and end date as well as a data type.');
        }
    });
    
})