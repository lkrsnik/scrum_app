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
		$( "#dialog_add_post" ).dialog({
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
	 
		$( ".add_post" ).click(function() {
			$('#storyid1').val ($(this).attr('data-story'));
		
			$('#new_post').val ($(this).parents('.story_container').find('.notes').html());
		
		  $( "#dialog_add_post" ).dialog( "open" );$('#storyid1').val ("Juhuhu");
			var elem = document.getElementById("new_post");
			//var encoded = $('#new_post').val ($(this).parents('.story_container').find('.notes').html());
			var div = document.createElement('div');
			div.innerHTML = $(this).parents('.story_container').find('.notes').html();
			console.log(div.innerHTML);
			
			var text = "";
			var decoded = $('#new_post').html(text).text();
			elem.value=decoded;
		
			var varTitle = $('<div />').html(text).text();
			$('#new_post').text(varTitle);
			
		});
		
		$("#submit").click (function(e) {
			val = $("#new_post").val();

			
			var pattern=/^(?!\s*$).+/;
			if(!pattern.test(val))
			{
				$("#warning").html("Please enter a post text.");
				e.preventDefault();
			}
		
			
			
		});
		
	  });
	  function htmlEntities(str) {
			return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
		}
});
