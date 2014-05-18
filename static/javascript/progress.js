

$(document).ready(function() {
		get_show_graph();
		
		
		

});




function get_show_graph()
{
	$.get('/scrumko/poker_table/', {}, function(data){
		
			
        $('#table').html(data['table']);
        $('#buttons').html(data['button']);
        $('#storyname').html(data['story_name']);
        $('#storytext').html(data['story_text']);
        $('#storytest').html(data['story_test']);
        
        
			
			
        
       
        
        
       
        
	},'json');
	
	
}

