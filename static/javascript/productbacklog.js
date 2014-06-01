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
			
			
			
			var pattern=/^\d{1,2}(\.\d+)?$/;
			if(!pattern.test(val))
			{
				$("#warning").html("Please enter a positive value less than 1000.");
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
		  $('#storyid1').val ($(this).attr('data-story'));
			var elem = document.getElementById("note");
			//var encoded = $('#note').val ($(this).parents('.story_container').find('.notes').html());
			var div = document.createElement('div');
			div.innerHTML = $(this).parents('.story_container').find('.notes').html();
			console.log(div.innerHTML)			
			var text = div.innerHTML
			console.log(text);
			var decoded = $('#note').html(text).text();
			decoded = replaceAll(decoded, "<br>", "\n");
			if (decoded=='undefined'){
				decoded="";
			}
			console.log(decoded)
			elem.value=decoded;
			
		
			var varTitle = $('<div />').html(text).text();
			$('#note').text(varTitle);
			
		});
	  });
	  		
function replaceAll(txt, replace, with_this) {   
	return txt.replace(new RegExp(replace, 'g'),with_this); 
	}
	  function htmlEntities(str) {
			return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
		}
});
