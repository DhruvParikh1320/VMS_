$(document).ready(function() {
    $('#appointment_table').on('click', '.delete-link', function() {
      var offer_id = $(this).attr('data-id');
      console.log(offer_id);
      const fullUrl = window.location.href;
      console.log('fullUrl:-',fullUrl); // Outputs the full URL of the current page, e.g., "https://example.com/page?query=123"
      const url = new URL(fullUrl);
      const pathSegments = url.pathname.split('/').filter(segment => segment.length > 0);
      const lastSegment = pathSegments[pathSegments.length - 1];
      console.log(lastSegment);
      Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
      }).then((result) => {
        if (result.isConfirmed) {
          let deleteUrl;
            if (lastSegment === 'upcoming_appointment') {
                deleteUrl = `/visitors/appointment/delete/${offer_id}`;
            } else if (fullUrl.includes('/visitors/appointment')) {
                deleteUrl = `/visitors/appointment/delete/${offer_id}`;
            }
            console.log(deleteUrl);

          $.ajax({
            url: deleteUrl,
            type: 'GET',

            success: function(data) {
              console.log(data);
              if (data.status === 1) {
                Swal.fire({
                  icon: 'success',
                  title: 'Deleted!',
                  text: data.message,
                }).then(() => {
                  location.reload(true);
                });
              } else {
                Swal.fire({
                  icon: 'error',
                  title: 'Oops...',
                  text: data.message,
                }).then(() => {
                  location.reload(true);
                });
              }
            },
            error: function(xhr, status, error) {
              console.error('AJAX Error:', status, error);
              Swal.fire({
                icon: 'error',
                title: 'AJAX Error',
                text: 'An error occurred while processing your request.',
              });
            }
          });
        }
      });
    });
  });