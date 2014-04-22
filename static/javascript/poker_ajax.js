

$(document).ready(function() {

		disp_table();
		//handle_estimates ();

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
		//alert (data);
		//var arr = $.parseJSON(data);
			
        $('#table').html(data['table']);
        $('#buttons').html(data['button']);
        
        // set click listener
        handle_estimates ();
        handle_activation ();
        
	},'json');
}

function handle_estimates ()
{
	
	$("button[name='estimate']").on('click',function(e)
	{
		
		e.preventDefault();
		var submit_value = $(this).val();
		
		// post selection to view
		$.get('/scrumko/poker_estimate/', {'estimate' : submit_value});	
		
		
	});
	
}

function handle_activation ()
{
	
	$("#endround").on('click',function(e)
	{
		
		e.preventDefault();
				
		// post selection to view
		$.get('/scrumko/poker_disactivate/', {});		
		
	});
	
	$("#startround").on('click',function(e)
	{
		
		e.preventDefault();
				
		// post selection to view
		$.get('/scrumko/poker_activate/', {});		
		
	});
	
	$("#useestimate").on('click',function(e)
	{
		alert ('ja');
		e.preventDefault();
				
		// post selection to view
		$.get('/scrumko/poker_uselast/', {});		
		
	});
	
	
	
}
