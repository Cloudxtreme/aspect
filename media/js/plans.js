$(function() {
      $("#id_tos").change(function() {
         $.get("/ajax/plans/", function(data) {
            alert(data);
         });
      });
});
