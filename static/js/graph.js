$(document).ready(function(){

    var today = new Date();

    $('.input-daterange').datepicker({
        startDate: '05/22/2024',
        endDate: today,
        format: 'mm/dd/yyyy',
        autoclose: true,
        todayHighlight: true
    });
     
    const dataSelector = $('#dataSelector')

    dataSelector.on('change', () => {
        if (dataSelector.val() === 'temperature'){
            $('#temperatureDropdownContainer').show()
        } else {
            $('#temperatureDropdownContainer').hide()
        }
    })
    
    $('#submitBtn').click(function() {
        var startDate = $('#startDate').val();
        var endDate = $('#endDate').val();
        var dataType = $('#dataSelector').val();
        var units = $('#temperatureDropdown').val();
        if (startDate && endDate && dataType != 'none') {

            $('#graph').hide();
            $.ajax({
                type: 'POST',
                url: '/process_dates',
                contentType: 'application/json',
                data: JSON.stringify({ 'start_date': startDate, 'end_date': endDate, 'data_type': dataType, 'units': units, 'station_id': 1 }),
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
            alert('Please make sure to fill in all available fields');
        }
    });
})