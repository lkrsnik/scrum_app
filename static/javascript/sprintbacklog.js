$(document).ready(function() {
	//hides all "Task" headers that don't have any tasks under
	var elems = document.getElementsByClassName('backlogtasktable');
	for(i=0;i<elems.length;i++) {
		if(elems[i].getElementsByTagName("tr").length < 2)
			elems[i].style.display = 'none';
	}
	
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
	$('.target2').click(function(e) {
		 // get form associated with the button
		var form = $(this)

		var x;
		var r=confirm("Do you really want to delete task?");
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
			console.log(decoded)
			if (decoded=='undefined'){
				decoded="";
			}
			elem.value=decoded;
			
		
			var varTitle = $('<div />').html(text).text();
			$('#note').text(varTitle);
			
		});
	  });
	  		
function replaceAll(txt, replace, with_this) {   
	return txt.replace(new RegExp(replace, 'g'),with_this); 
	}
	  $(function() {
		 
		$( "#dialogremaining" ).dialog({
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
	
		$( ".edit_remaining" ).click(function() {
			$('#taskid1').val ($(this).attr('data-story'));
		
			$('#duration').val($(this).parents('.column_mytask').find('.dur').html());
		
		  $( "#dialogremaining" ).dialog( "open" );
		});
		
		$("#submit2").click (function(e) {
			val = $("#duration").val();			
			
			var pattern=/^\d+(\.\d+)?$/;
			if(!pattern.test(val))
			{
				document.getElementById("warning").innerHTML="Please enter a positive number!";
				e.preventDefault();
			}
			
			
			
		});
		
	  });
});
