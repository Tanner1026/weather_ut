$(document).ready(function(){

    var today = new Date();

    
    
      const dataSelector = $('#dataSelector');
    
      dataSelector.on('change', () => {
        if (dataSelector.val() === 'temperature') {
          $('#temperatureDropdownContainer').show();
        } else {
          $('#temperatureDropdownContainer').hide();
        }
      });
    
      const stationID = $('#stationID');
    
      stationID.on('change', () => {
        let startDate
        if (stationID.val() === '1') {
            $('.input-daterange').datepicker('destroy')
            const dateRangePicker = $('.input-daterange').datepicker({
                startDate: '05/22/2024',
                endDate: today,
                format: 'mm/dd/yyyy',
                autoclose: true,
                todayHighlight: true,
              });
              $('#datepicker').show();
              $('#dateLabel').show()
              $('#dataSelector').show()
        } else if(stationID.val() === '2'){
            $('.input-daterange').datepicker('destroy')
            const dateRangePicker = $('.input-daterange').datepicker({
                startDate: '01/17/2025',
                endDate: today,
                format: 'mm/dd/yyyy',
                autoclose: true,
                todayHighlight: true,
              });
              $('#datepicker').show();
              $('#dateLabel').show()
              $('#dataSelector').show()
        } else {
            $('.input-daterange').datepicker('destroy')
            $('#datepicker').hide()
            $('#dateLabel').hide()
            $('#dataSelector').hide()
        }
      });

    
    $('#submitBtn').click(function() {
        var startDate = $('#startDate').val();
        var endDate = $('#endDate').val();
        var dataType = $('#dataSelector').val();
        var units = $('#temperatureDropdown').val();
        var station_id = $('#stationID').val();
        if (startDate && endDate && dataType && station_id != 'none') {
            $('#graph').hide();
            $.ajax({
                type: 'POST',
                url: '/process_dates',
                contentType: 'application/json',
                data: JSON.stringify({ 'start_date': startDate, 'end_date': endDate, 'data_type': dataType, 'units': units, 'station_id': station_id }),
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