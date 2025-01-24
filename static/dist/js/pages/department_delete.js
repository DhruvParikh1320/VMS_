$(document).ready(function() {
    $('#department_table').on('click', '.delete-link', function() {
      var offer_id = $(this).attr('data-id');
      console.log(offer_id);

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
            var deleteUrl = `department/delete/${offer_id}`;
            console.log('deleteUrl',deleteUrl);
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