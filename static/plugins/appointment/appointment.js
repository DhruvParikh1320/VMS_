
$(document).ready(function() {
    // CSRF setup for AJAX
    var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
    console.log("CSRF Token: ", csrfToken);

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });

    // Define the AJAX URL, make sure the URL is correctly rendered
    var ajaxUrl = "{% url 'appointment_page_ajax' %}";
    console.log("AJAX URL: ", ajaxUrl);

    // Initialize DataTable with server-side processing
    $('#user').DataTable({
        "ajax": {
            "url": ajaxUrl,
            "type": "POST",
            "data": function(d) {
                d.csrfmiddlewaretoken = csrfToken; // Include CSRF token in the data payload
            }
        },
        "columns": [
            { data: 'id' },
        ],
        processing: true,
        serverSide: true,
        responsive: true,
        ordering: false,
        lengthMenu: [
            [10, 25, 50, 100],
            [10, 25, 50, 100]
        ],
        layout: {
            topStart: {
                buttons: ['csv', 'print', 'pageLength']
            }
        },
    });

    // Initialize Morris.js line chart
    new Morris.Line({
        element: 'mygraph',
        data: [
            { year: '2008', value: 20 },
            { year: '2009', value: 10 },
            { year: '2010', value: 5 },
            { year: '2011', value: 5 },
            { year: '2012', value: 20 }
        ],
        xkey: 'year',
        ykeys: ['value'],
        labels: ['Value']
    });
});
