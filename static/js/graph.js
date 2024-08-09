$(document).ready(function(){

    var today = new Date();

    

    $('#stationID').change(function() {
        var stationID = $(this).val();
        var startDate;

        if (stationID === '1' || stationID === '2') {
            if (stationID === '1') {
                startDate = '05/22/2024'; // Station 1 start date
            } else if (stationID === '2') {
                startDate = '08/07/2024'; // Station 2 start date
            }
            
            $('.input-daterange').datepicker({
                startDate: startDate,
                endDate: today,
                format: 'mm/dd/yyyy',
                autoclose: true,
                todayHighlight: true
            });
            
            $('#datepicker').show();
            $('#dataSelector').show();
            $('#dateLabel').show();
        } else {
            $('#datepicker').hide();
            $('#dataSelector').hide();
            $('#dateLabel').hide();
        }
    });

    $('#dataSelector').change(function() {
        if ($(this).val() === 'temperature') {
            $('#temperatureDropdownContainer').show();
        } else {
            $('#temperatureDropdownContainer').hide();
        }
    });
    
    $('#submitBtn').click(function() {
        var startDate = $('#startDate').val();
        var endDate = $('#endDate').val();
        var dataType = $('#dataSelector').val();
        var units = $('#temperatureDropdown').val();
        var stationID = $('#stationID').val();
        console.log(stationID)
        if (startDate && endDate && dataType) {

            $('#graph').hide();
            $.ajax({
                type: 'POST',
                url: '/process_dates',
                contentType: 'application/json',
                data: JSON.stringify({ 'start_date': startDate, 'end_date': endDate, 'data_type': dataType, 'units': units, 'station_id': stationID }),
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