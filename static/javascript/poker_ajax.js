

$(document).ready(function() {

		disp_table();

});


function disp_table()
{/*
    $.ajax({
        type: "POST",
        url: '/scrumko/poker_table/',
        dataType: 'html',
        success: function(result)
        {
           $('#table').html(result);
        }
    });

    //don't submit the form
    return false;
	*/
	
	$.get('/scrumko/poker_table/', {}, function(data){
         $('#table').html(data);
	});

}
