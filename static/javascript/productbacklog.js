$(document).ready(function() {

	$('.target').click(function(e) {
		 // get form associated with the button
		var form = $(this)

		var x;
		var r=confirm("Do you really want to delete user story?");
		if (!r)
		  {
		  e.preventDefault();
		  }
	});




	$(function() {
		$( "#dialog" ).dialog({
		  autoOpen: false,
		  show: {
			effect: "fade",
			duration: 1000
		  },
		  hide: {
			effect: "fade",
			duration: 1000
		  },
		  width: 400
		});
	 
		$( ".edit_estimate" ).click(function() {
			$('#storyid').val ($(this).attr('data-story'));
		
			$('#estimation').val ($(this).parents('.story_estimation').find('.est').html());
		
		  $( "#dialog" ).dialog( "open" );
		});
		
		$("#submit").click (function(e) {
			val = $("#estimation").val();
			
			
			
			if(isNaN(parseFloat(val)))
			{
				
				$("#warning").html("Please enter a positive integer.");
				e.preventDefault();
			}
			
			
		});
		
	  });
	  
	  

	$(function() {
		$( "#dialog_note" ).dialog({
		  autoOpen: false,
		  show: {
			effect: "fade",
			duration: 1000
		  },
		  hide: {
			effect: "fade",
			duration: 1000
		  },
		  width: 600
		});
	 
		$( ".edit_note" ).click(function() {
			$('#storyid1').val ($(this).attr('data-story'));
		
			$('#note').val ($(this).parents('.story_container').find('.notes').html());
		
		  $( "#dialog_note" ).dialog( "open" );
		});
	  });
});
