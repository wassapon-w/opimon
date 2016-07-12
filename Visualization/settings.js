$(document).ready(function(){
     var i = 0;

     $("#add_row").click(function(){
          $('#switchName').append('<tr id="addr'+(i)+'"></tr>');
          $('#addr'+i).html("<td>" + (i+1) + "</td><td><input name='id" + i + "' type='text' placeholder='Switch ID' class='form-control input-md'  /> </td><td><input  name='name" + i + "' type='text' placeholder='Name'  class='form-control input-md'></td>");
          i++;
      });

      $("#delete_row").click(function(){
          if(i >= 1) {
              $("#addr"+(i-1)).html('');
              i--;
          }
      });

      $("#upload").click(function(evt) {
          var test = $("#inputJSON").val();
          console.log(test);

          // window.open(test);
      });
});
