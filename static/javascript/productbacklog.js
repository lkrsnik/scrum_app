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
	  });

});
