

$(document).ready(function() {

		
		$("#imgProgress").show();

		disp_table();
		
		window.setInterval(function(){
		  disp_table();
		}, 2000);
		

});




function disp_table()
{
	$.get('/scrumko/poker_table/', {}, function(data){
		//alert (data);
		//var arr = $.parseJSON(data);
			
        $('#table').html(data['table']);
        $('#buttons').html(data['button']);
        $('#storyname').html(data['story_name']);
        $('#storytext').html(data['story_text']);
        $('#storytest').html(data['story_test']);
        
        
			$("#imgProgress").hide()
			
        
        // set click listener
        handle_estimates ();
        handle_activation ();
        
        
       
        
	},'json');
	
	
}

function handle_estimates ()
{
	
	$("button[name='estimate']").on('click',function(e)
	{
		$("#imgProgress").show();
		e.preventDefault();
		var submit_value = $(this).val();
		
		// post selection to view
		$.get('/scrumko/poker_estimate/', {'estimate' : submit_value});	
		
		disp_table();
	});
	
}

function handle_activation ()
{
	
	$("#endround").on('click',function(e)
	{
		$("#imgProgress").show();
		e.preventDefault();
				
		// post selection to view
		$.get('/scrumko/poker_disactivate/', {});		
		
		disp_table();
	});
	
	$("#startround").on('click',function(e)
	{
		$("#imgProgress").show();
		e.preventDefault();
				
		// post selection to view
		$.get('/scrumko/poker_activate/', {});		
		
		disp_table();
	});
	
	/*$("#useestimate").on('click',function(e)
	{
		
		$("#imgProgress").show();
		
		e.preventDefault();
				
		// post selection to view
		$.get('/scrumko/poker_uselast/', {});		
		
		disp_table();
	});*/
	
	
	
}
